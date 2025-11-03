# -*- coding: utf-8 -*-
"""
ComputeAcquisitionTimes.py

python3 ComputeAcquisitionTimes.py "/home/mariana/Experiments/2025-08-21_Pig2/DICOM_clean" \
--series-shift 1000 \
--series-filter 66 67 \
--time-tag ADT \
--out timings_dicom.csv \
--timeline-out timelines.csv \
--verbose

"""
# -*- coding: utf-8 -*-
"""
ComputeAcquisitionTimes_DICOM_v4.py

Adds per-frame slice timeline export.
"""
import os, csv, argparse, sys
from typing import Dict, List, Tuple, Optional
from statistics import mean, pstdev
from datetime import datetime

try:
    import pydicom
except Exception as e:
    print("ERROR: pydicom is required. Install with: pip install pydicom", file=sys.stderr)
    raise

def parse_time_from_ds(ds, prefer: str = "ADT") -> Optional[float]:
    def parse_adt(val):
        s = str(val)
        if '.' in s:
            base, frac = s.split('.', 1)
            dt = datetime.strptime(base, "%Y%m%d%H%M%S")
            return dt.timestamp() + float("0."+frac)
        dt = datetime.strptime(s, "%Y%m%d%H%M%S")
        return dt.timestamp()

    def parse_date_time(date, time):
        sdate = str(date)
        stime = str(time)
        if '.' in stime:
            base, frac = stime.split('.', 1)
            dt = datetime.strptime(sdate+base, "%Y%m%d%H%M%S")
            return dt.timestamp() + float("0."+frac)
        dt = datetime.strptime(sdate+stime, "%Y%m%d%H%M%S")
        return dt.timestamp()

    order = {"ADT":["ADT","AT","CT"], "AT":["AT","ADT","CT"], "CT":["CT","ADT","AT"]}.get(prefer.upper(), ["ADT","AT","CT"])

    def get(field):
        try:
            return getattr(ds, field)
        except Exception:
            return None

    for tag in order:
        if tag == "ADT":
            adt = get("AcquisitionDateTime")
            if adt:
                try: return parse_adt(adt)
                except Exception: pass
        elif tag == "AT":
            date = get("AcquisitionDate") or get("StudyDate") or get("SeriesDate") or get("ContentDate")
            time = get("AcquisitionTime")
            if date and time:
                try: return parse_date_time(date, time)
                except Exception: pass
        elif tag == "CT":
            date = get("ContentDate") or get("SeriesDate") or get("StudyDate") or get("AcquisitionDate")
            time = get("ContentTime")
            if date and time:
                try: return parse_date_time(date, time)
                except Exception: pass
    return None

def plane_from_iop(ds) -> Optional[str]:
    try:
        iop = [float(x) for x in ds.ImageOrientationPatient]
        if len(iop) != 6: return None
        rx,ry,rz, cx,cy,cz = iop
        nx = ry*cz - rz*cy
        ny = rz*cx - rx*cz
        nz = rx*cy - ry*cx
        ax = [abs(nx), abs(ny), abs(nz)]
        k = ax.index(max(ax))
        return {2:"AX", 1:"COR", 0:"SAG"}[k]
    except Exception:
        return None

def load_dicom_series(root: str, series_filter_prefixes: Optional[List[str]]=None, time_pref: str="ADT", verbose: bool=False):
    series_raw: Dict[int, List[dict]] = {}
    diag = {"read":0, "accepted":0, "no_series":0, "filtered_series":0, "no_time":0}
    for dirpath, _, files in os.walk(root):
        for fn in files:
            fp = os.path.join(dirpath, fn)
            try:
                ds = pydicom.dcmread(fp, stop_before_pixels=True, force=True)
            except Exception:
                continue
            diag["read"] += 1

            try:
                s_no_raw = ds.SeriesNumber
                s_no = int(str(s_no_raw))
            except Exception:
                diag["no_series"] += 1
                continue

            if series_filter_prefixes:
                sn = str(s_no)
                if not any(sn.startswith(pfx) for pfx in series_filter_prefixes):
                    diag["filtered_series"] += 1
                    continue

            t = parse_time_from_ds(ds, prefer=time_pref)
            if t is None:
                diag["no_time"] += 1
                continue

            pl = plane_from_iop(ds)
            series_raw.setdefault(s_no, []).append({"t": t, "plane": pl})
            diag["accepted"] += 1

    if verbose:
        print(f"Parsed files: {diag['read']} | accepted: {diag['accepted']} | series found: {len(series_raw)}")
        print(f"Skipped: no_series={diag['no_series']}, filtered_series={diag['filtered_series']}, no_time={diag['no_time']}")
    return series_raw

def split_planes_for_series(entries: List[dict], include_ax: bool=False) -> Dict[str, List[float]]:
    ts = sorted(entries, key=lambda x: x["t"])
    planes = [x["plane"] for x in ts if x["plane"] is not None]
    has_cor = any(p == "COR" for p in planes)
    has_sag = any(p == "SAG" for p in planes)
    use_iop = has_cor and has_sag

    cor: List[float] = []
    sag: List[float] = []
    ax:  List[float] = []

    if use_iop:
        for x in ts:
            if x["plane"] == "COR":
                cor.append(x["t"])
            elif x["plane"] == "SAG":
                sag.append(x["t"])
            elif x["plane"] == "AX" and include_ax:
                ax.append(x["t"])
    else:
        n = len(ts)
        k = 3 if n >= 6 else max(1, n//2)
        cor = [x["t"] for x in ts[:k]]
        sag = [x["t"] for x in ts[k:2*k]] if n >= 2*k else [x["t"] for x in ts[k:]]
    return {"COR": cor, "SAG": sag, "AX": ax}

def build_series_map(series_raw: Dict[int, List[dict]], include_ax: bool=False) -> Dict[int, Dict[str, List[float]]]:
    return {s: split_planes_for_series(entries, include_ax=include_ax) for s, entries in series_raw.items()}

def abs_diffs_sorted(a: List[float], b: List[float]) -> List[float]:
    a = sorted(a)
    b = sorted(b)
    n = min(len(a), len(b))
    return [abs(a[i]-b[i]) for i in range(n)]

def summarize_pairs(series_map: Dict[int, dict], series_shift: int=1000, include_ax: bool=False):
    planes = ["COR","SAG"] + (["AX"] if include_ax else [])
    rows = []
    all_align_diffs = []
    for s in sorted(series_map.keys()):
        s_p = s + series_shift
        if s_p not in series_map:
            continue
        for plane in planes:
            tm = sorted(series_map[s].get(plane, []))
            tp = sorted(series_map[s_p].get(plane, []))
            if not tm and not tp:
                continue
            combined = sorted(tm + tp)
            dur = (combined[-1] - combined[0]) if len(combined) >= 2 else 0.0
            diffs = abs_diffs_sorted(tm, tp)
            mu = mean(diffs) if diffs else float('nan')
            sd = pstdev(diffs) if len(diffs) > 1 else (0.0 if diffs else float('nan'))
            all_align_diffs.extend(diffs)
            rows.append({
                "mag_series": s,
                "pha_series": s_p,
                "plane": plane,
                "n_M": len(tm),
                "n_P": len(tp),
                "complex_duration_s": dur,
                "mp_align_mean_abs_dt_s": mu,
                "mp_align_sd_abs_dt_s": sd,
            })
    overall_mu = mean(all_align_diffs) if all_align_diffs else float('nan')
    overall_sd = pstdev(all_align_diffs) if len(all_align_diffs) > 1 else (0.0 if all_align_diffs else float('nan'))
    return rows, overall_mu, overall_sd

def build_timelines(series_raw: Dict[int, List[dict]], series_shift: int=1000, include_ax: bool=False):
    rows = []
    for s in sorted(series_raw.keys()):
        sp = s + series_shift
        if sp not in series_raw:
            continue
        smap = split_planes_for_series(series_raw[s], include_ax=include_ax)
        pmap = split_planes_for_series(series_raw[sp], include_ax=include_ax)

        labeled = []
        for t in smap["COR"]:
            labeled.append(("M","COR",t))
        for t in pmap["COR"]:
            labeled.append(("P","COR",t))
        for t in smap["SAG"]:
            labeled.append(("M","SAG",t))
        for t in pmap["SAG"]:
            labeled.append(("P","SAG",t))

        if not labeled:
            continue
        labeled.sort(key=lambda x: x[2])
        t0 = labeled[0][2]

        row = {
            "mag_series": s,
            "pha_series": sp,
            "n_found": len(labeled),
        }
        for i, (mp, plane, t) in enumerate(labeled[:12], start=1):
            row[f"ord_{i}_label"] = f"{mp}-{plane}"
            row[f"ord_{i}_deltaT_s"] = t - t0
        for i in range(len(labeled)+1, 13):
            row[f"ord_{i}_label"] = ""
            row[f"ord_{i}_deltaT_s"] = ""
        rows.append(row)
    return rows

def main():
    ap = argparse.ArgumentParser(description="Compute per-plane complex timings and per-frame 12-slice timelines from DICOM (series-number pairing).")
    ap.add_argument("root", help="Root folder containing DICOM files")
    ap.add_argument("--series-shift", type=int, default=1000, help="Phase series = Magnitude series + shift (default 1000)")
    ap.add_argument("--series-filter", nargs="*", default=None, help="Optional list of SeriesNumber prefixes to include (e.g., 66 67)")
    ap.add_argument("--time-tag", choices=["ADT","AT","CT"], default="ADT", help="Preferred time tag: ADT, AT, or CT")
    ap.add_argument("--include-ax", action="store_true", help="Include axial plane if present")
    ap.add_argument("--out", default=None, help="Output CSV path for pair-plane summary")
    ap.add_argument("--timeline-out", default=None, help="Output CSV path for per-frame 12-slice timelines")
    ap.add_argument("--verbose", action="store_true", help="Verbose parsing and diagnostics")
    args = ap.parse_args()

    series_raw = load_dicom_series(
        root=args.root,
        series_filter_prefixes=args.series_filter,
        time_pref=args.time_tag,
        verbose=args.verbose
    )

    series_map = build_series_map(series_raw, include_ax=args.include_ax)
    rows, overall_mu, overall_sd = summarize_pairs(series_map, series_shift=args.series_shift, include_ax=args.include_ax)
    print(f"Pair-plane rows: {len(rows)}")
    print(f"Overall M↔P alignment |Δt|: {overall_mu:.6f} ± {overall_sd:.6f} s" if rows else "No paired series found.")

    if args.out:
        with open(args.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["mag_series","pha_series","plane","n_M","n_P","complex_duration_s","mp_align_mean_abs_dt_s","mp_align_sd_abs_dt_s"])
            for r in rows:
                w.writerow([r["mag_series"], r["pha_series"], r["plane"], r["n_M"], r["n_P"],
                            f"{r['complex_duration_s']:.6f}",
                            (f"{r['mp_align_mean_abs_dt_s']:.6f}" if r['n_M'] and r['n_P'] else ""),
                            (f"{r['mp_align_sd_abs_dt_s']:.6f}" if r['n_M'] and r['n_P'] and r['n_M']+r['n_P']>2 else "")])
        print(f"Wrote summary CSV: {args.out}")

    if args.timeline_out:
        timelines = build_timelines(series_raw, series_shift=args.series_shift, include_ax=args.include_ax)
        headers = ["mag_series","pha_series","n_found"]
        for i in range(1,13):
            headers += [f"ord_{i}_label", f"ord_{i}_deltaT_s"]
        with open(args.timeline_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in timelines:
                w.writerow(r)
        print(f"Wrote timeline CSV: {args.timeline_out}")

if __name__ == "__main__":
    main()