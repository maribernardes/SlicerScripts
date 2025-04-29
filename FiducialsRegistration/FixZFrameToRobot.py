# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/FiducialsRegistration/FixZFrameToRobot.py"

# Define the variable to pass
#script_globals = {'worldPoints': 'W', 'outputName': 'P4', 'p1': (2784,849), 'p2': (2165,3318), 'p3': (889,1109), 'p4': (2194,2283)}

# Execute the script with the provided globals
#exec(open(filePath, encoding='utf-8').read(), script_globals)
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

    # Check original ZFrameToRobot (From URDF definition)
    mat_ZFrameToRobot_OG= vtk.vtkMatrix4x4()
    mat_RobotToZFrame_OG = vtk.vtkMatrix4x4()
    mat_ZFrameToRobot_OG.SetElement(0,0,-1.0); mat_ZFrameToRobot_OG.SetElement(0,1,0.0); mat_ZFrameToRobot_OG.SetElement(0,2,0.0)
    mat_ZFrameToRobot_OG.SetElement(1,0,0.0); mat_ZFrameToRobot_OG.SetElement(1,1,1.0); mat_ZFrameToRobot_OG.SetElement(1,2,0.0); 
    mat_ZFrameToRobot_OG.SetElement(2,0,0.0); mat_ZFrameToRobot_OG.SetElement(2,1,0.0); mat_ZFrameToRobot_OG.SetElement(2,2,-1.0); 
    mat_ZFrameToRobot_OG.SetElement(3,0,0.0); mat_ZFrameToRobot_OG.SetElement(3,1,0.0); mat_ZFrameToRobot_OG.SetElement(3,2,0.0); 
    mat_ZFrameToRobot_OG.SetElement(0,3,0.0); mat_ZFrameToRobot_OG.SetElement(1,3,98.0); mat_ZFrameToRobot_OG.SetElement(2,3,-128.3); mat_ZFrameToRobot_OG.SetElement(3,3,1.0)
    vtk.vtkMatrix4x4.Invert(mat_ZFrameToRobot_OG, mat_RobotToZFrame_OG)
    
    # Obtain original RobotToScanner
    mat_RobotToScanner_OG = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(mat_ZFrameToScanner, mat_RobotToZFrame_OG, mat_RobotToScanner_OG)
    nodeRobotToScanner_OG = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','RobotToScanner_OG')
    if nodeRobotToScanner_OG is None:
        nodeRobotToScanner_OG = slicer.vtkMRMLLinearTransformNode()
        nodeRobotToScanner_OG.SetName('RobotToScanner_OG')
        slicer.mrmlScene.AddNode(nodeRobotToScanner_OG)
    nodeRobotToScanner_OG.SetMatrixTransformToParent(mat_RobotToScanner_OG)

    # Get RobotToScanner (Result from Fiducial Registration)
    mat_RobotToScanner_EXP= vtk.vtkMatrix4x4()
    node_RobotToScanner = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','RobotToScanner_EXP')
    node_RobotToScanner.GetMatrixTransformToParent(mat_RobotToScanner_EXP)

    # Calculate the corrected ZFrameToRobot from experimental points
    mat_RobotToZFrame_EXP = vtk.vtkMatrix4x4()
    mat_ZFrameToRobot_EXP = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(mat_ScannerToZFrame, mat_RobotToScanner_EXP, mat_RobotToZFrame_EXP)
    vtk.vtkMatrix4x4.Invert(mat_RobotToZFrame_EXP, mat_ZFrameToRobot_EXP)
    
    # Check with new RobotToScanner (verify with world_listener)
    mat_RobotToScanner_NEW= vtk.vtkMatrix4x4()
    mat_ScannerToRobot_NEW= vtk.vtkMatrix4x4()
    mat_RobotToZFrame_EXP = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Invert(mat_ZFrameToRobot_EXP, mat_RobotToZFrame_EXP)
    vtk.vtkMatrix4x4.Multiply4x4(mat_ZFrameToScanner, mat_RobotToZFrame_EXP, mat_RobotToScanner_NEW)
    vtk.vtkMatrix4x4.Invert(mat_RobotToScanner_NEW, mat_ScannerToRobot_NEW)

    # Push to node
    nodeRobotToScanner_NEW = slicer.util.getFirstNodeByClassByName('vtkMRMLLinearTransformNode','RobotToScanner_NEW')
    if nodeRobotToScanner_NEW is None:
        nodeRobotToScanner_NEW = slicer.vtkMRMLLinearTransformNode()
        nodeRobotToScanner_NEW.SetName('RobotToScanner_NEW')
        slicer.mrmlScene.AddNode(nodeRobotToScanner_NEW)
    nodeRobotToScanner_NEW.SetMatrixTransformToParent(mat_RobotToScanner_NEW)
    

    printVtkMatrix4x4(mat_ZFrameToRobot_OG, 'ZFrameToRobot_OG = ')
    printVtkMatrix4x4(mat_ZFrameToRobot_EXP, 'ZFrameToRobot_EXP= ')
    print('_______________')
    printVtkMatrix4x4(mat_RobotToScanner_EXP, 'RobotToScanner_EXP= ')
    printVtkMatrix4x4(mat_RobotToScanner_NEW, 'RobotToScanner_NEW= ')

main()