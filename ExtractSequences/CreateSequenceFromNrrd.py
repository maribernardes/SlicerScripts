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
import os, re, math, gc
import slicer

# ========= OTHER INPUTS =========
offset       = 1000             # M->P series offset
clear_between_planes = True    # set True to save a separate, minimal scene per plane
save_dir     = os.path.join(folder, "Sequences")
initial_cleanup = True  # If you want to be absolutely sure the script starts clean, set initial_cleanup = True. 
                        # If you’re running inside a fresh Slicer session or you want to keep other nodes, set it to False.
# =================================


# --------- filename parsing helpers ----------
FILENAME_RE = re.compile(
    r"""^(?P<study>[A-Za-z0-9\-]+?)-(?P<series>\d+)-(?P<desc>[^-]+?)-\[(?P<rot>[^\]]+)\]-\[(?P<type>[^\]]+)\]\.nrrd$"""
)

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

def hasToken(img_type, token):  # token 'M' or 'P'
    return token in img_type.replace(",", " ").split()

def findFiles(folder, study, s0, s1, plane, modality):
    out = []
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
    out.sort(key=lambda x: x[0])
    return out

def _format_ranges(nums):
    if not nums:
        return ""
    nums = sorted(nums)
    ranges = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
        else:
            ranges.append((start, prev))
            start = prev = n
    ranges.append((start, prev))
    return ", ".join(f"{a}" if a == b else f"{a}–{b}" for a, b in ranges)

# ---------- cleanup helpers ----------
def remove_sequence_nodes():
    """Remove prior sequence-related nodes (browsers + sequences + common proxies) without touching singletons."""
    for cls in ("vtkMRMLSequenceBrowserNode", "vtkMRMLSequenceNode"):
        for n in list(slicer.util.getNodesByClass(cls)):
            slicer.mrmlScene.RemoveNode(n)
    # Remove likely proxies with our naming patterns
    for n in list(slicer.util.getNodes("*").values()):
        nm = n.GetName() if hasattr(n, "GetName") else ""
        if any(tag in nm for tag in (" Browser", " M", " P")):
            try:
                slicer.mrmlScene.RemoveNode(n)
            except Exception:
                pass
    slicer.app.processEvents()

def soft_clear_scene():
    """Try to clear the scene but keep singletons. Falls back to targeted cleanup if not supported."""
    try:
        slicer.mrmlScene.Clear(False)   # keep singletons/views/modules
        slicer.app.processEvents()
        print("[INIT] Soft-cleared scene (kept singletons).")
    except Exception as e:
        print("[INIT] Soft clear failed; falling back to targeted cleanup:", e)
        # remove common data-bearing nodes (defensive)
        classes = [
            "vtkMRMLSequenceBrowserNode","vtkMRMLSequenceNode",
            "vtkMRMLScalarVolumeNode","vtkMRMLVectorVolumeNode","vtkMRMLLabelMapVolumeNode",
            "vtkMRMLMarkupsFiducialNode","vtkMRMLMarkupsCurveNode","vtkMRMLMarkupsPlaneNode",
            "vtkMRMLTransformNode","vtkMRMLModelNode","vtkMRMLTableNode"
        ]
        for cls in classes:
            for n in list(slicer.util.getNodesByClass(cls)):
                slicer.mrmlScene.RemoveNode(n)
        slicer.app.processEvents()
        print("[INIT] Targeted cleanup complete.")

# ---------- optional initial cleanup ----------
if initial_cleanup:
    soft_clear_scene()

# ============ PASS 1: discover pairable frames per plane ============
plane_info = {}
for pl in planes:
    filesM = findFiles(folder, study_id, m_start, m_end, pl, 'M')
    filesP = findFiles(folder, study_id, m_start + offset, m_end + offset, pl, 'P')
    mapM = {s: p for (s, p) in filesM}
    mapP = {s: p for (s, p) in filesP}
    pairable = {s for s in mapM.keys() if (s + offset) in mapP}
    plane_info[pl] = {"mapM": mapM, "mapP": mapP, "pairable": pairable}

global_pairable = None
for pl, info in plane_info.items():
    if global_pairable is None:
        global_pairable = set(info["pairable"])
    else:
        global_pairable &= info["pairable"]

global_pairable = sorted(global_pairable)
if not global_pairable:
    for pl, info in plane_info.items():
        print(f"[WARN] {pl}: pairable frames: {_format_ranges(sorted(info['pairable'])) or 'none'}")
    raise RuntimeError("No common pairable frames across requested planes (M&P).")

excluded_by_filter = sorted(set(range(m_start, m_end + 1)) - set(global_pairable))
if excluded_by_filter:
    print(f"[WARN] Cross-plane sync filter excluded: {_format_ranges(excluded_by_filter)}")

# ============ builder ============
def build_for_plane(plane, kept_frames, info):
    plane = plane.upper()
    kept_frames = sorted(kept_frames)
    m_thousands = m_start // 1000
    p_thousands = (m_start + offset) // 1000
    name_base = f"{m_thousands}-{p_thousands} {plane}"

    seqM = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " M")
    seqP = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", name_base + " P")
    for seq in (seqM, seqP):
        seq.SetIndexName("Frame")
        seq.SetIndexUnit("")
        seq.SetIndexType(slicer.vtkMRMLSequenceNode.NumericIndex)

    included = []

    slicer.app.pauseRender()
    slicer.mrmlScene.StartState(slicer.vtkMRMLScene.BatchProcessState)
    try:
        for frame_idx, sM in enumerate(kept_frames):
            pM = info["mapM"].get(sM)
            pP = info["mapP"].get(sM + offset)
            if not pM or not pP:
                continue
            volM = slicer.util.loadNodeFromFile(pM, "VolumeFile", {"singleFile": True})
            volP = slicer.util.loadNodeFromFile(pP, "VolumeFile", {"singleFile": True})
            if volM:
                seqM.SetDataNodeAtValue(volM, str(frame_idx))
                slicer.mrmlScene.RemoveNode(volM)
            if volP:
                seqP.SetDataNodeAtValue(volP, str(frame_idx))
                slicer.mrmlScene.RemoveNode(volP)
            if volM and volP:
                included.append(sM)
    finally:
        slicer.mrmlScene.EndState(slicer.vtkMRMLScene.BatchProcessState)
        slicer.app.resumeRender()

    browser = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceBrowserNode", name_base + " Browser")
    browser.SetAndObserveMasterSequenceNodeID(seqM.GetID())
    browser.AddSynchronizedSequenceNodeID(seqP.GetID())
    slicer.modules.sequences.logic().UpdateProxyNodesFromSequences(browser)
    browser.SetSelectedItemNumber(0)

    print(f"[OK] {plane}: {seqM.GetNumberOfDataNodes()} frames M, {seqP.GetNumberOfDataNodes()} frames P")
    return name_base

# ============ PASS 2: build & save per plane ============
os.makedirs(save_dir, exist_ok=True)

for pl in planes:
    # ensure no residues from previous runs before building/saving this plane
    remove_sequence_nodes()

    name_base = build_for_plane(pl, global_pairable, plane_info[pl])

    # paranoid: ensure only this plane’s nodes remain before saving
    for n in list(slicer.util.getNodesByClass("vtkMRMLSequenceNode")):
        if pl not in n.GetName():
            slicer.mrmlScene.RemoveNode(n)
    for n in list(slicer.util.getNodesByClass("vtkMRMLSequenceBrowserNode")):
        if pl not in n.GetName():
            slicer.mrmlScene.RemoveNode(n)
    slicer.app.processEvents()

    mrb_path = os.path.join(save_dir, name_base + ".mrb")
    slicer.util.saveScene(mrb_path)
    print("[OK] Saved:", mrb_path)

    # remove this plane’s nodes before next plane (keeps scene minimal throughout)
    remove_sequence_nodes()

print("\n[DONE] Saved independent bundles for:", ", ".join(planes))