# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/ExtractSequences/SplitSequences.py"

# Define the variable to pass
script_globals = {'sequenceName': '13: MR 2D BIPLANE GRE TE4', 'blockSize': 3, 'CORFirst': False}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)
"""

import slicer

def split_sequence_into_two(sequence_node_name: str, block_size: int = 1, cor_first: bool = True):
    """
    Splits a sequence node into two sequences, alternating every 'block_size' frames.

    :param sequence_node_name: Name of the original sequence node.
    :param block_size: Number of consecutive frames to assign to each sequence before switching.
    :param cor_first: If True, the first sequence will be labeled _COR, otherwise _SAG.
    """

    if block_size < 1:
        print("Error: block_size must be at least 1.")
        return

    sequence_node = slicer.util.getFirstNodeByClassByName("vtkMRMLSequenceNode", sequence_node_name)
    if not sequence_node or not isinstance(sequence_node, slicer.vtkMRMLSequenceNode):
        print(f"Error: No sequence node named '{sequence_node_name}' found.")
        return

    num_frames = sequence_node.GetNumberOfDataNodes()
    if num_frames < (2*block_size):
        print("Not enough frames to split into two sequences.")
        return

    # Postfix and naming
    postfix_a = "_COR" if cor_first else "_SAG"
    postfix_b = "_SAG" if cor_first else "_COR"

    sequence_a = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", f"{sequence_node_name}{postfix_a}")
    sequence_b = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", f"{sequence_node_name}{postfix_b}")

    print(f"Splitting '{sequence_node_name}' into blocks of {block_size} frames.")
    print(f"- Sequence A: '{sequence_a.GetName()}'")
    print(f"- Sequence B: '{sequence_b.GetName()}'")

    for i in range(num_frames):
        frame_node = sequence_node.GetNthDataNode(i)
        if not frame_node:
            continue

        block_index = i // block_size
        target_sequence = sequence_a if block_index % 2 == 0 else sequence_b
        target_sequence.SetDataNodeAtValue(frame_node, str(i))

    print(f"Done. Created sequences: '{sequence_a.GetName()}' and '{sequence_b.GetName()}'.")

# Check if 'sequenceName' 'blockSize' and 'CORFirst' are defined in the global namespace
try:
    sequenceName
except NameError:
    sequenceName = None
try:
    blockSize
except NameError:
    blockSize = 1  # default to alternating every frame
try:
    CORFirst
except NameError:
    CORFirst = True # default to COR first

if sequenceName is None:
    print("Error: Missing 'sequenceName'. Please define it before executing the script.")
else:
    split_sequence_into_two(sequence_node_name=sequenceName, block_size=blockSize, cor_first=CORFirst)