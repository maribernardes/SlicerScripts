# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/Experiments/2024-12-20_Phantom Test/ExtractSequences/CombineSequences.py"

# Define the variable to pass
script_globals = {
    'sequenceAName': '46: MR BEAT_NEEDLE BIPLANE_COR',
    'sequenceBName': '46: MR BEAT_NEEDLE BIPLANE_SAG',
    'outputSequenceName': '46: MR BEAT_NEEDLE BIPLANE_Combined'
}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)
"""

import slicer

def combine_sequences(sequence_A_name: str, sequence_B_name: str, output_sequence_name: str):
    """
    Combines two sequence nodes by interleaving their frames, preserving spatial information.
    The output is a new sequence node added to the Slicer scene.

    :param sequence_A_name: Name of the first sequence node.
    :param sequence_B_name: Name of the second sequence node.
    :param output_sequence_name: Name of the combined output sequence.
    """
    # Get the input sequences
    sequence_A = slicer.util.getFirstNodeByClassByName("vtkMRMLSequenceNode", sequence_A_name)
    sequence_B = slicer.util.getFirstNodeByClassByName("vtkMRMLSequenceNode", sequence_B_name)

    if not sequence_A or not sequence_B:
        print(f"Error: One or both sequence nodes ('{sequence_A_name}', '{sequence_B_name}') were not found.")
        return

    num_frames_A = sequence_A.GetNumberOfDataNodes()
    num_frames_B = sequence_B.GetNumberOfDataNodes()
    max_frames = max(num_frames_A, num_frames_B)

    if max_frames == 0:
        print("Error: Both sequences are empty.")
        return

    # Create the new interleaved sequence node
    combined_sequence = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSequenceNode", output_sequence_name)
    
    print(f"Combining sequences '{sequence_A_name}' and '{sequence_B_name}' into '{output_sequence_name}'.")

    # Interleave frames from both sequences
    for i in range(max_frames):
        if i < num_frames_A:
            frame_A = sequence_A.GetNthDataNode(i)
            if frame_A:
                combined_sequence.SetDataNodeAtValue(frame_A, str(2 * i))

        if i < num_frames_B:
            frame_B = sequence_B.GetNthDataNode(i)
            if frame_B:
                combined_sequence.SetDataNodeAtValue(frame_B, str(2 * i + 1))

    print(f"Successfully created combined sequence: '{combined_sequence.GetName()}'.")


# **Execution Part**
try:
    sequenceAName
    sequenceBName
    outputSequenceName
except NameError:
    sequenceAName = None
    sequenceBName = None
    outputSequenceName = None

if None in (sequenceAName, sequenceBName, outputSequenceName):
    print("Error: Missing one or more input sequence names.")
    print("Please define 'sequenceAName', 'sequenceBName', and 'outputSequenceName' before executing the script.")
else:
    combine_sequences(sequence_A_name=sequenceAName, sequence_B_name=sequenceBName, output_sequence_name=outputSequenceName)
