# -*- coding: utf-8 -*-
 
"""
# Define the script path
filePath = "/home/mrthermometry/SlicerScripts/SaveSliceAsPng.py"

# Define the variables to pass
script_globals = {'viewerName': 'Yellow', 'scriptPath': filePath}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)
"""

import os
import numpy as np
import slicer
import vtk
import re  # Import regex module
from PIL import Image

def get_subject_name(volume_node):
    """
    Get the subject (patient) name from a given volume node.
    
    Parameters:
        volume_node (vtkMRMLScalarVolumeNode): The volume node to find the subject for.
    
    Returns:
        str: The subject (patient) name if found, otherwise None.
    """
    # Ensure a valid volume node is provided
    if not volume_node or not volume_node.IsA("vtkMRMLScalarVolumeNode"):
        print("Error: Invalid volume node.")
        return None

    # Get the Subject Hierarchy Node
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    if not shNode:
        print("Error: No Subject Hierarchy found.")
        return None

    # Find the Scene Node ID dynamically
    scene_item_id = shNode.GetSceneItemID()
    # Find the corresponding Subject Hierarchy Item ID for the volume
    volume_item_id = shNode.GetItemByDataNode(volume_node)
    if volume_item_id == 0:
        print("Error: No hierarchy item found for the volume.")
        return None

    # Traverse up the hierarchy to find the subject (patient)
    current_item_id = volume_item_id
    subject_item_id = None

    while current_item_id != scene_item_id:  # Stop when reaching the Scene Node
        parent_item_id = shNode.GetItemParent(current_item_id)

        # If the next parent is the Scene, mark the current node as the Subject
        if parent_item_id == scene_item_id:
            subject_item_id = current_item_id
            break  # Stop searching
        
        # Move up to the next parent
        current_item_id = parent_item_id

    # Ensure the identified subject is actually different from the volume name
    if subject_item_id:
        subject_name = shNode.GetItemName(subject_item_id)

        if subject_name and subject_name != volume_node.GetName():
            print(f"Subject (patient) name for volume '{volume_node.GetName()}': {subject_name}")
            return subject_name

    print("No subject found in the hierarchy.")
    return None

def get_series_number(volume_node):
    """
    Extracts the series number from the volume node name.
    
    Parameters:
        volume_node (vtkMRMLScalarVolumeNode): The volume node to extract the series number from.
    
    Returns:
        int: The extracted series number if found, otherwise None.
    """
    # Ensure a valid volume node is provided
    if not volume_node or not volume_node.IsA("vtkMRMLScalarVolumeNode"):
        print("Error: Invalid volume node.")
        return None

    # Get the volume node name
    volume_name = volume_node.GetName()
    
    # Use regex to find the first continuous digit sequence before a non-numerical character
    match = re.match(r"^(\d+)\D", volume_name)

    if match:
        series_number = int(match.group(1))  # Extract the matched integer
        print(f"Series number for volume '{volume_name}': {series_number}")
        return series_number

    print(f"Error: Could not extract series number from '{volume_name}'.")
    return None


def get_slice_as_16bit_png(viewer_name, script_path):

    # Validate viewer name
    valid_viewers = {"Red", "Green", "Yellow"}
    if viewer_name not in valid_viewers:
        print(f"Error: Invalid viewer name '{viewer_name}'. Must be one of {valid_viewers}.")
        return
    
    # Get the slice logic for the desired viewer
    slice_logic = slicer.app.layoutManager().sliceWidget(viewer_name).sliceLogic()
    
    # Get the volume node displayed in the slice viewer
    volume_node = slice_logic.GetBackgroundLayer().GetVolumeNode()
    
    if not volume_node:
        print(f"No volume displayed in the {viewer_name} viewer.")
        return
    
    # Get the slice node
    slice_node = slice_logic.GetSliceNode()
    
    # Get the RAS-to-IJK transformation matrix
    volume_ras_to_ijk = vtk.vtkMatrix4x4()
    volume_node.GetRASToIJKMatrix(volume_ras_to_ijk)

    # Get the slice origin in RAS coordinates
    slice_origin_ras = slice_node.GetSliceToRAS().MultiplyPoint([0, 0, 0, 1])

    # Convert slice RAS to IJK
    slice_origin_ijk = [0, 0, 0, 1]
    volume_ras_to_ijk.MultiplyPoint(slice_origin_ras, slice_origin_ijk)
    
    # Extract the integer slice index
    slice_index = int(round(slice_origin_ijk[2]))  # Z-index for axial slices
    
    # Get image data from the scalar volume node
    image_data = volume_node.GetImageData()
    dims = image_data.GetDimensions()

    if slice_index < 0 or slice_index >= dims[2]:
        print("Error: Slice index out of range.")
        return

    # Convert VTK image data to NumPy array
    scalars = image_data.GetPointData().GetScalars()
    volume_array = vtk.util.numpy_support.vtk_to_numpy(scalars)
    
    # Reshape to 3D (Z, Y, X)
    volume_array = volume_array.reshape(dims[2], dims[1], dims[0])

    # Extract the 2D slice
    slice_array = volume_array[slice_index, :, :]
    
    # Normalize to 16-bit
    slice_array = np.interp(slice_array, (slice_array.min(), slice_array.max()), (0, 65535)).astype(np.uint16)
    
    # Convert to PIL Image and save as PNG
    image = Image.fromarray(slice_array)
    
    # Get the study name
    subject_name = get_subject_name(volume_node)
    series_number = get_series_number(volume_node)
    
    # Define the filename with the required suffix
    output_filename = f"MWALiver_2D_P_{subject_name}_{series_number}s{slice_index}.png"

    # Use the provided script path to determine the output folder
    script_dir = os.path.dirname(script_path)  # Get the folder where the script is stored
    output_path = os.path.join(script_dir, output_filename)

    image.save(output_path, format="PNG")
    print(f"Saved slice from {viewer_name} viewer (Slice {slice_index}) as 16-bit PNG: {output_path}")

# Check if 'viewerName' is defined in the global namespace
try:
    viewerName
except NameError:
    viewerName = None

# Check if 'scriptPath' is defined
try:
    scriptPath
except NameError:
    scriptPath = None

if viewerName is None:
    print("Error: Missing required input: 'viewerName'.")
    print("Please define 'viewerName' before executing the script.")
elif scriptPath is None:
    print("Error: Missing required input: 'scriptPath'. Make sure you pass it in script_globals.")
else:
    get_slice_as_16bit_png(viewer_name=viewerName, script_path=scriptPath)
    
