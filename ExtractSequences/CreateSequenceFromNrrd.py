# -*- coding: utf-8 -*-

"""
# Define the script path
scriptPath = "/home/mariana/SlicerScripts/ExtractSequences/CreateSequenceFromNrrd.py"

# --- parameters (edit these) ---
folder       = "/home/mariana/Experiments/2025-08-21_Pig2/NRRD"
study_id     = "09450140-98d9-4d"
m_start = 68001
m_end   = 68027
plane        = "COR"   # 'AX'|'COR'|'SAG'


# Define the variable to pass
***************************************************************************************
Pig 1 2025-08-20
-----------------------------------
PLAN_0
script_globals = {'folder': "/home/mariana/Experiments/2025-08-20_Pig1/NRRD", 'study_id':'045b871a-06d9-4a', 'm_start':33001, 'm_end':33081, 'plane':'COR'}
***************************************************************************************

***************************************************************************************
Pig 2 2025-08-21
-----------------------------------
PLAN_1
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':33001, 'm_end':33044, 'plane':'COR'}

REPLAN_1
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':47001, 'm_end':47034, 'plane':'COR'}
-----------------------------------
PLAN_2
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':57001, 'm_end':57034, 'plane':'COR'}

REPLAN_2
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':60001, 'm_end':60051, 'plane':'COR'}
-----------------------------------
PLAN_3
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':68001, 'm_end':68027, 'plane':'COR'}

REPLAN_3
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':71001, 'm_end':71038, 'plane':'COR'}
-----------------------------------
PLAN_4
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':77001, 'm_end':77033, 'plane':'COR'}

REPLAN_4
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':82001, 'm_end':82026, 'plane':'COR'}
***************************************************************************************

# Execute the script with the provided globals
exec(open(scriptPath, encoding='utf-8').read(), script_globals)

"""

import os, re, math
import slicer

# --------- filename parsing (same as yours) ----------
FILENAME_RE = re.compile(r"""^(?P<study>[A-Za-z0-9\-]+?)-(?P<series>\d+)-(?P<desc>[^-]+?)-\[(?P<rot>[^\]]+)\]-\[(?P<type>[^\]]+)\]\.nrrd$""")

def parse(fname):
    m = FILENAME_RE.match(fname)
    if not m:
        return None
    d = m.groupdict()
    d["series"] = int(d["series"])
    d["type"]   = " ".join(d["type"].split())
    d["__fname"] = fname
    return d

def _nums_from_str(s):
    return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s)]

def _unit(v):
    n = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/n, v[1]/n, v[2]/n) if n else (0.0, 0.0, 0.0)

def nearestAxisIdx(v):
    if isinstance(v, str):
        nums = _nums_from_str(v)
        if len(nums) < 3:
            raise ValueError(f"Cannot parse 3 numbers from: {v}")
        v = (nums[0], nums[1], nums[2])
    vx, vy, vz = _unit(v)
    a = [abs(vx), abs(vy), abs(vz)]
    return a.index(max(a))

def planeFromRot(rot):
    nums = _nums_from_str(rot)
    if len(nums) != 6:
        return None
    u = _unit((nums[0], nums[1], nums[2]))
    v = _unit((nums[3], nums[4], nums[5]))
    axes = {nearestAxisIdx(u), nearestAxisIdx(v)}
    if axes == {0,1}: return "AX"
    if axes == {0,2}: return "COR"
    if axes == {1,2}: return "SAG"
    nx = u[1]*v[2] - u[2]*v[1]
    ny = u[2]*v[0] - u[0]*v[2]
    nz = u[0]*v[1] - u[1]*v[0]
    n_axis = nearestAxisIdx((nx,ny,nz))
    return {"2":"AX","1":"COR","0":"SAG"}[str(n_axis)]

def hasToken(img_type, token):  # 'M' or 'P'
    return token in img_type.replace(",", " ").split()

def findFiles(folder, study, s0, s1, plane, modality):
    out=[]
    plane = plane.upper()
    modality = modality.upper() if modality else None
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".nrrd"): 
            continue
        info = parse(fname)
        if not info:
            continue
        if info["study"] != study:
            continue
        if not (s0 <= info["series"] <= s1):
            continue
        if planeFromRot(info["rot"]) != plane:
            continue
        if modality and not hasToken(info["type"], modality):
            continue
        out.append((info["series"], os.path.join(folder, fname)))
    out.sort(key=lambda x:x[0])
    return out

# --------- builder that pairs M/P by +offset and makes ONE synced browser ----------

# ---------- SAFE EXECUTION (drop-in replacement) ----------
try:
    folder; study_id; m_start; m_end; plane
except NameError:
    raise RuntimeError("Please define folder, study_id, m_start, m_end, plane before running.")

try:
    offset
except NameError:
    offset = 1000


filesM = findFiles(folder, study_id, m_start, m_end, plane, 'M')
filesP = findFiles(folder, study_id, m_start+offset, m_end+offset, plane, 'P')
if not filesM:
    raise RuntimeError(f"No M files found in {plane} {m_start}-{m_end}")

mapM = {s:p for (s,p) in filesM}
mapP = {s:p for (s,p) in filesP}

paired, missingP = [], []
for sM in sorted(mapM.keys()):
    sP = sM + offset
    if sP in mapP:
        paired.append((sM, mapM[sM], sP, mapP[sP]))
    else:
        missingP.append(sM)
if not paired:
    raise RuntimeError("No M/P pairs matched the +offset rule.")
if missingP:
    print(f"[WARN] {len(missingP)} M frames lack a matching P (+{offset}).")

# ---- Unified base name: "<MM>-<PP> <PLANE>", using thousands of start and start+offset
m_thousands = m_start // 1000
p_thousands = (m_start + offset) // 1000
name_base = f"{m_thousands}-{p_thousands} {plane.upper()}"

# Sequence nodes (keep them identifiable as M/P, but browser/mrb use the base)
seqM = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " M")
seqP = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " P")
for seq in (seqM, seqP):
    seq.SetIndexName("Frame")
    seq.SetIndexUnit("")
    seq.SetIndexType(slicer.vtkMRMLSequenceNode.NumericIndex)

slicer.app.pauseRender()
slicer.mrmlScene.StartState(slicer.vtkMRMLScene.BatchProcessState)
try:
    for frame_idx, (_, pM, _, pP) in enumerate(paired):
        volM = slicer.util.loadNodeFromFile(pM, "VolumeFile", {"name": os.path.basename(pM), "singleFile": True})
        if volM:
            seqM.SetDataNodeAtValue(volM, str(frame_idx))
            slicer.mrmlScene.RemoveNode(volM)
        else:
            print(f"[WARN] Failed to load {pM}")
        volP = slicer.util.loadNodeFromFile(pP, "VolumeFile", {"name": os.path.basename(pP), "singleFile": True})
        if volP:
            seqP.SetDataNodeAtValue(volP, str(frame_idx))
            slicer.mrmlScene.RemoveNode(volP)
        else:
            print(f"[WARN] Failed to load {pP}")
finally:
    slicer.mrmlScene.EndState(slicer.vtkMRMLScene.BatchProcessState)
    slicer.app.resumeRender()

print(f"[OK] Built sequences: {seqM.GetNumberOfDataNodes()} (M), {seqP.GetNumberOfDataNodes()} (P)")

# ---- Single synchronized browser named with the same base
browser = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", name_base)
browser.SetAndObserveMasterSequenceNodeID(seqM.GetID())
browser.AddSynchronizedSequenceNodeID(seqP.GetID())

# create proxy nodes
sequencesLogic = slicer.modules.sequences.logic()
sequencesLogic.UpdateProxyNodesFromSequences(browser)
browser.SetSelectedItemNumber(0)
print("[OK] Synchronized browser created:", name_base)

# ---- Save with the same base name
out_dir = os.path.join(folder, "Sequences")
os.makedirs(out_dir, exist_ok=True)
mrb_path = os.path.join(out_dir, name_base + ".mrb")
try:
    slicer.util.saveScene(mrb_path)
    print("[OK] Saved scene:", mrb_path)
except Exception as e:
    print("[WARN] saveScene failed:", e)