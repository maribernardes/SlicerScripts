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
script_globals = {'folder': "/home/mariana/Experiments/2025-08-20_Pig1/NRRD", 'study_id':'045b871a-06d9-4a', 'm_start':33001, 'm_end':33081, 'planes':('COR', 'SAG')}
***************************************************************************************

***************************************************************************************
Pig 2 2025-08-21
-----------------------------------
PLAN_1
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':33001, 'm_end':33044, 'planes':('COR', 'SAG')}

REPLAN_1
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':47001, 'm_end':47034, 'planes':('COR', 'SAG')}
-----------------------------------
PLAN_2
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':57001, 'm_end':57034, 'planes':('COR', 'SAG')}

REPLAN_2
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':60001, 'm_end':60051, 'planes':('COR', 'SAG')}
-----------------------------------
PLAN_3
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':68001, 'm_end':68027, 'planes':('COR', 'SAG')}

REPLAN_3
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':71001, 'm_end':71038, 'planes':('COR', 'SAG')}
-----------------------------------
PLAN_4
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':77001, 'm_end':77033, 'planes':('COR', 'SAG')}

REPLAN_4
script_globals = {'folder': "/home/mariana/Experiments/2025-08-21_Pig2/NRRD", 'study_id':'09450140-98d9-4d', 'm_start':82001, 'm_end':82026, 'planes':('COR', 'SAG')}
***************************************************************************************

# Execute the script with the provided globals
exec(open(scriptPath, encoding='utf-8').read(), script_globals)

"""
# -*- coding: utf-8 -*-
import os, re, math
import slicer

# === inputs ===
offset       = 1000             # M->P series offset
clear_between_planes = False    # set True to save a separate, minimal scene per plane

# --- filename parsing helpers (same as before) ---
FILENAME_RE = re.compile(r"""^(?P<study>[A-Za-z0-9\-]+?)-(?P<series>\d+)-(?P<desc>[^-]+?)-\[(?P<rot>[^\]]+)\]-\[(?P<type>[^\]]+)\]\.nrrd$""")

def parse(fname):
    m = FILENAME_RE.match(fname)
    if not m: return None
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

def _format_ranges(nums):
    if not nums: return ""
    ranges = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
        else:
            ranges.append((start, prev))
            start = prev = n
    ranges.append((start, prev))
    return ", ".join(f"{a}" if a==b else f"{a}–{b}" for a,b in ranges)

def build_for_plane(plane):
    plane = plane.upper()
    print(f"\n===== Building synchronized M/P browser for {plane} [{m_start}..{m_end}] =====")

    filesM = findFiles(folder, study_id, m_start, m_end, plane, 'M')
    filesP = findFiles(folder, study_id, m_start+offset, m_end+offset, plane, 'P')
    if not filesM:
        print(f"[WARN] No M files found in {plane} {m_start}-{m_end}")
        return

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
        print(f"[WARN] No M/P pairs matched +{offset} for {plane}.")
        return
    if missingP:
        print(f"[WARN] {len(missingP)} M frames have no matching P (+{offset}): {_format_ranges(sorted(missingP))}")

    m_thousands = m_start // 1000
    p_thousands = (m_start + offset) // 1000
    name_base = f"{m_thousands}-{p_thousands} {plane}"

    # Create sequences
    seqM = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " M")
    seqP = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " P")
    for seq in (seqM, seqP):
        seq.SetIndexName("Frame")
        seq.SetIndexUnit("")
        seq.SetIndexType(slicer.vtkMRMLSequenceNode.NumericIndex)

    included_series = []

    slicer.app.pauseRender()
    slicer.mrmlScene.StartState(slicer.vtkMRMLScene.BatchProcessState)
    try:
        for frame_idx, (sM, pM, sP, pP) in enumerate(paired):
            ok = True

            volM = slicer.util.loadNodeFromFile(pM, "VolumeFile", {"name": os.path.basename(pM), "singleFile": True})
            if volM:
                seqM.SetDataNodeAtValue(volM, str(frame_idx))
                slicer.mrmlScene.RemoveNode(volM)
            else:
                ok = False
                print(f"[WARN] Failed to load M series {sM}: {pM}")

            volP = slicer.util.loadNodeFromFile(pP, "VolumeFile", {"name": os.path.basename(pP), "singleFile": True})
            if volP:
                seqP.SetDataNodeAtValue(volP, str(frame_idx))
                slicer.mrmlScene.RemoveNode(volP)
            else:
                ok = False
                print(f"[WARN] Failed to load P series {sP}: {pP}")

            if ok:
                included_series.append(sM)
    finally:
        slicer.mrmlScene.EndState(slicer.vtkMRMLScene.BatchProcessState)
        slicer.app.resumeRender()

    print(f"[OK] Built sequences for {plane}: {seqM.GetNumberOfDataNodes()} (M), {seqP.GetNumberOfDataNodes()} (P)")

    # One synchronized browser for THIS plane
    browser = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", name_base + " Browser")
    browser.SetAndObserveMasterSequenceNodeID(seqM.GetID())
    browser.AddSynchronizedSequenceNodeID(seqP.GetID())
    sequencesLogic = slicer.modules.sequences.logic()
    sequencesLogic.UpdateProxyNodesFromSequences(browser)
    browser.SetSelectedItemNumber(0)
    print("[OK] Synchronized browser created:", name_base, "Browser")

    # Missing frame warning (strict: not included in the built sequence)
    expected = set(range(m_start, m_end + 1))
    missing_frames = sorted(expected - set(included_series))
    if missing_frames:
        print(f"[WARN] {plane}: Frames missing from sequence [{m_start}..{m_end}]: {_format_ranges(missing_frames)}")
    else:
        print(f"[OK] {plane}: All frames [{m_start}..{m_end}] included.")

    # Save a scene snapshot for this plane
    out_dir = os.path.join(folder, "Sequences")
    os.makedirs(out_dir, exist_ok=True)
    mrb_path = os.path.join(out_dir, name_base + ".mrb")
    try:
        slicer.util.saveScene(mrb_path)
        print("[OK] Saved scene:", mrb_path)
    except Exception as e:
        print("[WARN] saveScene failed for", plane, ":", e)

    return (seqM, seqP, browser)

# === run for all requested planes ===
all_nodes = []
for pl in planes:
    if clear_between_planes and slicer.mrmlScene.GetNumberOfNodes() > 0:
        slicer.mrmlScene.Clear(0)
    nodes = build_for_plane(pl)
    all_nodes.append(nodes)
