# -*- coding: utf-8 -*-

"""
# Define the script path
scriptPath = "/home/mariana/SlicerScripts/ExtractSequences/CreateSequenceFromNrrd.py"

# --- parameters (edit these) ---
folder       = "/home/mariana/Experiments/2025-08-21_Pig2/out-nrrd-4"
study_id     = "045b871a-06d9-4a"
series_start = 33001
series_end   = 33081
plane        = "COR"   # 'AX'|'COR'|'SAG'
modality     = "M"     # 'M'|'P' or None


# Define the variable to pass
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/out-nrrd-4", 'study_id':'045b871a-06d9-4a', 'series_start':33001, 'series_end':33081, 'plane':'COR', 'modality': 'M'}


# Execute the script with the provided globals
exec(open(scriptPath, encoding='utf-8').read(), script_globals)

"""

# Paste in Slicer's Python Console

import os, re
import slicer
import SimpleITK as sitk
import sitkUtils
import slicer
import re, math

# --- helpers copied/adapted from earlier ---
FILENAME_RE = re.compile(r"""^(?P<study>[A-Za-z0-9\-]+?)-(?P<series>\d+)-(?P<desc>[^-]+?)-\[(?P<rot>[^\]]+)\]-\[(?P<type>[^\]]+)\]\.nrrd$""")

def parse(fname):
    m = FILENAME_RE.match(fname)
    if not m:
        return None
    d = m.groupdict()                 # includes 'study','series','desc','rot','type'
    d["series"] = int(d["series"])
    d["type"]   = " ".join(d["type"].split())   # normalize spaces
    d["__fname"] = fname
    return d


def _nums_from_str(s):
    # robustly pull floats/ints out of strings like "[1  0  0  0  0  -1]"
    return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s)]

def _unit(v):
    n = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/n, v[1]/n, v[2]/n) if n else (0.0, 0.0, 0.0)

def nearestAxisIdx(v):
    """
    v can be a tuple/list of 3 floats OR a string like "[0 1 0]".
    Returns 0 for R(x), 1 for A(y), 2 for S(z).
    """
    if isinstance(v, str):
        nums = _nums_from_str(v)
        if len(nums) < 3:
            raise ValueError(f"Cannot parse 3 numbers from: {v}")
        v = (nums[0], nums[1], nums[2])
    vx, vy, vz = _unit(v)
    a = [abs(vx), abs(vy), abs(vz)]
    return a.index(max(a))

def planeFromRot(rot):
    """
    rot is the 6-number string inside brackets in the filename.
    Works for any sign/order; classifies by in-plane axes (fallback: normal).
    Returns 'AX'|'COR'|'SAG' or None.
    """
    nums = _nums_from_str(rot)
    if len(nums) != 6:
        return None

    u = _unit((nums[0], nums[1], nums[2]))
    v = _unit((nums[3], nums[4], nums[5]))

    # primary attempt: which two axes are spanned?
    axes = {nearestAxisIdx(u), nearestAxisIdx(v)}
    if axes == {0, 1}:  # R & A
        return "AX"
    if axes == {0, 2}:  # R & S
        return "COR"
    if axes == {1, 2}:  # A & S
        return "SAG"

    # fallback: use normal
    nx = u[1]*v[2] - u[2]*v[1]
    ny = u[2]*v[0] - u[0]*v[2]
    nz = u[0]*v[1] - u[1]*v[0]
    n_axis = nearestAxisIdx((nx, ny, nz))
    return {"2":"AX","1":"COR","0":"SAG"}[str(n_axis)]


def hasToken(img_type, token):  # token 'M' or 'P'
    return token in img_type.replace(",", " ").split()

def findFiles(folder, study, s0, s1, plane, modality):
    out=[]
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".nrrd"): continue
        info = parse(fname)
        if not info: continue
        if info["study"] != study: continue
        if not (s0 <= info["series"] <= s1): continue
        if planeFromRot(info["rot"]) != plane: continue
        if modality and not hasToken(info["type"], modality): continue
        out.append((info["series"], os.path.join(folder, fname)))
    out.sort(key=lambda x:x[0])
    return out


# ---------- SAFE EXECUTION (drop-in replacement) ----------
try:
    folder; study_id; series_start; series_end; plane; modality
except NameError:
    raise RuntimeError("Please define folder, study_id, series_start, series_end, plane, modality before running.")

files = findFiles(folder, study_id, series_start, series_end, plane.upper(), (modality.upper() if modality else None))
if not files:
    print("No matches"); raise SystemExit

print(f"[INFO] Will load {len(files)} frame(s). Building sequence…")

# Pause rendering & batch scene edits to avoid UI churn crashes
slicer.app.pauseRender()
slicer.mrmlScene.StartState(slicer.vtkMRMLScene.BatchProcessState)
try:
    # Create sequence & browser
    seqNodeName = f"{series_start}-{series_end} {modality} {plane}"
    seqNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", seqNodeName)
    seqNode.SetIndexName("SeriesNumber")
    seqNode.SetIndexUnit("")  # optional

    browserName = f"Browser_{series_start}-{series_end} {modality} {plane}"
    browser = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", browserName)
    browser.SetAndObserveMasterSequenceNodeID(seqNode.GetID())

    # Determine zero-pad width from series range (e.g., 33001..33081 -> width 5)
    zwidth = max(1, len(str(max(s for s,_ in files))))

    prev_series = None
    for series, path in files:
        # Gaps report
        if prev_series is not None and series != prev_series + 1:
            missing = list(range(prev_series + 1, series))
            print(f"[WARN] Missing series: {missing}")
        prev_series = series
        print(f"[FRAME] series={series}  file={os.path.basename(path)}")
        # NEW API: returns the node directly; DO NOT pass returnNode
        vol = slicer.util.loadNodeFromFile(
            path,
            "VolumeFile",
            {"name": os.path.basename(path), "singleFile": True}
        )
        if not vol:
            print(f"[WARN] Failed to load {path}, skipping.")
            continue
        idx_str = f"{series:0{zwidth}d}"
        seqNode.SetDataNodeAtValue(vol, idx_str)
        slicer.mrmlScene.RemoveNode(vol)
    browser.SetSelectedItemNumber(0)

finally:
    slicer.mrmlScene.EndState(slicer.vtkMRMLScene.BatchProcessState)
    slicer.app.resumeRender()

print(f"[OK] Sequence built with {seqNode.GetNumberOfDataNodes()} items (original geometry preserved).")

# Optional save (you can comment this out while debugging)
out_name = f"{series_start}-{series_end} {modality} {plane}.mrb"
mrb_path = os.path.join(folder, out_name)
try:
    slicer.util.saveScene(mrb_path)
    print("[OK] Saved scene:", mrb_path)
except Exception as e:
    print("[WARN] saveScene failed:", e)
