# -*- coding: utf-8 -*-

"""
# Define the script path
filePath = "/home/mariana/SlicerScripts/OBGYNBrachyCatheters/LoadCatheters.py"

# Define the variable to pass
script_globals = {'start':1, 'N': 28, 'folder': '/home/mariana/SlicerScenes/2024-11-11_GynBrachyteraphy/catheter_csv'}
script_globals = {'start':3, 'N': 1, 'folder': '/home/mariana/Experiments/2025-08-21_Pig2/trajectories_csv', 'fileName':'R'}

# Execute the script with the provided globals
exec(open(filePath, encoding='utf-8').read(), script_globals)

"""

import os
import slicer
import vtk
import numpy as np

def import_catheters(start, N, folder, fileName):

    required_cols = ['label', 'r', 'a', 's']  # defined/selected/visible/locked are optional; we set them to 1 anyway
    
    for i in range(start, N + start):
        base = str(fileName) + str(i)
        csv_path = os.path.join(folder, f"{base}.csv")
        if not os.path.isfile(csv_path):
            print(f"[WARN] File not found: {csv_path} — skipping.")
            continue

        # Load CSV as a Table node
        try:
            tableNode = slicer.util.loadTable(csv_path)
        except Exception as e:
            print(f"[ERROR] Could not load {csv_path}: {e}")
            continue

        table = tableNode.GetTable()

        # Check required columns
        col_map = {}
        ok = True
        for name in required_cols:
            col = table.GetColumnByName(name)
            if col is None:
                print(f"[ERROR] {base}: Missing required column '{name}' in {csv_path}")
                ok = False
            else:
                col_map[name] = col
        if not ok:
            slicer.mrmlScene.RemoveNode(tableNode)
            continue

        nrows = table.GetNumberOfRows()
        if nrows == 0:
            print(f"[INFO] {base}: No rows in table, nothing to import.")
            slicer.mrmlScene.RemoveNode(tableNode)
            continue

        # Create or reuse Markups point list node named Ci
        markupsName = base
        try:
            markupsNode = slicer.util.getNode(markupsName)
            if markupsNode.GetClassName() != 'vtkMRMLMarkupsFiducialNode':
                markupsNode = None
        except Exception:
            markupsNode = None

        if markupsNode is None:
            markupsNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', markupsName)
        else:
            markupsNode.RemoveAllControlPoints()

        # Ensure display node exists and is visible
        if not markupsNode.GetDisplayNode():
            markupsNode.CreateDefaultDisplayNodes()
        displayNode = markupsNode.GetDisplayNode()
        # 3D view visibility
        displayNode.SetVisibility(True)
        # 2D slice visibility
        displayNode.SetVisibility2D(True)
        # Style
        displayNode.SetTextScale(0)   # hide text labels
        displayNode.SetGlyphScale(1)  # small glyphs

        # Add points
        rCol, aCol, sCol = col_map['r'], col_map['a'], col_map['s']
        lblCol = col_map['label']

        for row in range(nrows):
            try:
                r = float(rCol.GetValue(row))
                a = float(aCol.GetValue(row))
                s = float(sCol.GetValue(row))
            except Exception:
                # If the arrays are string-typed, fall back to converting via vtkVariant
                r = float(rCol.GetVariantValue(row).ToDouble())
                a = float(aCol.GetVariantValue(row).ToDouble())
                s = float(sCol.GetVariantValue(row).ToDouble())

            lbl = lblCol.GetValue(row) if hasattr(lblCol, 'GetValue') else lblCol.GetVariantValue(row).ToString()
            if lbl is None or str(lbl).strip() == '':
                lbl = f"{base}_{row+1}"
            else:
                lbl = str(lbl)

            idx = markupsNode.AddControlPoint(vtk.vtkVector3d(r, a, s))
            markupsNode.SetNthControlPointLabel(idx, lbl)
            # Set flags: defined/selected/visible/locked = 1
            markupsNode.SetNthControlPointSelected(idx, True)
            markupsNode.SetNthControlPointVisibility(idx, True)
            markupsNode.SetNthControlPointLocked(idx, True)

        # Done with table -> remove it
        slicer.mrmlScene.RemoveNode(tableNode)
        print(f"[OK] Imported {nrows} points into Markups node '{markupsName}' and deleted table.")


def main(start, N, folder, fileName):
    #  Load fileNamei.csv for i in [1..N], create/update Markups nodes named Ci with points
    # from the CSV table, then remove the temporary table nodes.
    print(f"Loading total of {N} catheters with input name '{fileName}'.")    
    import_catheters(start, N, folder, fileName)
    print("[DONE] Import finished.")


# Check if 'N' and 'folder' is defined in the global namespace
try:
    start
except NameError:
    start = 1

try:
    N
except NameError:
    N = None
    
try:
    folder
except NameError:
    folder = None
    
try:
    fileName
except NameError:
    fileName = 'C'

if None in (start, N, folder):
    # Handle the case where inputs are not provided
    print("Error: Missing one or more inputs.")
    print("Please define 'N' and 'folder' before executing the script.")
else:
    # Call the main function with the inputs
    main(start, N, folder, fileName)
