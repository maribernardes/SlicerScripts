import os
import slicer
import vtk
import numpy as np
import sitkUtils

 
"""
# Define the script path
scriptPath = "/home/mariana/SlicerScripts/ExtractSequences/CreateSequencesFromVolumes.py"
inputPath = 

# Define the variable to pass
script_globals = {'inputPath': "/home/mariana/Experiments/2025-08-21_Pig2/out-nrrd-4", 'baseName':'BEAT_interactive_jhu_tracking', 'seriesNumber':68000, 'startFrame':1, 'endFrame':27}

# Execute the script with the provided globals
exec(open(scriptPath, encoding='utf-8').read(), script_globals)

"""

def getOrientation(volumeNode, tol=1e-3):
    """
    Return 'AX', 'COR', 'SAG', or 'Unknown' based on the IJK→RAS direction matrix,
    ignoring sign (so flips are OK).
    """
    if volumeNode is None:
        return "Unknown"

    m = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASDirectionMatrix(m)
    D = np.array([[m.GetElement(r, c) for c in range(3)] for r in range(3)])

    # Normalize columns (guard against tiny rounding)
    for c in range(3):
        n = np.linalg.norm(D[:, c])
        if n > 0:
            D[:, c] = D[:, c] / n

    # Map each column to the closest RAS axis by absolute value
    # R=(1,0,0), A=(0,1,0), S=(0,0,1)
    axis_idx = np.argmax(np.abs(D), axis=0)  # which basis axis each column aligns to
    axis_mag = np.take_along_axis(np.abs(D), axis_idx[np.newaxis, :], axis=0).flatten()

    # Ensure each column is near a unit axis
    if np.any(np.abs(axis_mag - 1.0) > tol):
        return "Unknown"

    # axis_idx values: 0=R, 1=A, 2=S for columns [I, J, K]
    # Patterns (ignoring sign):
    # AX: I→R(0), J→A(1), K→S(2)  -> (0,1,2)
    # COR: I→R(0), J→S(2), K→A(1) -> (0,2,1)
    # SAG: I→A(1), J→S(2), K→R(0) -> (1,2,0)
    pattern = tuple(axis_idx.tolist())
    if pattern == (0, 1, 2):
        return "AX"
    elif pattern == (0, 2, 1):
        return "COR"
    elif pattern == (1, 2, 0):
        return "SAG"
    else:
        return "Unknown"
    

def create_sequences_from_volumes(base_name: str, series_number: int, start_frame: int = 1, end_frame: int = 1):
    """
    Creates an image sequence from volume nodes named as follows:
        Thousand digits: sequence series number
        Hundreds digits: frame number 
        imageOrientationPatient: 1 = SAG / 2 = COR
        Ex: 16025: BEAT_interactive_jhu_tracking - imageOrientationPatient 1
            Series: 16000
            Frame #: 025
    """

    # Get the sequence node
    sag_sequence = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", f"{series_number}: {base_name}_SAG")
    cor_sequence = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", f"{series_number}: {base_name}_COR")
    for i in range(start_frame, end_frame+1):
        print("Processing frame #", str(i))
        volume_name = str(series_number+i) + ': ' + base_name + ' - imageOrientationPatient '
        volume_node_1 = slicer.util.getFirstNodeByClassByName('vtkMRMLScalarVolumeNode', volume_name + '1')
        volume_node_2 = slicer.util.getFirstNodeByClassByName('vtkMRMLScalarVolumeNode', volume_name + '2')
        if not volume_node_1 or not isinstance(volume_node_1, slicer.vtkMRMLScalarVolumeNode):
            print(f"Error: No volume node named '{volume_name} 1' found.")
            return
        if not volume_node_2 or not isinstance(volume_node_2, slicer.vtkMRMLScalarVolumeNode):
            print(f"Error: No volume node named '{volume_name} 2' found.")
            return
        # Define who is SAG and who is COR:
        print(getOrientation(volume_node_1))
        print(getOrientation(volume_node_2))
        if getOrientation(volume_node_1) == 'COR':
            cor_node = volume_node_1
            sag_node = volume_node_2
        else:
            cor_node = volume_node_2
            sag_node = volume_node_1
        # Add to the correct sequence
        num_frame = i-start_frame+1
        sag_sequence.SetDataNodeAtValue(sag_node, str(num_frame))
        cor_sequence.SetDataNodeAtValue(cor_node, str(num_frame))

    print(f"Successfully created sequences "+ f"{series_number}: {base_name}_SAG and _COR")

# Check if 'sequenceName' is defined in the global namespace
try:
    baseName
except NameError:
    baseName = None
try:
    seriesNumber
except NameError:
    seriesNumber = None
try:
    startFrame
except NameError:
    startFrame = None
try:
    endFrame
except NameError:
    endFrame = None

if None in (baseName, seriesNumber, startFrame, endFrame):  
    print("Error: Missing 'baseName', 'seriesNumber', 'startFrame'  or 'endFrames'. Please define them before executing the script.")
else:
    create_sequences_from_volumes(base_name=baseName, series_number=seriesNumber, start_frame=startFrame, end_frame=endFrame)
