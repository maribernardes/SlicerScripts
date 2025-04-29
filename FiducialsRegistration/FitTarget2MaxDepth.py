# -*- coding: utf-8 -*-
 
"""
# Define the script path
filePath = "/Users/pl771/Devel/AI_Tracking_Experiment/FitTarget2MaxDepth.py"

# Define the variable to pass
script_globals = {'markupName': 'FiducialPoints', 'pointPrefix': 'C', 'targetName': 'target', 'x': -26.0, 'y': -17.0}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)

"""

import numpy as np
import sys
import slicer
import re

RING_OFFSET = 5  #5mm offset from fiducial to max insertion depth

def create_or_update_markup(targetName, x, y, z):

    # Check if a markup node with the given name exists
    markupNode = None
    nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
    for i in range(nodes.GetNumberOfItems()):
        node = nodes.GetItemAsObject(i)
        if node.GetName() == targetName:
            markupNode = node
            break

    if not markupNode:
        # Create a new markup node with a unique name
        uniqueName = slicer.mrmlScene.GenerateUniqueName(targetName)
        markupNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', uniqueName)
        print(f"Created new markup node with unique name '{uniqueName}'.")
    else:
        # Use the existing markup node
        pass

    # Remove all current control points
    markupNode.RemoveAllControlPoints()

    # Add a single control point with label 'target' at coordinates (x, y, z)
    pointIndex = markupNode.AddControlPoint([x, y, z])
    markupNode.SetNthControlPointLabel(pointIndex, 'target')

def offset_parallel_plane(A, B, C, D, offset_distance, direction='positive'):
    """
    Calculates the D coefficient for a plane parallel to the original plane,
    offset by a given distance.
    
    Parameters:
        A, B, C (float): Coefficients of the plane normal vector.
        D (float): Original plane's D coefficient.
        offset_distance (float): The distance to offset the plane.
        direction (str): 'positive' to offset in the direction of the normal vector,
                         'negative' to offset in the opposite direction.
    
    Returns:
        D_new (float): The D coefficient of the offset plane.
    """
    # Compute the norm of the normal vector
    normal_norm = np.sqrt(A**2 + B**2 + C**2)
    
    # Determine the sign based on the desired direction
    sign = 1 if direction == 'positive' else -1
    
    # Calculate the new D coefficient
    D_new = D + sign * offset_distance * normal_norm
    
    return D_new

    
def fit_plane_to_points(points):
    """
    Fits a plane to a set of 3D points using least squares.

    Parameters:
        points (array-like): An Nx3 array of XYZ coordinates.

    Returns:
        A, B, C, D (float): Coefficients of the plane equation Ax + By + Cz + D = 0.
    """
    # Ensure input is a NumPy array
    points = np.asarray(points)
    
    # Check if there are at least 3 points
    if points.shape[0] < 3:
        raise ValueError("At least three points are required to define a plane.")
    
    # Compute the centroid of the points
    centroid = points.mean(axis=0)
    
    # Center the points by subtracting the centroid
    centered_points = points - centroid
    
    # Compute the covariance matrix
    covariance_matrix = np.cov(centered_points, rowvar=False)
    
    # Perform eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    
    # The normal vector is the eigenvector corresponding to the smallest eigenvalue
    normal_vector = eigenvectors[:, np.argmin(eigenvalues)]
    
    # Extract the coefficients A, B, C from the normal vector
    A, B, C = normal_vector
    
    # Compute D using the plane equation and the centroid
    D = -np.dot(normal_vector, centroid)
    
    return A, B, C, D


def main(markupName, pointPrefix, targetName, x, y):
    # Your existing code that uses 'markupName', 'pointPrefix', 'targetName', 'x', and 'y'
    print(f"The markupName is: {markupName}")
    print(f"The pointPrefix is: {pointPrefix}")
    print(f"The targetName is: {targetName}")
    print(f"The x coordinate is: {x}")
    print(f"The y coordinate is: {y}")
    
    # Get the markup node from the scene
    markupNode = slicer.util.getNode(markupName)
    
    if not markupNode:
        print(f"Markup node named '{markupName}' was not found in the scene.")
    else:
        # Initialize a list to hold (i, position) tuples
        labeledPoints = []

        # Regular expression pattern to match labels 'prefix-1', 'prefix-2', ..., 'prefix-N'
        pattern = re.compile(r'^{}-(\d+)$'.format(re.escape(pointPrefix)))

        # Get the number of control points in the markup node
        nControlPoints = markupNode.GetNumberOfControlPoints()

        # Iterate over each control point
        for idx in range(nControlPoints):
            label = markupNode.GetNthControlPointLabel(idx)
            match = pattern.match(label)
            if match:
                # Extract the integer part 'i' from 'prefix-i'
                i = int(match.group(1))
                # Get the position in world coordinates (with transforms applied)
                pointWorld = [0.0, 0.0, 0.0]
                markupNode.GetNthControlPointPositionWorld(idx, pointWorld)
                # Append the tuple (i, position) to the list
                labeledPoints.append((i, pointWorld))
        
        # Get the number of labeled control points found
        numLabeledPoints = len(labeledPoints)
    
        if numLabeledPoints < 3:
            print(f"Only {numLabeledPoints} control points labeled 'prefix-i' were found (minimum 3 required).") 
        else:
            # Sort the list based on the integer 'i' extracted from the labels
            labeledPoints.sort(key=lambda x: x[0])

            # Extract positions into a NumPy array
            positions = [point for i, point in labeledPoints]
            pointsArray = np.array(positions)
            
            # Now 'pointsArray' contains the coordinates of the markup points
            # Calculate the plane parameters
            (A,B,C,D) = fit_plane_to_points(pointsArray)

            # Apply RING_OFFSET to plane
            D2 = offset_parallel_plane(A, B, C, D, RING_OFFSET)
            
            # Get z coordinate for offset plane            
            z = (-D2 -A*x -B*y)/C
            print(f"Z Coordinate:")
            print(z)
            create_or_update_markup(targetName, x, y, z)

# Check if 'markupName', 'pointPrefix', 'x', and 'y' are defined in the global namespace
try:
    markupName
except NameError:
    markupName = None

try:
    pointPrefix
except NameError:
    pointPrefix = None

try:
    targetName
except NameError:
    targetName = None
        
try:
    x
except NameError:
    x = None

try:
    y
except NameError:
    y = None

if None in (markupName, pointPrefix, targetName, x, y):
    # Handle the case where inputs are not provided
    print("Error: Missing one or more inputs.")
    print("Please define 'markupName', pointPrefix, 'targetName', 'x', and 'y' before executing the script.")
else:
    # Call the main function with the inputs
    main(markupName, pointPrefix, targetName, x, y)
