import os
import slicer
import vtk
import numpy as np

 
"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/ExtractSequences/CreateVolumesFromSequence.py"

# Define the variable to pass
# invertStack = True for SAG / False for COR
script_globals = {'sequenceName': '27: 2D BIPLANE_COR', 'invertStack': False}
script_globals = {'sequenceName': '27: 2D BIPLANE_SAG', 'invertStack': True}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)

"""

def create_volumes_from_sequence(sequence_node_name: str, invert_stack: bool = False, slice_number: int = 3):
    """
    Extracts groups of frames from a vtkMRMLSequenceNode and creates a 3D volume for each group,
    ensuring spatial orientation and position match the middle slice.

    :param sequence_node_name: Name of the sequence node in Slicer.
    :param slice_number: Number of slices per 3D volume.
    """

    # Get the sequence node
    sequence_node = slicer.util.getFirstNodeByClassByName('vtkMRMLSequenceNode', sequence_node_name)
    if not sequence_node or not isinstance(sequence_node, slicer.vtkMRMLSequenceNode):
        print(f"Error: No sequence node named '{sequence_node_name}' found.")
        return
    num_frames = sequence_node.GetNumberOfDataNodes()
    if num_frames < slice_number:
        print("Not enough frames to create a 3D volume.")
        return
    num_volumes = num_frames // slice_number  # Number of volumes we can extract
    print(f"Reconstructing {num_volumes} total 3D frames.")

    # Create a new sequence node to store 3D volumes
    new_sequence_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", f"{sequence_node_name}_3DSequence")

    for i in range(num_volumes):
        slice_arrays = []  # Store numpy arrays
        reference_frame = None  # Store reference for spatial metadata

        # Extract slice_number frames from the sequence
        for j in range(slice_number):
            frame_value = str(i * slice_number + j)
            frame_node = sequence_node.GetNthDataNode(i * slice_number + j)
            if frame_node:
                # Convert frame node to numpy array (without creating an intermediate Slicer node)
                slice_array = slicer.util.arrayFromVolume(frame_node)
                if slice_array is None:
                    print(f"Warning: Failed to extract frame {frame_value}. Skipping.")
                    continue  # Skip this slice if data extraction failed
                slice_arrays.append(slice_array.squeeze(axis=0))  # Ensure (256, 256)
                # Select spatial reference                
                if invert_stack is True:
                    if j == 0: # Use the first slice (slice 0)  as the reference for position
                        reference_frame = frame_node  
                else:
                    if j == 2: # Use the last slice (slice 2)  as the reference for position
                        reference_frame = frame_node  

        # Ensure we have enough slices
        if len(slice_arrays) != slice_number:
            print(f"Skipping volume {i+1} due to missing slices.")
            continue

        # Stack slices correctly in RAS coordinate order
        if invert_stack is True:
            stacked_array = np.stack(slice_arrays[::-1], axis=0)  # Reverse order so first frame
        else:
            stacked_array = np.stack(slice_arrays, axis=0)  # Reverse order so first frame is first slice

        # Flip images if necessary to match Slicer’s RAS orientation
        stacked_array = np.flip(stacked_array, axis=0)  # Flip Superior-Inferior (Z-axis)

        # Create a new 3D volume
        new_volume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", f"Volume_{i+1}")
        slicer.util.updateVolumeFromArray(new_volume, stacked_array)

        # Copy spacing from the reference slice
        spacing = reference_frame.GetSpacing()
        new_volume.SetSpacing(spacing[0], spacing[1], spacing[2])

        # Copy the orientation (direction matrix)
        direction_matrix = vtk.vtkMatrix4x4()
        reference_frame.GetIJKToRASDirectionMatrix(direction_matrix)
        new_volume.SetIJKToRASDirectionMatrix(direction_matrix)

        # Copy the origin (translation in RAS space) from the middle slice
        origin = reference_frame.GetOrigin()
        new_volume.SetOrigin(origin)  # Apply the correct position

        # Copy the transform (position in 3D space)
        transform_id = reference_frame.GetTransformNodeID()
        if transform_id:
            parent_transform = slicer.mrmlScene.GetNodeByID(transform_id)
            if parent_transform:
                new_volume.SetAndObserveTransformNodeID(parent_transform.GetID())  # Apply the transform

        # Add new 3D volume to the sequence node
        new_sequence_node.SetDataNodeAtValue(new_volume, str(i))  # Use index as sequence frame value
        print(f"Frame {i + 1} with shape {stacked_array.shape}, origin {new_volume.GetOrigin()} and spacing {new_volume.GetSpacing()}")

        # Remove the temporary 3D volume from the scene after adding it to the sequence
        slicer.mrmlScene.RemoveNode(new_volume)

    print(f"Successfully created {num_volumes} 3D volumes and stored them in a new sequence node: {new_sequence_node.GetName()}")


# Check if 'sequenceName' is defined in the global namespace
try:
    sequenceName
except NameError:
    sequenceName = None
try:
    invertStack
except NameError:
    invertStack = None

if None in (sequenceName, invertStack):  
    print("Error: Missing 'sequenceName' or 'invertStack'. Please define it before executing the script.")
else:
    create_volumes_from_sequence(sequence_node_name=sequenceName, invert_stack=invertStack, slice_number=3)
