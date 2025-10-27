# -*- coding: utf-8 -*-
"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/ScalarVolumes/CompareBias.py"

# Define the variable to pass
script_globals = {'volumeA': '71-72 COR M', 'volumeB': '71-72 SAG M', 'maskA': 'Mask', 'maskB': 'Mask'}
script_globals = {'volumeA': '82-83 COR M', 'volumeB': '82-83 SAG M', 'maskA': 'Mask', 'maskB': 'Mask'}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)
"""

import numpy as np
import SimpleITK as sitk
from math import exp
import sitkUtils
import slicer
import vtk

# ----------------- Helpers -----------------
def get_sitk_image(node_name):
    node = slicer.util.getNode(node_name)
    return sitkUtils.PullVolumeFromSlicer(node), node

def push_sitk_image(im, name, ref_node=None):
    outNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", name)
    sitkUtils.PushVolumeToSlicer(im, outNode)
    if ref_node:
        outNode.SetOrigin(ref_node.GetOrigin())
        outNode.SetSpacing(ref_node.GetSpacing())
        m = vtk.vtkMatrix4x4()
        ref_node.GetIJKToRASDirectionMatrix(m)
        outNode.SetIJKToRASDirectionMatrix(m)
    return outNode

def resample_mask_to_reference(mask_sitk, ref_sitk):
    rf = sitk.ResampleImageFilter()
    rf.SetReferenceImage(ref_sitk)
    rf.SetInterpolator(sitk.sitkNearestNeighbor)
    rf.SetDefaultPixelValue(0)
    rf.SetOutputPixelType(sitk.sitkUInt8)
    mask_bin = sitk.BinaryThreshold(sitk.Cast(mask_sitk, sitk.sitkUInt8), 1, 255, 1, 0)
    return rf.Execute(mask_bin)

def to_sitk_mask_like(slice_img, slice_mask=None):
    if slice_mask is None:
        otsu = sitk.OtsuThreshold(slice_img, 0, 1)
        return sitk.Cast(otsu, sitk.sitkUInt8)
    m = sitk.Cast(slice_mask, sitk.sitkUInt8)
    m = sitk.BinaryThreshold(m, 1, 255, 1, 0)
    return m

def seg_to_mask_for_reference(seg_node_name, ref_volume_name, segment_names=None, out_label_name=None):
    segNode = slicer.util.getNode(seg_node_name)
    refNode = slicer.util.getNode(ref_volume_name)

    tl = slicer.vtkSlicerTransformLogic()
    if segNode.GetParentTransformNode():
        tl.hardenTransform(segNode)
    if refNode.GetParentTransformNode():
        tl.hardenTransform(refNode)

    if out_label_name is None:
        out_label_name = f"{seg_node_name}_asMask_{ref_volume_name}"
    labelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode", out_label_name)

    logic = slicer.vtkSlicerSegmentationsModuleLogic()

    if segment_names is None:
        logic.ExportVisibleSegmentsToLabelmapNode(segNode, labelNode, refNode)
    else:
        ids = vtk.vtkStringArray()
        seg = segNode.GetSegmentation()
        for nm in segment_names:
            sid = seg.GetSegmentIdBySegmentName(nm)
            if sid is None:
                raise ValueError(f"Segment name not found: {nm}")
            ids.InsertNextValue(sid)
        logic.ExportSegmentsToLabelmapNode(segNode, ids, labelNode, refNode)

    mask_sitk = sitkUtils.PullVolumeFromSlicer(labelNode)
    mask_sitk = sitk.BinaryThreshold(sitk.Cast(mask_sitk, sitk.sitkUInt8), 1, 255, 1, 0)
    return mask_sitk, labelNode

def extract_slice_2d(img3d, k):
    size = list(img3d.GetSize())
    idx = [0, 0, k]
    ext_size = [size[0], size[1], 0]
    extractor = sitk.ExtractImageFilter()
    extractor.SetSize(ext_size)
    extractor.SetIndex(idx)
    slice2d = extractor.Execute(img3d)
    spacing3d = img3d.GetSpacing()
    slice2d.SetSpacing((spacing3d[0], spacing3d[1]))
    return sitk.Cast(slice2d, sitk.sitkFloat32)

def stack_slices_to_3d(slices, ref3d):
    join = sitk.JoinSeriesImageFilter()
    vol = join.Execute(slices)
    xy = slices[0].GetSpacing()
    z = ref3d.GetSpacing()[2]
    vol.SetSpacing((xy[0], xy[1], z))
    vol.SetOrigin(ref3d.GetOrigin())
    vol.SetDirection(ref3d.GetDirection())
    return sitk.Cast(vol, sitk.sitkFloat32)

def per_slice_mask(img3d, mask3d=None):
    masks = []
    depth = img3d.GetDepth()
    for k in range(depth):
        s2d = extract_slice_2d(img3d, k)
        m2d = extract_slice_2d(mask3d, k) if mask3d is not None else None
        masks.append(to_sitk_mask_like(s2d, m2d))
    return masks

def n4_slice_bias(slice_img, slice_mask, shrink_factor=2, conv=[50,50,30,20], bspline_mm=50.0, fitting_levels=4):
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    corrector.SetMaximumNumberOfIterations(conv)
    corrector.SetConvergenceThreshold(1e-7)
    corrector.SetSplineOrder(3)
    if hasattr(corrector, "SetNumberOfFittingLevels"):
        corrector.SetNumberOfFittingLevels(int(fitting_levels))
    if hasattr(corrector, "SetNumberOfControlPoints"):
        size = slice_img.GetSize()
        spacing = slice_img.GetSpacing()
        extent_mm = (size[0]*spacing[0], size[1]*spacing[1])
        nx = max(4, int(round(extent_mm[0]/bspline_mm)))
        ny = max(4, int(round(extent_mm[1]/bspline_mm)))
        corrector.SetNumberOfControlPoints([nx, ny])

    shrink = [max(1, int(shrink_factor)), max(1, int(shrink_factor))]
    sim   = sitk.Shrink(slice_img, shrink)
    smask = sitk.Shrink(slice_mask, shrink)
    sim   = sitk.Cast(sim, sitk.sitkFloat32)

    _ = corrector.Execute(sim, smask)
    log_bias = corrector.GetLogBiasFieldAsImage(slice_img)
    return sitk.Cast(log_bias, sitk.sitkFloat32)

def compute_biasfield_per_slice(img3d, mask3d=None, **n4kw):
    depth = img3d.GetDepth()
    masks2d = per_slice_mask(img3d, mask3d)
    log_slices = []
    for k in range(depth):
        s2d = extract_slice_2d(img3d, k)
        logb = n4_slice_bias(s2d, masks2d[k], **n4kw)
        log_slices.append(logb)
    return stack_slices_to_3d(log_slices, img3d)

def bias_stats_core(log_bias_3d, mask3d):
    arr = sitk.GetArrayFromImage(log_bias_3d)  # z,y,x
    msk = sitk.GetArrayFromImage(mask3d).astype(bool)
    vals = arr[msk]
    if vals.size == 0:
        return {"n":0,"mad":np.nan,"iqr_half":np.nan}
    q1, med, q3 = np.percentile(vals, [25,50,75])
    mad = float(np.median(np.abs(vals - med)))
    iqr_half = float((q3 - q1)/2.0)
    return {"n": int(vals.size), "mad": mad, "iqr_half": iqr_half}

def slice_medians(logB, mask):
    arr = sitk.GetArrayFromImage(logB); m = sitk.GetArrayFromImage(mask).astype(bool)
    meds = [float(np.median(arr[z][m[z]])) for z in range(arr.shape[0]) if m[z].any()]
    return meds

def slice_drift_percent(logB, mask):
    to_pct = lambda x: 100.0*(np.exp(x)-1.0)
    meds = slice_medians(logB, mask)
    meds_pct = [to_pct(x) for x in meds]
    if not meds_pct:
        return meds_pct, np.nan, np.nan
    return meds_pct, float(max(meds_pct)-min(meds_pct)), float(np.std(meds_pct))

def pct_above(th, logB, mask):
    a = sitk.GetArrayFromImage(logB); m = sitk.GetArrayFromImage(mask).astype(bool)
    v = np.abs(a[m]); 
    return 100.0 * np.mean(v > th) if v.size else np.nan

def to_pct(x):  # log -> percent
    return 100.0*(np.exp(x)-1.0)

# ----------------- Main -----------------
def main (VOL_A_NAME, VOL_B_NAME, MASK_A_NAME, MASK_B_NAME, OUTPUT_PREFIX):
    imgA_sitk, nodeA = get_sitk_image(VOL_A_NAME)
    imgB_sitk, nodeB = get_sitk_image(VOL_B_NAME)

    maskA_sitk = None
    maskB_sitk = None
    if MASK_A_NAME:
        maskA_sitk, _ = seg_to_mask_for_reference(MASK_A_NAME, VOL_A_NAME)
    if MASK_B_NAME:
        maskB_sitk, _ = seg_to_mask_for_reference(MASK_B_NAME, VOL_B_NAME)

    def volume_mask(im):
        sm = sitk.CurvatureFlow(im, timeStep=0.01, numberOfIterations=3)
        m = sitk.OtsuThreshold(sm, 0, 1)
        return sitk.Cast(m, sitk.sitkUInt8)

    if maskA_sitk is None: maskA_sitk = volume_mask(imgA_sitk)
    if maskB_sitk is None: maskB_sitk = volume_mask(imgB_sitk)

    # Compute N4 log-bias fields (per-slice)
    logB_A = compute_biasfield_per_slice(imgA_sitk, maskA_sitk, bspline_mm=50.0, shrink_factor=2, conv=[50,50,30,20])
    logB_B = compute_biasfield_per_slice(imgB_sitk, maskB_sitk, bspline_mm=50.0, shrink_factor=2, conv=[50,50,30,20])

    # --- Core stats only ---
    statsA = bias_stats_core(logB_A, maskA_sitk)
    statsB = bias_stats_core(logB_B, maskB_sitk)

    # convert dispersion to percent
    A_MAD_pct = to_pct(statsA["mad"])
    B_MAD_pct = to_pct(statsB["mad"])
    A_IQRhalf_pct = to_pct(statsA["iqr_half"])
    B_IQRhalf_pct = to_pct(statsB["iqr_half"])

    # proportions above thresholds
    A_p10 = pct_above(0.1, logB_A, maskA_sitk); B_p10 = pct_above(0.1, logB_B, maskB_sitk)
    A_p22 = pct_above(0.2, logB_A, maskA_sitk); B_p22 = pct_above(0.2, logB_B, maskB_sitk)

    # slice-wise drift (percent)
    A_slice_pct, A_range_pct, A_sd_pct = slice_drift_percent(logB_A, maskA_sitk)
    B_slice_pct, B_range_pct, B_sd_pct = slice_drift_percent(logB_B, maskB_sitk)

    # ------------- PRINT -------------
    print("\n=== N4 LOG-BIAS: Essential Stats (ROI) ===")
    print(f"Voxels:  COR={statsA['n']},  SAG={statsB['n']}")

    print("\nTypical voxel deviation (MAD, percent):")
    print(f"  COR ±{A_MAD_pct:.1f}%   |   SAG ±{B_MAD_pct:.1f}%")

    print("\nMiddle-50% spread (IQR half-range, percent):")
    print(f"  COR ±{A_IQRhalf_pct:.1f}%   |   SAG ±{B_IQRhalf_pct:.1f}%")

    print("\nProportion of voxels above strong-bias thresholds:")
    print(f"  |logB|>0.1 (~±10%):  COR {A_p10:.1f}%   |   SAG {B_p10:.1f}%")
    print(f"  |logB|>0.2 (~±22%):  COR {A_p22:.1f}%   |   SAG {B_p22:.1f}%")

    print("\nSlice-wise median bias (percent) and drift:")
    print(f"  COR slices (%): {np.round(A_slice_pct,1)}  |  range={A_range_pct:.1f}%, SD={A_sd_pct:.1f}%")
    print(f"  SAG slices (%): {np.round(B_slice_pct,1)}  |  range={B_range_pct:.1f}%, SD={B_sd_pct:.1f}%")

    # (Optional) push bias fields for visualization — keep, but not required for stats.
    outA = push_sitk_image(logB_A, f"{OUTPUT_PREFIX}_LogBias_A", ref_node=nodeA)
    outB = push_sitk_image(logB_B, f"{OUTPUT_PREFIX}_LogBias_B", ref_node=nodeB)
    print(f"\nPushed bias fields: {outA.GetName()}, {outB.GetName()} (log-scale).")

# ----------------- Inputs & call -----------------
try:
    volumeA
except NameError:
    volumeA = None
try:
    volumeB
except NameError:
    volumeB = None
try:
    maskA
except NameError:
    maskA = None
try:
    maskB
except NameError:
    maskB = None
try:
    outputPrefix
except NameError:
    outputPrefix = "N4Bias"

if None in (volumeA, volumeB):
    print("Error: Missing one or more inputs.")
    print("Please define 'volumeA' and 'volumeB' before executing the script.")
else:
    main(volumeA, volumeB, maskA, maskB, outputPrefix)
