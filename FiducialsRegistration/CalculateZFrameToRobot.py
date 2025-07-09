# -*- coding: utf-8 -*-

"""
# Step 1: Select points in images using MarkupTools - List P
# Step 2: Enter the corresponding robot joints - List R
# Step 3: Use FiducialRegistration to obtain RobotToScanner transform
# Step 4: Use ZFrameRegistrationWithROI to obtain ZFrameToScanner transform
# Step 5: Run this script to calculate ZFrameToRobot

# Define the script path
filePath = "/home/mariana/SlicerScripts/FiducialsRegistration/CalculateZFrameToRobot.py"

exec(open(filePath, encoding='utf-8').read())

"""

import numpy as np
import vtk
import slicer



# Print vtkMatrix4x4 (for debugging)
def printVtkMatrix4x4(matrix4x4, name=''):
    print(name)
    for i in range(4):
        text=''
        for j in range(4):
            text = text + '  ' + str(matrix4x4.GetElement(i, j))
        print(text)

def main():

    # Get ZFrameToScanner (Result from ZFrameRegistrationWithROI)
    mat_ZFrameToScanner= vtk.vtkMatrix4x4()
    mat_ScannerToZFrame = vtk.vtkMatrix4x4()
    node_ZFrameToScanner = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','ZFrameToScanner')
    node_ZFrameToScanner.GetMatrixTransformToParent(mat_ZFrameToScanner)
    vtk.vtkMatrix4x4.Invert(mat_ZFrameToScanner, mat_ScannerToZFrame)

    # Get RobotToScanner (Result from Fiducial Registration)
    mat_RobotToScanner= vtk.vtkMatrix4x4()
    node_RobotToScanner = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','RobotToScanner')
    node_RobotToScanner.GetMatrixTransformToParent(mat_RobotToScanner)

    # Calculate the corrected ZFrameToRobot from experimental points
    mat_RobotToZFrame = vtk.vtkMatrix4x4()
    mat_ZFrameToRobot = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(mat_ScannerToZFrame, mat_RobotToScanner, mat_RobotToZFrame)
    vtk.vtkMatrix4x4.Invert(mat_RobotToZFrame, mat_ZFrameToRobot)
    
    # Push to node
    nodeZFrameToRobot = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','ZFrameToRobot')
    if nodeZFrameToRobot is None:
        nodeZFrameToRobot = slicer.vtkMRMLLinearTransformNode()
        nodeZFrameToRobot.SetName('ZFrameToRobot')
        slicer.mrmlScene.AddNode(nodeZFrameToRobot)
    nodeZFrameToRobot.SetMatrixTransformToParent(mat_ZFrameToRobot)
    printVtkMatrix4x4(mat_ZFrameToRobot, 'ZFrameToRobot = ')

main()
