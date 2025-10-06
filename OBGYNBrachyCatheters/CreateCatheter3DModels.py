# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/OBGYNBrachyCatheters/CreateCatheter3DModels.py"

# Define the variable to pass
script_globals = {'N': 8, 'prefix': 'T', 'radius_mm': 0.6}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)

"""


import slicer, vtk

def build_tube_model_from_fiducials(markupsNode, modelName,
                                    radius_mm=0.6, sides=16,
                                    color=(1.0, 0.2, 0.2), opacity=1.0,
                                    show_in_slice=True):
    """Create a tube surface model from a Markups fiducial node."""
    n = markupsNode.GetNumberOfControlPoints()
    if n < 2:
        print(f"[WARN] {modelName}: need at least 2 points, got {n}. Skipping.")
        return None

    # Polyline from points
    pts = vtk.vtkPoints()
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(n)
    for i in range(n):
        p = [0.0, 0.0, 0.0]
        markupsNode.GetNthControlPointPositionWorld(i, p)
        pid = pts.InsertNextPoint(p)
        lines.InsertCellPoint(pid)

    poly = vtk.vtkPolyData()
    poly.SetPoints(pts)
    poly.SetLines(lines)

    # Optional smoothing/resampling (comment out if you want exact segments)
    spline = vtk.vtkSplineFilter()
    spline.SetInputData(poly)
    spline.SetSubdivideToLength()
    spline.SetLength(0.5)  # resample every 0.5 mm; adjust as needed
    spline.Update()

    # Tube surface
    tube = vtk.vtkTubeFilter()
    tube.SetInputConnection(spline.GetOutputPort())
    tube.SetRadius(radius_mm)     # catheter radius in mm
    tube.SetNumberOfSides(sides)  # roundness
    tube.SetCapping(True)
    tube.Update()

    # Model node in scene
    modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', modelName)
    modelNode.SetAndObservePolyData(tube.GetOutput())
    if not modelNode.GetDisplayNode():
        modelNode.CreateDefaultDisplayNodes()
    d = modelNode.GetDisplayNode()
    d.SetColor(*color)
    d.SetOpacity(opacity)
    d.SetVisibility(True)
    # Show in slice views as intersection (optional)
    if show_in_slice:
        d.SetVisibility2D(True)

    print(f"[OK] Created model '{modelName}' with {n} points, radius {radius_mm} mm.")
    return modelNode

def main(N, prefix='C', radius_mm=0.6):
    """Find Markups nodes named C1..CN and create tube models named C1_model..CN_model."""
    for i in range(1, int(N) + 1):
        name = f"{str(prefix)}{i}"
        try:
            markupsNode = slicer.util.getNode(name)
            if markupsNode.GetClassName() != 'vtkMRMLMarkupsFiducialNode':
                print(f"[WARN] {name} is not a fiducial list. Skipping.")
                continue
        except Exception:
            print(f"[WARN] Markups node '{name}' not found. Skipping.")
            continue

        modelName = f"{name}_model"
        build_tube_model_from_fiducials(markupsNode, modelName, radius_mm=radius_mm)


# Check if 'N', 'prefix' and 'radius_mm' is defined in the global namespace
try:
    N
except NameError:
    N = None
    
try:
    prefix
except NameError:
    prefix = 'C'
    
try:
    radius_mm
except NameError:
    radius_mm = 0.6

if N is None:
    # Handle the case where inputs are not provided
    print("Error: Missing one input.")
    print("Please define 'N' before executing the script.")
else:
    # Call the main function with the inputs
    main(N, prefix, radius_mm)
