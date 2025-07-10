# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/FiducialsRegistration/GetPuncturePoint.py"

# Define the variable to pass
script_globals = {'worldPoints': 'WaxPaperPoints', 'outputName': 'P6w', 'p1': (3140,2106), 'p2': (3687,4601), 'p3': (1522,3227), 'p4': (2748,3343)}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)

"""

import numpy as np
import slicer


def create_or_update_markup(outputName, P4):
    # Check if a markup node with the given name exists
    markupNode = None
    nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
    for i in range(nodes.GetNumberOfItems()):
        node = nodes.GetItemAsObject(i)
        if node.GetName() == outputName:
            markupNode = node
            break

    if not markupNode:
        # Create a new markup node with outputName
        markupNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', outputName)
        print(f"Created new markup node with name '{outputName}'.")
    else:
        # Use the existing markup node
        pass

    # Remove all current control points
    markupNode.RemoveAllControlPoints()

    # Add a single control point
    pointIndex = markupNode.AddControlPoint(P4)
    markupNode.SetNthControlPointLabel(pointIndex, outputName)
    
    
def calculate_4th_point_3d(P1, P2, P3, p1, p2, p3, p4):
    """
    Calculate the 3D coordinates of the 4th point on a plane given 3 known 3D points
    and their corresponding image points.

    Parameters:
        P1, P2, P3: Arrays or lists representing the 3D coordinates of the known points.
        p1, p2, p3: Arrays or lists representing the pixel coordinates of the known points.
        p4: Array or list representing the pixel coordinates of the 4th point.

    Returns:
        P4: Numpy array representing the 3D coordinates of the 4th point.
    """
    # Convert inputs to numpy arrays
    P1 = np.array(P1)
    P2 = np.array(P2)
    P3 = np.array(P3)
    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)
    p4 = np.array(p4)
    
    # Step 1: Define basis vectors on the plane
    u = P2 - P1
    v = P3 - P1
    
    # Step 2: Compute affine transformation parameters
    a3, b3 = p1  # a3 = u1, b3 = v1
    a1 = p2[0] - a3
    b1 = p2[1] - b3
    a2 = p3[0] - a3
    b2 = p3[1] - b3

    # Affine transformation matrix
    A = np.array([[a1, a2],
                  [b1, b2]])

    # Check if A is invertible
    if np.linalg.det(A) == 0:
        raise ValueError("The affine transformation matrix is singular and cannot be inverted.")
    
    # Step 3: Compute (s, t) for the 4th point
    u_prime = p4[0] - a3
    v_prime = p4[1] - b3
    uv_prime = np.array([u_prime, v_prime])
    
    # Solve for s and t
    st = np.linalg.solve(A, uv_prime)
    s4, t4 = st

    # Step 4: Compute the 3D coordinates of the 4th point
    P4 = P1 + s4 * u + t4 * v
    
    return P4

def main(worldPoints, outputName, p1, p2, p3, p4):
    # Your existing code that uses 'worldPoints'and 'pixelPoints'
    print(f"The worldPoints is: {worldPoints}")
    
    # Get the markup node from the scene
    worldNode = slicer.util.getNode(worldPoints)
    
    if not worldNode:
        print(f"worldPoints node named '{worldPoints}' was not found in the scene.")
    else:
        # Get the number of control points in the markup node
        nControlPoints = worldNode.GetNumberOfControlPoints()
        
        if nControlPoints != 3:
            print(f"Number of worldPoints should be 3 ({nControlPoints} found).") 
        else:       

            # Get the 3D coordinates
            P1 = [0.0, 0.0, 0.0]
            P2 = [0.0, 0.0, 0.0]
            P3 = [0.0, 0.0, 0.0]
            worldNode.GetNthControlPointPositionWorld(0, P1)
            worldNode.GetNthControlPointPositionWorld(1, P2)
            worldNode.GetNthControlPointPositionWorld(2, P3)

            # Compute the 4th point
            P4 = calculate_4th_point_3d(P1, P2, P3, p1, p2, p3, p4)

            print(f"Puncture Point:")
            print(P4)
            create_or_update_markup(outputName, P4)


# Check if 'worldPoints', óutputName, 'p1', 'p2', 'p3' and 'p4' are defined in the global namespace
try:
    worldPoints
except NameError:
    worldPoints = None
    
try:
    outputName
except NameError:
    outputName = None

try:
    p1
except NameError:
    p1 = None

try:
    p2
except NameError:
    p2 = None
        
try:
    p3
except NameError:
    p3 = None

try:
    p4
except NameError:
    p4 = None

if None in (worldPoints, outputName, p1, p2, p3, p4):
    # Handle the case where inputs are not provided
    print("Error: Missing one or more inputs.")
    print("Please define 'worldPoints', outputName, 'p1', 'p2', 'p3', and 'p4' before executing the script.")
else:
    # Call the main function with the inputs
    main(worldPoints, outputName, p1, p2, p3, p4)
