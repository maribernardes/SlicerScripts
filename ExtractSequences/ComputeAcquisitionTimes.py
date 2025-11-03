# -*- coding: utf-8 -*-
"""
ComputeAcquisitionTimes.py

Given a folder containing NRRD frames and a tags.json file that maps each NRRD
filename to DICOM tags (including AcquisitionTime), compute empirical timing stats:
- Mean/SD per-scan duration (between consecutive frames)
- Mean/SD per-cycle duration for 2 consecutive scans (according to an order like ('COR','SAG'))
- Totals: number of scans and cycles used

Assumptions:
- tags.json contains a dict keyed by NRRD filename (basename) with at least
  {"AcquisitionTime": "HHMMSS.frac"} and, optionally, plane info.
- Plane is derived from filename if possible (must contain 'COR' or 'SAG' substrings).
- Frames are filtered to a study substring and a magnitude index range [m_start, m_end],
  but the script is resilient and will process whatever matches.
- Cycle duration is computed as t[i+2] - t[i] for frames aligned to the given planes order,
  i.e., two consecutive scans in the specified order form a complete cycle.
  
Call example: 
python3 ComputeAcquisitionTimes.py "/home/mariana/Experiments/2025-08-20_Pig1/NRRD" \
  --study 045b871a-06d9-4a \
  --mstart 33001 \
  --mend 33081 \
  --planes COR SAG \
  --out timings_T8.csv  
  
  
"""
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math
import csv

TimeLike = float  # seconds


def parse_acq_time(date_str: str, time_str: str) -> float:
    """
    Parse DICOM date/time to seconds from epoch-like reference.
    date_str: 'YYYYMMDD' if available; if not, pass empty string and only parse time.
    time_str: 'HHMMSS.frac' (Siemens standard)

    Returns: seconds as float since an arbitrary reference (same-day comparable).
    """
    if not time_str:
        raise ValueError("Empty AcquisitionTime")
    # Default date if not provided
    if not date_str:
        date_str = "19700101"
    # Split fractional seconds
    if "." in time_str:
        base, frac = time_str.split(".", 1)
        frac_val = float("0." + ''.join(ch for ch in frac if ch.isdigit())) if frac else 0.0
    else:
        base, frac_val = time_str, 0.0
    dt = datetime.strptime(date_str + base, "%Y%m%d%H%M%S")
    return dt.timestamp() + frac_val


def robust_plane_from_name(name: str) -> Optional[str]:
    up = name.upper()
    if "COR" in up:
        return "COR"
    if "SAG" in up:
        return "SAG"
    if "AX" in up:
        return "AX"
    return None


def extract_mag_index(name: str) -> Optional[int]:
    """
    Try to recover a running magnitude index from the filename.
    Heuristic: look for a contiguous run of digits with length >= 3.
    """
    m = re.findall(r"(\d{3,})", name)
    if not m:
        return None
    try:
        return int(m[-1])  # last group
    except Exception:
        return None


@dataclass
class Frame:
    fname: str
    plane: Optional[str]
    acq_sec: float
    mag_idx: Optional[int]


def load_tags_json(tags_path: str) -> Dict[str, Dict]:
    with open(tags_path, "r") as f:
        return json.load(f)


def find_frames(folder: str,
                study_filter: Optional[str],
                planes: Tuple[str, ...],
                m_start: Optional[int],
                m_end: Optional[int]) -> List[Frame]:
    tags_path = os.path.join(folder, "tags.json")
    if not os.path.exists(tags_path):
        raise FileNotFoundError(f"tags.json not found in {folder}")
    tags = load_tags_json(tags_path)

    frames: List[Frame] = []
    for fname, meta in tags.items():
        if not fname.lower().endswith(".nrrd"):
            continue
        # Filter by study substring in filename if given
        if study_filter and study_filter not in fname:
            continue

        # Plane from filename or metadata
        plane = robust_plane_from_name(fname)
        if plane is None:
            for k in ("SeriesDescription", "ImageType", "ProtocolName"):
                v = meta.get(k, "")
                if isinstance(v, list):
                    v = " ".join(str(x) for x in v)
                if isinstance(v, str) and v:
                    plane = robust_plane_from_name(v)
                    if plane:
                        break
        if plane is None or plane not in planes:
            continue

        # AcquisitionTime and optional StudyDate
        acq_time = meta.get("AcquisitionTime") or meta.get("(0008,0032)") or meta.get("AcquisitionTime(0008,0032)")
        if not acq_time:
            continue
        study_date = meta.get("StudyDate") or meta.get("(0008,0020)") or meta.get("StudyDate(0008,0020)") or ""

        acq_sec = parse_acq_time(str(study_date), str(acq_time))
        mag_idx = extract_mag_index(fname)

        # Filter by magnitude index range if provided
        if m_start is not None and mag_idx is not None and mag_idx < m_start:
            continue
        if m_end is not None and mag_idx is not None and mag_idx > m_end:
            continue

        frames.append(Frame(fname=fname, plane=plane, acq_sec=acq_sec, mag_idx=mag_idx))

    # Sort by acquisition time, and as tiebreaker by mag_idx then name
    frames.sort(key=lambda x: (x.acq_sec, x.mag_idx if x.mag_idx is not None else -1, x.fname))
    return frames


def mean_std(vals: List[float]) -> Tuple[float, float]:
    if not vals:
        return float("nan"), float("nan")
    mu = sum(vals) / len(vals)
    if len(vals) == 1:
        return mu, float("nan")
    var = sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)
    return mu, math.sqrt(var)


def compute_stats(frames: List[Frame], planes_order: Tuple[str, ...] = ("COR", "SAG")) -> Dict[str, object]:
    """
    Compute per-scan and per-cycle durations.

    Definitions:
    - Per-scan duration: time between consecutive frames (any plane).
    - Per-cycle duration (two consecutive scans): for sequences aligned to planes_order,
      measure t[i+2]-t[i] when frames[i].plane==planes_order[0] and frames[i+1].plane==planes_order[1].
    """
    if len(frames) < 2:
        return {
            "n_scans": len(frames),
            "n_cycles": 0,
            "per_scan_durations": [],
            "per_cycle_durations": [],
            "per_scan_mean_s": float("nan"),
            "per_scan_std_s": float("nan"),
            "per_cycle_mean_s": float("nan"),
            "per_cycle_std_s": float("nan"),
        }

    # Per-scan durations: consecutive deltas
    per_scan = [frames[i+1].acq_sec - frames[i].acq_sec for i in range(len(frames)-1)]

    # Per-cycle durations: two-scan span respecting order
    per_cycle = []
    i = 0
    while i + 2 <= len(frames) - 1:
        f0, f1, f2 = frames[i], frames[i+1], frames[i+2]
        if f0.plane == planes_order[0] and f1.plane == planes_order[1]:
            per_cycle.append(f2.acq_sec - f0.acq_sec)
            i += 2  # advance to next cycle candidate
        else:
            i += 1  # realign

    mu_scan, sd_scan = mean_std(per_scan)
    mu_cycle, sd_cycle = mean_std(per_cycle)

    return {
        "n_scans": len(frames),
        "n_cycles": len(per_cycle),
        "per_scan_durations": per_scan,
        "per_cycle_durations": per_cycle,
        "per_scan_mean_s": mu_scan,
        "per_scan_std_s": sd_scan,
        "per_cycle_mean_s": mu_cycle,
        "per_cycle_std_s": sd_cycle,
    }


def summarize(folder: str,
              study_id: Optional[str],
              m_start: Optional[int],
              m_end: Optional[int],
              planes: Tuple[str, ...] = ("COR", "SAG")) -> Dict[str, object]:
    frames = find_frames(folder, study_id, planes, m_start, m_end)
    stats = compute_stats(frames, planes_order=planes)
    return {"folder": folder, "study_id": study_id, "planes": planes, "m_range": (m_start, m_end),
            "n_frames_used": len(frames), "frames": [f.__dict__ for f in frames], **stats}


def save_csv(out_path: str, stats: Dict[str, object]) -> None:
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Metric", "Value"])
        w.writerow(["n_scans", stats["n_scans"]])
        w.writerow(["n_cycles", stats["n_cycles"]])
        w.writerow(["per_scan_mean_s", f'{stats["per_scan_mean_s"]:.6f}'])
        w.writerow(["per_scan_std_s", f'{stats["per_scan_std_s"]:.6f}'])
        w.writerow(["per_cycle_mean_s", f'{stats["per_cycle_mean_s"]:.6f}'])
        w.writerow(["per_cycle_std_s", f'{stats["per_cycle_std_s"]:.6f}'])

        w.writerow([])
        w.writerow(["Per-scan durations (s)"])
        for v in stats["per_scan_durations"]:
            w.writerow([f"{v:.6f}"])

        w.writerow([])
        w.writerow(["Per-cycle durations (s)"])
        for v in stats["per_cycle_durations"]:
            w.writerow([f"{v:.6f}"])


if __name__ == "__main__":
    # Example CLI usage:
    # python compute_empirical_scan_times.py "/path/NRRD" --study 045b871a-06d9-4a --mstart 33001 --mend 33081 --planes COR SAG --out timings.csv
    import argparse

    ap = argparse.ArgumentParser(description="Compute empirical per-scan and per-cycle durations from NRRD tags.json")
    ap.add_argument("folder", help="Folder containing NRRD files and tags.json")
    ap.add_argument("--study", dest="study_id", default=None, help="Substring to filter filenames (e.g., study ID)")
    ap.add_argument("--mstart", dest="m_start", type=int, default=None, help="Minimum magnitude index to include")
    ap.add_argument("--mend", dest="m_end", type=int, default=None, help="Maximum magnitude index to include")
    ap.add_argument("--planes", nargs="+", default=["COR", "SAG"], help="Plane order to consider for cycles, e.g. COR SAG")
    ap.add_argument("--out", dest="out_csv", default=None, help="Optional CSV output path")

    args = ap.parse_args()
    planes_tuple = tuple([p.upper() for p in args.planes])
    res = summarize(args.folder, args.study_id, args.m_start, args.m_end, planes=planes_tuple)

    # Print summary to stdout
    print(f"Folder: {res['folder']}")
    print(f"Study filter: {res['study_id']}")
    print(f"Planes order: {res['planes']}")
    print(f"Frames used: {res['n_frames_used']}")
    print(f"n_scans: {res['n_scans']} | n_cycles: {res['n_cycles']}")
    print(f"Per-scan: mean={res['per_scan_mean_s']:.6f}s, std={res['per_scan_std_s']:.6f}s")
    print(f"Per-cycle(2 scans): mean={res['per_cycle_mean_s']:.6f}s, std={res['per_cycle_std_s']:.6f}s")

    if args.out_csv:
        save_csv(args.out_csv, res)
        print(f"Saved CSV to: {args.out_csv}")
