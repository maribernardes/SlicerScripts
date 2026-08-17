import slicer
import vtk
import time
from __main__ import qt

# STABLE VERSION
# Sequence playback with tracking initialization, cycle annotation,
# orthogonal viewer updates, valid 3-slice positioning, and enhanced
# NeedleTip display for video recording.

"""

# Example execution snippet:

filePath = "/home/mariana/SlicerScripts/SequencePlayback/PlaybackVideo.py"
filePath = "/Users/pl771/SlicerScripts/SequencePlayback/PlaybackVideo.py"

# firstFrame and lastFrame are two-element arrays:
# [frame for browserNameA, frame for browserNameB]
#
# viewerColorA and viewerColorB define which Slicer slice viewer
# corresponds to each browser. Valid values are:
# 'Red', 'Green', or 'Yellow'
#
# During playback, only the slice plane corresponding to the
# active browser is shown in the 3D view.

# T1

script_globals = {
    'browserNameA': '33-34 SAG',
    'browserNameB': '33-34 COR',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '35001 AX VIBE',
    'cameraView': {
        'position': [-230.60944034893606, 225.10991333832752, -394.64102504795454],
        'focalPoint': [28.099272402258137, -4.3539065458298865, -66.86069833791028],
        'viewUp': [0.24567694746027066, 0.8744678129889569, 0.41826891055027515],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [32, 32],
    'lastFrame': [40, 39],
    'loop': False
}

# T2

script_globals = {
    'browserNameA': '47-48 SAG',
    'browserNameB': '47-48 COR',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '49001 AX VIBE',
    'cameraView': {
        'position': [436.0848390013352, -222.63884639291925, -491.4983016707708],
        'focalPoint': [-12.610944922609619, 10.220544510948832, -137.315819487491],
        'viewUp': [-0.21930106723705964, -0.9193622818737608, 0.32661910014045165],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [22, 22],
    'lastFrame': [29, 29],
    'loop': False
}

# T3

script_globals = {
    'browserNameA': '57-58 SAG',
    'browserNameB': '57-58 COR',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '59001 AX VIBE',
    'cameraView': {
        'position': [-402.82752287043024, 289.54169056680587, -425.47225797608155],
        'focalPoint': [-4.74442, 18.377, -123.711],
        'viewUp': [0.31361209975563425, 0.8738502779595838, 0.3715281181779118],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [10, 10],
    'lastFrame': [29, 29],
    'loop': False
}

# T4

script_globals = {
    'browserNameA': '60-61 SAG',
    'browserNameB': '60-61 COR',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '62001 AX VIBE',
    'cameraView': {
        'position': [-429.81060995061443, 281.3693793982463, -382.10367224900426],
        'focalPoint': [-46.008222445720946, 43.213542592523424, -115.27296593682728],
        'viewUp': [0.3559634719158801, 0.8906431581721338, 0.2829218469167062],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [33, 34],
    'lastFrame': [47, 48],
    'loop': False
}

# T5

script_globals = {
    'browserNameA': '71-72 SAG',
    'browserNameB': '71-72 COR',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '73001 AX VIBE',
    'cameraView': {
        'position': [-487.4447986769182, 268.6196606513246, -439.44686310071586],
        'focalPoint': [-34.187921271223246, 23.09824059673931, -134.85742331594236],
        'viewUp': [0.3193125243032016, 0.911424533755633, 0.25950882661567515],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [21, 21],
    'lastFrame': [34, 33],
    'loop': False
}

# T6

script_globals = {
    'browserNameA': '77-78 SAG Browser',
    'browserNameB': '77-78 COR Browser',
    'viewerColorA': 'Yellow',
    'viewerColorB': 'Green',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '79001 AX VIBE',
    'cameraView': {
        'position': [-547.9152861191684, 431.8786509216361, -634.8376391595991],
        'focalPoint': [17.978120659085437, -1.8509075239135786, -93.29754064851899],
        'viewUp': [0.3177940544606002, 0.8739005893199872, 0.3678378704479356],
        'parallelScale': 1.0,
        'viewAngle': 14.999999999999975
    },
    'delayms': 1000,
    'firstFrame': [14, 14],
    'lastFrame': [26, 26],
    'loop': False
}

# T7

script_globals = {
    'browserNameA': '82-83 COR',
    'browserNameB': '82-83 SAG',
    'viewerColorA': 'Green',
    'viewerColorB': 'Yellow',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '84001 AX VIBE',
    'cameraView': {
        'position': [-477.4068851182397, 265.56381706050433, -438.14406862967724],
        'focalPoint': [-31.352668996696778, 23.943954190840564, -138.39483022928505],
        'viewUp': [0.31931252430320156, 0.9114245337556328, 0.2595088266156751],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [0, 1],
    'lastFrame': [22, 23],
    'loop': False
}

# T8

script_globals = {
    'browserNameA': '33-34 COR Browser',
    'browserNameB': '33-34 SAG Browser',
    'viewerColorA': 'Green',
    'viewerColorB': 'Yellow',
    'fiducialName': 'NeedleTip',
    'confidenceNodeName': 'CurrentTipConfidence',
    'confirmationVolumeName': '35001 AX VIBE',
    'cameraView': {
        'position': [-297.70153217124215, 252.14283432652104, -429.931000556036],
        'focalPoint': [13.701035978287955, -9.385995054754009, -30.49540811568034],
        'viewUp': [0.2374160878623685, 0.8871353283088852, 0.39575814646121255],
        'parallelScale': 1.0,
        'viewAngle': 30.0
    },
    'delayms': 1000,
    'firstFrame': [55, 55],
    'lastFrame': [70, 69],
    'loop': False
}

exec(open(filePath, encoding='utf-8').read(), script_globals)

# To stop the execution:

script_globals['stop_alternate_playback']()

"""


# Global timer and observer handles to allow external stopping

startPlaybackTimer = None
alternatePlaybackTimer = None
finalizePlaybackTimer = None
confirmationPlaybackTimer = None
confirmationZoomTimer = None

confidenceNode = None
confidenceObserverTag = None

# Orthogonal slice viewer waiting for the tracking result of the most
# recently updated browser. For example, a COR image updates the SAG
# viewer position, and a SAG image updates the COR viewer position.
# It is set immediately before advancing a browser.
pendingViewerColor = None

# Source plane that generated the pending tracking result.
pendingSourcePlane = None

# Detection results for the current COR-SAG pair.
lastCorSuccess = None
lastSagSuccess = None

# Number of completed COR-SAG pairs during playback.
cycleCount = 0

# Playback initialization state.
# The script first loads the initial COR/SAG pair, hides NeedleTip,
# and waits for the two confidence updates generated when tracking starts.
initializingPlayback = True
initializationResultCount = 0

# NeedleTip remains hidden after initialization and is shown only after
# the first successful detection from the actual playback.
waitingForFirstPlaybackDetection = False


def setupCustomLayout():
    """
    Set up the recording layout:
    - 3D view on the left
    - Coronal (Green) on the upper right
    - Sagittal (Yellow) on the lower right
    """

    customLayout = """
    <layout type="horizontal" split="true">
      <item splitSize="500">
        <view class="vtkMRMLViewNode" singletontag="1">
          <property name="viewlabel" action="default">1</property>
        </view>
      </item>
      <item splitSize="500">
        <layout type="vertical">
          <item>
            <view class="vtkMRMLSliceNode" singletontag="Green">
              <property name="orientation" action="default">Coronal</property>
              <property name="viewlabel" action="default">G</property>
              <property name="viewcolor" action="default">#6EB04B</property>
            </view>
          </item>
          <item>
            <view class="vtkMRMLSliceNode" singletontag="Yellow">
              <property name="orientation" action="default">Sagittal</property>
              <property name="viewlabel" action="default">Y</property>
              <property name="viewcolor" action="default">#EDD54C</property>
            </view>
          </item>
        </layout>
      </item>
    </layout>
    """

    customLayoutId = 508

    layoutManager = slicer.app.layoutManager()
    layoutNode = layoutManager.layoutLogic().GetLayoutNode()

    layoutNode.AddLayoutDescription(
        customLayoutId,
        customLayout
    )

    layoutManager.setLayout(customLayoutId)


def customize3DView():
    """
    Customize the 3D view for video recording.

    - Hide Red, Green, and Yellow slice borders in 3D.
    - Set the orientation marker to the cube.
    - Hide the 3D bounding box.
    - Hide the 3D axis labels.
    """

    # Hide slice borders in the 3D view
    for color in ["Red", "Green", "Yellow"]:
        sliceNode = slicer.mrmlScene.GetNodeByID(
            f"vtkMRMLSliceNode{color}"
        )

        if sliceNode is not None:
            sliceNode.SetSliceEdgeVisibility3D(False)

            # Start with all slice planes hidden in 3D.
            # Playback explicitly shows Green/Yellow as needed.
            sliceNode.SetSliceVisible(False)

    # Get 3D view node
    viewNode = (
        slicer.app.layoutManager()
        .threeDWidget(0)
        .mrmlViewNode()
    )

    # Set orientation marker to cube
    viewNode.SetOrientationMarkerType(
        viewNode.OrientationMarkerTypeCube
    )

    # Hide 3D bounding box and axis labels
    viewNode.SetBoxVisible(False)
    viewNode.SetAxisLabelsVisible(False)



def setCameraView(camera_view):
    """
    Restore a saved 3D camera view.

    camera_view is expected to contain:
    - position
    - focalPoint
    - viewUp
    - parallelScale
    - viewAngle
    """

    if not camera_view:
        print("No saved 3D camera view specified.")
        return

    viewNode = (
        slicer.app.layoutManager()
        .threeDWidget(0)
        .mrmlViewNode()
    )

    cameraNode = (
        slicer.modules.cameras.logic()
        .GetViewActiveCameraNode(viewNode)
    )

    if cameraNode is None:
        print("Warning: Could not find active 3D camera node.")
        return

    camera = cameraNode.GetCamera()

    camera.SetPosition(
        camera_view['position']
    )

    camera.SetFocalPoint(
        camera_view['focalPoint']
    )

    camera.SetViewUp(
        camera_view['viewUp']
    )

    camera.SetParallelScale(
        camera_view['parallelScale']
    )

    camera.SetViewAngle(
        camera_view['viewAngle']
    )

    cameraNode.Modified()
    slicer.util.forceRenderAllViews()

    print("3D camera view restored.")


def initializeViews(camera_view=None):
    """
    Initialize all Slicer views for video recording.
    """

    # Set custom layout
    setupCustomLayout()

    # Customize 3D view appearance
    customize3DView()

    # Reset field of view for all available slice viewers
    layoutManager = slicer.app.layoutManager()

    for color in ["Red", "Green", "Yellow"]:
        sliceWidget = layoutManager.sliceWidget(color)

        if sliceWidget is not None:
            sliceWidget.sliceLogic().FitSliceToAll()

    # Restore the trajectory-specific 3D camera framing once
    # during view initialization.
    setCameraView(
        camera_view
    )


def set3DViewText(text):
    """
    Show fixed text in the upper-right corner of the 3D view.
    Pass an empty string to clear the annotation.

    This uses the same minimal cornerAnnotation configuration
    verified directly in the Slicer Python Interactor.
    """

    view = (
        slicer.app.layoutManager()
        .threeDWidget(0)
        .threeDView()
    )

    annotation = view.cornerAnnotation()

    annotation.SetVisibility(True)

    annotation.SetText(
        vtk.vtkCornerAnnotation.UpperRight,
        text
    )

    textProperty = annotation.GetTextProperty()
    textProperty.SetColor(1.0, 1.0, 1.0)
    textProperty.SetBold(True)

    annotation.Modified()
    slicer.util.forceRenderAllViews()

    if text:
        print(
            f"3D annotation: {text}"
        )
    else:
        print("3D annotation cleared.")



def configureNeedleTipDisplay(fiducial_name):
    """
    Enhance NeedleTip visibility for video recording.

    3D display:
    - Visible in 3D
    - Occluded visibility enabled
    - Full standard opacity
    - Full occluded opacity

    2D display:
    - Visible in 2D
    - Projection visibility enabled
    - Projection uses markup/fiducial color
    - Projection outlined behind slice plane
    - Full projection opacity
    """

    fiducialNode = slicer.util.getNode(
        fiducial_name
    )

    displayNode = fiducialNode.GetDisplayNode()

    if displayNode is None:
        fiducialNode.CreateDefaultDisplayNodes()
        displayNode = fiducialNode.GetDisplayNode()

    if displayNode is None:
        print(
            f"Warning: Could not create display node for "
            f"'{fiducial_name}'."
        )
        return

    # General / 3D visibility
    displayNode.SetVisibility(True)
    displayNode.SetVisibility3D(True)
    displayNode.SetOpacity(1.0)
    displayNode.SetUseGlyphScale(True)
    displayNode.SetGlyphScale(2.0)

    # Markup text/label size
    displayNode.SetTextScale(6.0)

    # 3D occluded visibility
    displayNode.SetOccludedVisibility(True)
    displayNode.SetOccludedOpacity(1.0)

    # 2D visibility and projection
    displayNode.SetVisibility2D(True)
    displayNode.SetSliceProjection(True)
    displayNode.SetSliceProjectionUseFiducialColor(True)
    displayNode.SetSliceProjectionOutlinedBehindSlicePlane(False)
    displayNode.SetSliceProjectionOpacity(1.0)

    print(
        f"Enhanced 2D/3D display visibility for "
        f"'{fiducial_name}'."
    )


def setNeedleTipVisibility(
    fiducial_name,
    visible
):
    """
    Temporarily hide/show NeedleTip during initialization/playback.

    Initialization:
    - General display opacity = 0
    - 2D projection visibility = off

    Playback:
    - General display opacity = 1
    - 2D projection visibility = on

    Other 2D/3D display settings remain unchanged.
    """

    fiducialNode = slicer.util.getNode(
        fiducial_name
    )

    displayNode = fiducialNode.GetDisplayNode()

    if displayNode is None:
        fiducialNode.CreateDefaultDisplayNodes()
        displayNode = fiducialNode.GetDisplayNode()

    if displayNode is None:
        return

    if visible:
        displayNode.SetOpacity(1.0)
        displayNode.SetSliceProjection(True)

        print(
            "NeedleTip restored: opacity = 1.0, "
            "2D projection ON."
        )
    else:
        displayNode.SetOpacity(0.0)
        displayNode.SetSliceProjection(False)

        print(
            "NeedleTip hidden for initialization: "
            "opacity = 0.0, 2D projection OFF."
        )

    displayNode.Modified()
    slicer.util.forceRenderAllViews()



def getActualSliceOffsets(viewer_color):
    """
    Return the physical offsets of the actual acquired slices
    in the volume currently displayed in the specified viewer.
    """

    sliceWidget = (
        slicer.app.layoutManager()
        .sliceWidget(viewer_color)
    )

    if sliceWidget is None:
        print(
            f"Warning: Could not find "
            f"{viewer_color} slice widget."
        )
        return []

    sliceLogic = sliceWidget.sliceLogic()
    sliceNode = sliceLogic.GetSliceNode()

    # Get currently displayed background volume
    volumeNode = (
        sliceLogic
        .GetBackgroundLayer()
        .GetVolumeNode()
    )

    if volumeNode is None:
        print(
            f"Warning: No background volume displayed "
            f"in {viewer_color}."
        )
        return []

    imageData = volumeNode.GetImageData()

    if imageData is None:
        return []

    dimensions = imageData.GetDimensions()

    # Slice normal = third column of SliceToRAS
    sliceToRAS = sliceNode.GetSliceToRAS()

    normal = [
        sliceToRAS.GetElement(0, 2),
        sliceToRAS.GetElement(1, 2),
        sliceToRAS.GetElement(2, 2)
    ]

    # IJK-to-RAS geometry of the displayed volume
    ijkToRAS = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASMatrix(ijkToRAS)

    # Use the center voxel in I and J
    centerI = (dimensions[0] - 1) / 2.0
    centerJ = (dimensions[1] - 1) / 2.0

    sliceOffsets = []

    # Each K value corresponds to one acquired slice
    for k in range(dimensions[2]):

        ijk = [
            centerI,
            centerJ,
            float(k),
            1.0
        ]

        rasSlice = [0.0, 0.0, 0.0, 1.0]

        ijkToRAS.MultiplyPoint(
            ijk,
            rasSlice
        )

        offset = (
            rasSlice[0] * normal[0]
            + rasSlice[1] * normal[1]
            + rasSlice[2] * normal[2]
        )

        sliceOffsets.append(offset)

    return sliceOffsets


def updateSliceViewFromFiducial(
    fiducial_node,
    viewer_color
):
    """
    Move the specified viewer to the acquired slice closest
    to the fiducial point.

    The viewer is always positioned on one of the actual acquired
    slices of the currently displayed volume, preventing black
    intermediate or out-of-volume positions.

    Zoom/FOV and in-plane image position are preserved.
    """

    if fiducial_node is None:
        return

    if fiducial_node.GetNumberOfControlPoints() == 0:
        return

    # Fiducial position in world/RAS coordinates
    ras = [0.0, 0.0, 0.0]
    fiducial_node.GetNthControlPointPositionWorld(
        0,
        ras
    )

    sliceWidget = (
        slicer.app.layoutManager()
        .sliceWidget(viewer_color)
    )

    if sliceWidget is None:
        return

    sliceLogic = sliceWidget.sliceLogic()
    sliceNode = sliceLogic.GetSliceNode()

    sliceOffsets = getActualSliceOffsets(
        viewer_color
    )

    if not sliceOffsets:
        return

    # Slice normal = third column of SliceToRAS
    sliceToRAS = sliceNode.GetSliceToRAS()

    normal = [
        sliceToRAS.GetElement(0, 2),
        sliceToRAS.GetElement(1, 2),
        sliceToRAS.GetElement(2, 2)
    ]

    # NeedleTip position along the slice normal
    requestedOffset = (
        ras[0] * normal[0]
        + ras[1] * normal[1]
        + ras[2] * normal[2]
    )

    # Always select the actual acquired slice closest to NeedleTip
    closestOffset = min(
        sliceOffsets,
        key=lambda offset: abs(
            offset - requestedOffset
        )
    )

    sliceLogic.SetSliceOffset(
        closestOffset
    )

    if (
        requestedOffset < min(sliceOffsets)
        or requestedOffset > max(sliceOffsets)
    ):
        print(
            f"{viewer_color}: tip outside volume -> "
            "using nearest acquired slice."
        )

def setViewerToMiddleSlice(viewer_color):
    """
    Position the viewer on the middle acquired slice of the
    currently displayed volume.

    This is used when a new volume is loaded and there is no
    valid tracking result to determine another slice position.
    """

    sliceWidget = (
        slicer.app.layoutManager()
        .sliceWidget(viewer_color)
    )

    if sliceWidget is None:
        return

    sliceLogic = sliceWidget.sliceLogic()

    sliceOffsets = getActualSliceOffsets(
        viewer_color
    )

    if not sliceOffsets:
        return

    middleIndex = len(sliceOffsets) // 2
    middleOffset = sliceOffsets[middleIndex]

    sliceLogic.SetSliceOffset(
        middleOffset
    )

def observeTrackingResult(
    fiducial_name,
    confidence_node_name,
    initialization_complete_callback=None
):
    """
    Observe the tracking-result TextNode.

    Initialization phase:
    - The initial COR and SAG frames are already loaded.
    - NeedleTip is hidden.
    - The first two confidence updates generated when tracking starts
      are treated only as initialization and are not counted.

    Playback phase:
    - The same first COR and SAG frames are replayed.
    - The first successful playback detection reveals NeedleTip.
    - A completed COR-SAG pair is counted as one cycle.
    """

    global confidenceNode
    global confidenceObserverTag
    global pendingViewerColor
    global pendingSourcePlane
    global lastCorSuccess
    global lastSagSuccess
    global cycleCount
    global initializingPlayback
    global initializationResultCount
    global waitingForFirstPlaybackDetection

    # Remove previous observer if the script is run again
    if (
        confidenceNode is not None
        and confidenceObserverTag is not None
    ):
        confidenceNode.RemoveObserver(
            confidenceObserverTag
        )

    fiducialNode = slicer.util.getNode(
        fiducial_name
    )

    confidenceNode = slicer.util.getNode(
        confidence_node_name
    )

    acceptedConfidence = {
        "High",
        "Medium High",
        "Medium"
    }

    def onConfidenceModified(caller=None, event=None):
        global pendingViewerColor
        global pendingSourcePlane
        global lastCorSuccess
        global lastSagSuccess
        global cycleCount
        global initializingPlayback
        global initializationResultCount
        global waitingForFirstPlaybackDetection

        confidenceText = confidenceNode.GetText()

        if not confidenceText:
            return

        # Expected format:
        # timestamp; confidence text; confidence value
        parts = [
            part.strip()
            for part in confidenceText.split(";")
        ]

        if len(parts) < 2:
            print(
                "Warning: Unexpected CurrentTipConfidence format: "
                f"{confidenceText}"
            )
            return

        confidence = parts[1]

        # -------------------------------------------------------------
        # Initialization phase
        # -------------------------------------------------------------
        if initializingPlayback:
            initializationResultCount += 1

            print(
                "Tracking initialization result "
                f"{initializationResultCount}/2: "
                f"{confidence}"
            )

            # The tracking module processes the two already-present
            # orthogonal planes when tracking is started. These two
            # results initialize tracking but are not playback cycles.
            if initializationResultCount >= 2:
                initializingPlayback = False
                initializationResultCount = 0

                pendingViewerColor = None
                pendingSourcePlane = None
                lastCorSuccess = None
                lastSagSuccess = None
                cycleCount = 0

                # Keep the marker hidden until the first successful
                # detection from the actual playback is returned.
                waitingForFirstPlaybackDetection = True

                set3DViewText("")

                print(
                    "Tracking initialization complete. "
                    "Starting playback from the initial frames."
                )

                if initialization_complete_callback is not None:
                    # Defer playback start until the tracking callback
                    # has fully returned.
                    qt.QTimer.singleShot(
                        0,
                        initialization_complete_callback
                    )

            return

        # -------------------------------------------------------------
        # Playback phase
        # -------------------------------------------------------------
        if (
            pendingViewerColor is None
            or pendingSourcePlane is None
        ):
            return

        viewerColor = pendingViewerColor
        sourcePlane = pendingSourcePlane
        success = confidence in acceptedConfidence

        print(
            f"Tracking result for {sourcePlane}: "
            f"{confidence}"
        )

        if success:
            updateSliceViewFromFiducial(
                fiducialNode,
                viewerColor
            )

        else:
            # Do not use a previous/stale NeedleTip position.
            setViewerToMiddleSlice(
                viewerColor
            )

            print(
                f"{sourcePlane} tip not updated "
                f"(confidence: {confidence})"
            )

        # The initialization tip remained invisible. Once the first
        # real playback tracking result has returned, restore NeedleTip
        # display. If that result failed, the marker remains at the last
        # valid tracked position until a later successful result updates it.
        if waitingForFirstPlaybackDetection:
            print(
                "First playback result received. "
                "NeedleTip will be restored after the proxy update returns."
            )

        # Store this scan result for the current COR-SAG pair.
        if sourcePlane == "COR":
            lastCorSuccess = success

        elif sourcePlane == "SAG":
            lastSagSuccess = success

        # Once both views have produced a result, one cycle is complete.
        if (
            lastCorSuccess is not None
            and lastSagSuccess is not None
        ):
            cycleCount += 1

            if lastCorSuccess and lastSagSuccess:
                set3DViewText(
                    f"Cycle {cycleCount}"
                )

            elif lastCorSuccess and not lastSagSuccess:
                set3DViewText(
                    f"Cycle {cycleCount} | "
                    "COR: success | SAG: fail"
                )

            elif not lastCorSuccess and lastSagSuccess:
                set3DViewText(
                    f"Cycle {cycleCount} | "
                    "COR: fail | SAG: success"
                )

            else:
                set3DViewText(
                    f"Cycle {cycleCount} | "
                    "COR: fail | SAG: fail"
                )

            # Start collecting the next COR-SAG pair.
            lastCorSuccess = None
            lastSagSuccess = None

        # This tracking result has been consumed.
        pendingViewerColor = None
        pendingSourcePlane = None

    confidenceObserverTag = confidenceNode.AddObserver(
        vtk.vtkCommand.ModifiedEvent,
        onConfidenceModified
    )

    print(
        f"Observing '{confidence_node_name}' "
        "for tracking results."
    )


def alternate_playback(
    browser_name_A: str,
    browser_name_B: str,
    viewer_color_A: str,
    viewer_color_B: str,
    fiducial_name: str,
    confidence_node_name: str,
    confirmation_volume_name: str,
    camera_view=None,
    delay_ms: float = 1000,
    first_frame=(0, 0),
    last_frame=(-1, -1),
    loop: bool = False
):
    """
    Alternates frame-by-frame playback between two sequence browsers.

    The slice plane corresponding to the currently active browser
    is shown in the 3D view, while the other slice planes are hidden.

    :param browser_name_A: Name of Sequence Browser A.
    :param browser_name_B: Name of Sequence Browser B.
    :param viewer_color_A: Slice viewer associated with Browser A.
                           Valid values: 'Red', 'Green', 'Yellow'.
    :param viewer_color_B: Slice viewer associated with Browser B.
                           Valid values: 'Red', 'Green', 'Yellow'.
    :param fiducial_name: Name of the tracked-tip fiducial node.
    :param confidence_node_name: Name of the tracking-confidence TextNode.
    :param confirmation_volume_name: Name of the post-insertion
                                     confirmation VIBE volume.
    :param camera_view: Saved 3D camera framing dictionary.
    :param delay_ms: Delay in milliseconds between playback steps.
    :param first_frame: Two-element sequence containing the initial frames
                        for browsers A and B: [firstFrameA, firstFrameB].
    :param last_frame: Two-element sequence containing the final frames
                       for browsers A and B: [lastFrameA, lastFrameB].
                       A value of -1 selects the final available frame.
    :param loop: Restart playback after both browsers reach their final frames.
    """

    global startPlaybackTimer
    global alternatePlaybackTimer
    global finalizePlaybackTimer
    global confirmationPlaybackTimer
    global confirmationZoomTimer
    global pendingViewerColor
    global pendingSourcePlane
    global lastCorSuccess
    global lastSagSuccess
    global cycleCount
    global initializingPlayback
    global initializationResultCount
    global waitingForFirstPlaybackDetection

    validViewerColors = ["Red", "Green", "Yellow"]

    # In the custom recording layout:
    # Green = Coronal, Yellow = Sagittal.
    viewerToPlane = {
        "Green": "COR",
        "Yellow": "SAG",
        "Red": "AX"
    }

    sourcePlaneA = viewerToPlane.get(
        viewer_color_A,
        viewer_color_A
    )

    sourcePlaneB = viewerToPlane.get(
        viewer_color_B,
        viewer_color_B
    )

    if viewer_color_A not in validViewerColors:
        raise ValueError(
            f"Invalid viewerColorA '{viewer_color_A}'. "
            f"Valid values are {validViewerColors}."
        )

    if viewer_color_B not in validViewerColors:
        raise ValueError(
            f"Invalid viewerColorB '{viewer_color_B}'. "
            f"Valid values are {validViewerColors}."
        )

    if viewer_color_A == viewer_color_B:
        raise ValueError(
            "viewerColorA and viewerColorB must refer to "
            "different slice viewers."
        )

    
    if len(first_frame) != 2:
        raise ValueError(
            "'first_frame' must contain two elements: "
            "[firstFrameA, firstFrameB]."
        )

    if len(last_frame) != 2:
        raise ValueError(
            "'last_frame' must contain two elements: "
            "[lastFrameA, lastFrameB]."
        )

    # Initialize Slicer views for recording and restore
    # the trajectory-specific saved 3D camera framing.
    initializeViews(
        camera_view
    )

    # Enhance NeedleTip visibility in both 2D and 3D views
    configureNeedleTipDisplay(
        fiducial_name
    )

    # Get Sequence Browser nodes
    browserA = slicer.util.getNode(browser_name_A)
    browserB = slicer.util.getNode(browser_name_B)

    # Get Red, Green, and Yellow slice nodes
    sliceNodes = {
        "Red": slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed"),
        "Green": slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen"),
        "Yellow": slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow")
    }

    for color, sliceNode in sliceNodes.items():
        if sliceNode is None:
            raise RuntimeError(
                f"Could not find the {color} slice node."
            )

    def setActiveSlicePlane(activeViewerColor):
        """
        Show only the active browser's slice plane in the 3D view.
        Hide Red, Green, and Yellow first, then enable the active one.
        """

        for sliceNode in sliceNodes.values():
            sliceNode.SetSliceVisible(False)

        sliceNodes[activeViewerColor].SetSliceVisible(True)

        print(
            f"3D slice visibility: "
            f"{activeViewerColor} ON"
        )

    def showBothSlicePlanes():
        """
        Show both Browser A and Browser B slice planes in the 3D view.
        All other standard slice planes are hidden.
        """

        for sliceNode in sliceNodes.values():
            sliceNode.SetSliceVisible(False)

        sliceNodes[viewer_color_A].SetSliceVisible(True)
        sliceNodes[viewer_color_B].SetSliceVisible(True)

        print(
            f"3D slice visibility: "
            f"{viewer_color_A} + {viewer_color_B} ON"
        )

    def showConfirmationVolume():
        """
        Replace the tracking views with the confirmation VIBE volume.

        Green remains Coronal and Yellow remains Sagittal in the
        visible 2D layout. Red is used only as an Axial VIBE plane
        in the 3D view.

        All three VIBE planes are positioned directly through the
        final NeedleTip RAS coordinates.
        """

        if not confirmation_volume_name:
            print(
                "No confirmationVolumeName specified. "
                "Skipping confirmation VIBE."
            )
            return

        try:
            confirmationVolume = slicer.util.getNode(
                confirmation_volume_name
            )
        except Exception:
            print(
                f"Warning: Confirmation volume "
                f"'{confirmation_volume_name}' not found."
            )
            return

        fiducialNode = slicer.util.getNode(
            fiducial_name
        )

        if (
            fiducialNode is None
            or fiducialNode.GetNumberOfControlPoints() == 0
        ):
            print(
                "Warning: NeedleTip not available. "
                "Cannot position confirmation VIBE."
            )
            return

        # Final tracked NeedleTip in world RAS coordinates.
        ras = [0.0, 0.0, 0.0]

        fiducialNode.GetNthControlPointPositionWorld(
            0,
            ras
        )

        print(
            "Final NeedleTip RAS:",
            ras
        )

        # ----------------------------------------------------------
        # Load VIBE into Green, Yellow, and Red.
        # Red is not part of the visible 2D layout, but its slice
        # plane will be shown in the 3D view.
        # ----------------------------------------------------------

        for viewerColor in [
            "Green",
            "Yellow",
            "Red"
        ]:
            sliceWidget = (
                slicer.app.layoutManager()
                .sliceWidget(viewerColor)
            )

            if sliceWidget is None:
                continue

            sliceLogic = sliceWidget.sliceLogic()

            compositeNode = (
                sliceLogic
                .GetSliceCompositeNode()
            )

            compositeNode.SetBackgroundVolumeID(
                confirmationVolume.GetID()
            )

        # ----------------------------------------------------------
        # Set the desired orthogonal orientations.
        # ----------------------------------------------------------

        greenNode = slicer.util.getNode(
            "vtkMRMLSliceNodeGreen"
        )

        yellowNode = slicer.util.getNode(
            "vtkMRMLSliceNodeYellow"
        )

        redNode = slicer.util.getNode(
            "vtkMRMLSliceNodeRed"
        )

        greenNode.SetOrientation(
            "Coronal"
        )

        yellowNode.SetOrientation(
            "Sagittal"
        )

        redNode.SetOrientation(
            "Axial"
        )

        # ----------------------------------------------------------
        # Reset field of view for the two visible VIBE viewers.
        #
        # Do this BEFORE applying the NeedleTip offsets, because
        # FitSliceToAll() may recenter the slice.
        # ----------------------------------------------------------

        for viewerColor in [
            "Green",
            "Yellow"
        ]:
            sliceWidget = (
                slicer.app.layoutManager()
                .sliceWidget(viewerColor)
            )

            if sliceWidget is None:
                continue

            sliceWidget.sliceLogic().FitSliceToAll()

        # ----------------------------------------------------------
        # Position all three VIBE planes directly through the final
        # NeedleTip.
        #
        # This is deliberately done AFTER FitSliceToAll(), so the
        # final slice positions remain exactly at the NeedleTip RAS
        # coordinates.
        # ----------------------------------------------------------

        for viewerColor in [
            "Green",
            "Yellow",
            "Red"
        ]:
            sliceWidget = (
                slicer.app.layoutManager()
                .sliceWidget(viewerColor)
            )

            if sliceWidget is None:
                continue

            sliceLogic = sliceWidget.sliceLogic()
            sliceNode = sliceLogic.GetSliceNode()

            sliceToRAS = (
                sliceNode.GetSliceToRAS()
            )

            normal = [
                sliceToRAS.GetElement(0, 2),
                sliceToRAS.GetElement(1, 2),
                sliceToRAS.GetElement(2, 2)
            ]

            offset = (
                ras[0] * normal[0]
                + ras[1] * normal[1]
                + ras[2] * normal[2]
            )

            sliceLogic.SetSliceOffset(
                offset
            )

            print(
                f"{viewerColor} VIBE offset = "
                f"{offset:.3f}"
            )

        # ----------------------------------------------------------
        # Show all three orthogonal VIBE planes in the 3D view.
        # ----------------------------------------------------------

        greenNode.SetSliceVisible(True)
        yellowNode.SetSliceVisible(True)
        redNode.SetSliceVisible(True)

        # Final video annotation.
        set3DViewText(
            "Confirmation VIBE"
        )

        slicer.util.forceRenderAllViews()

        print(
            f"Confirmation VIBE displayed: "
            f"{confirmation_volume_name}"
        )

        print(
            f"Holding confirmation VIBE for "
            f"{int(2 * delay_ms)} ms before progressive 100% zoom..."
        )

        confirmationZoomTimer.start()

    def zoomConfirmationView():
        """
        Progressively zoom the active 3D camera in by 100% after
        the VIBE confirmation has been displayed for one complete cycle.

        The animation lasts one delay_ms interval and is split into
        multiple small zoom steps for a smoother final video.
        """

        viewNode = (
            slicer.app.layoutManager()
            .threeDWidget(0)
            .mrmlViewNode()
        )

        cameraNode = (
            slicer.modules.cameras.logic()
            .GetViewActiveCameraNode(viewNode)
        )

        if cameraNode is None:
            print(
                "Warning: Could not find active 3D camera node "
                "for confirmation zoom."
            )
            return

        camera = cameraNode.GetCamera()

        totalZoom = 2.00
        steps = 20
        stepZoom = totalZoom ** (1.0 / steps)

        intervalMs = max(
            1,
            int(delay_ms / steps)
        )

        currentStep = 0

        progressiveZoomTimer = qt.QTimer()
        progressiveZoomTimer.setInterval(intervalMs)

        def zoomStep():
            nonlocal currentStep

            camera.Zoom(stepZoom)

            cameraNode.Modified()
            slicer.util.forceRenderAllViews()

            currentStep += 1

            if currentStep >= steps:
                progressiveZoomTimer.stop()

                print(
                    "Progressive 25% confirmation zoom complete."
                )

        progressiveZoomTimer.timeout.connect(zoomStep)

        # Keep a reference so the timer is not garbage-collected.
        nonlocalProgressiveTimers.append(
            progressiveZoomTimer
        )

        print(
            f"Starting progressive confirmation zoom: "
            f"25% over {int(delay_ms)} ms "
            f"({steps} steps)."
        )

        progressiveZoomTimer.start()

    def getCurrentIndex(browser):
        return browser.GetSelectedItemNumber()

    def getMaxIndex(browser):
        return browser.GetNumberOfItems() - 1

    def validateFrameRange(
        browser,
        browser_name,
        requested_first_frame,
        requested_last_frame
    ):
        max_index = getMaxIndex(browser)

        if max_index < 0:
            raise ValueError(
                f"Sequence Browser '{browser_name}' contains no items."
            )

        first_index = max(
            0,
            min(int(requested_first_frame), max_index)
        )

        if requested_last_frame >= 0:
            last_index = max(
                0,
                min(int(requested_last_frame), max_index)
            )
        else:
            last_index = max_index

        if first_index > last_index:
            raise ValueError(
                f"Invalid frame range for '{browser_name}': "
                f"first frame {first_index} is greater than "
                f"last frame {last_index}."
            )

        return first_index, last_index

    def advanceBrowser(browser, maximum_index):
        current_index = getCurrentIndex(browser)

        if current_index < maximum_index:
            browser.SetSelectedItemNumber(current_index + 1)
            return True

        return False

    # Validate independent frame ranges
    firstFrameA, lastFrameA = validateFrameRange(
        browser=browserA,
        browser_name=browser_name_A,
        requested_first_frame=first_frame[0],
        requested_last_frame=last_frame[0]
    )

    firstFrameB, lastFrameB = validateFrameRange(
        browser=browserB,
        browser_name=browser_name_B,
        requested_first_frame=first_frame[1],
        requested_last_frame=last_frame[1]
    )

    # Stop previous timers if the script is executed again
    if startPlaybackTimer and startPlaybackTimer.isActive():
        startPlaybackTimer.stop()

    if alternatePlaybackTimer and alternatePlaybackTimer.isActive():
        alternatePlaybackTimer.stop()

    if finalizePlaybackTimer and finalizePlaybackTimer.isActive():
        finalizePlaybackTimer.stop()

    if (
        confirmationPlaybackTimer
        and confirmationPlaybackTimer.isActive()
    ):
        confirmationPlaybackTimer.stop()

    if (
        confirmationZoomTimer
        and confirmationZoomTimer.isActive()
    ):
        confirmationZoomTimer.stop()

    # Internal playback timers
    startPlaybackTimer = None

    alternatePlaybackTimer = qt.QTimer()
    alternatePlaybackTimer.setInterval(int(delay_ms))

    finalizePlaybackTimer = qt.QTimer()
    finalizePlaybackTimer.setSingleShot(True)
    finalizePlaybackTimer.setInterval(int(delay_ms))

    confirmationPlaybackTimer = qt.QTimer()
    confirmationPlaybackTimer.setSingleShot(True)

    # Hold the final bi-plane tracking view for one complete
    # COR-SAG cycle (two scan intervals) before VIBE confirmation.
    confirmationPlaybackTimer.setInterval(
        int(2 * delay_ms)
    )

    confirmationZoomTimer = qt.QTimer()
    confirmationZoomTimer.setSingleShot(True)

    # After the VIBE confirmation appears, hold it for one
    # complete cycle before zooming the 3D view in by 25%.
    confirmationZoomTimer.setInterval(
        int(2 * delay_ms)
    )

    def printCurrentFrame(browser_name, browser):
        print(
            f"Frame {browser_name} "
            f"#{getCurrentIndex(browser)}"
        )

    def resetPlayback():
        nonlocal currentBrowser
        global pendingViewerColor
        global pendingSourcePlane
        global lastCorSuccess
        global lastSagSuccess
        global cycleCount
        global initializingPlayback
        global initializationResultCount
        global waitingForFirstPlaybackDetection

        # Initial frame loading is only for playback setup.
        # Do not associate these frame changes with a pending tracking
        # result, because tracking may not be running yet.
        pendingViewerColor = None
        pendingSourcePlane = None
        lastCorSuccess = None
        lastSagSuccess = None
        cycleCount = 0
        initializingPlayback = True
        initializationResultCount = 0
        waitingForFirstPlaybackDetection = False

        set3DViewText("")

        # Hide the initialization tip. It will remain hidden until
        # the first successful detection from the actual playback.
        setNeedleTipVisibility(
            fiducial_name,
            False
        )

        browserA.SetSelectedItemNumber(firstFrameA)

        # Keep Browser A's initialization view on the middle
        # acquired slice of the newly loaded volume.
        setViewerToMiddleSlice(
            viewer_color_A
        )

        printCurrentFrame(browser_name_A, browserA)

        browserB.SetSelectedItemNumber(firstFrameB)

        # Keep Browser B's initialization view on the middle
        # acquired slice of the newly loaded volume.
        setViewerToMiddleSlice(
            viewer_color_B
        )

        printCurrentFrame(browser_name_B, browserB)

        # Show both initialized slice planes in 3D.
        # Once alternating playback begins, only the currently
        # updated browser's slice plane will be shown.
        showBothSlicePlanes()


        # Browser A is the first active browser during playback
        currentBrowser = "A"

    firstPlaybackPass = True

    # Keep references to short-lived progressive zoom timers so
    # they are not garbage-collected before the animation completes.
    nonlocalProgressiveTimers = []

    def startPlayback():
        nonlocal currentBrowser
        nonlocal firstPlaybackPass

        # Replay the exact same first A/B frames that were used for
        # initialization. Cycle counting starts only now.
        currentBrowser = "A"
        firstPlaybackPass = True

        print("Alternating playback started from initial frames.")

        alternatePlaybackTimer.start()

    def finalizePlayback():
        """
        After one normal playback delay following the final frame,
        show both final tracking planes together.

        Hold this final tracking state for one additional delay_ms
        interval before switching to the VIBE confirmation.
        """

        set3DViewText("")
        showBothSlicePlanes()

        # Red is reserved for the final axial VIBE plane and
        # remains hidden throughout tracking playback.
        redNode = slicer.util.getNode(
            "vtkMRMLSliceNodeRed"
        )
        redNode.SetSliceVisible(False)

        slicer.util.forceRenderAllViews()

        print(
            f"Final tracking planes displayed. "
            f"Holding for {int(2 * delay_ms)} ms "
            f"(one cycle) before confirmation VIBE..."
        )

        confirmationPlaybackTimer.start()

    def stepPlayback():
        nonlocal currentBrowser
        nonlocal firstPlaybackPass
        global pendingViewerColor
        global pendingSourcePlane
        global waitingForFirstPlaybackDetection

        if currentBrowser == "A":

            if (
                firstPlaybackPass
                or getCurrentIndex(browserA) < lastFrameA
            ):
                # Set this BEFORE refreshing/advancing the browser because
                # the tracking module may process the image immediately.
                #
                # Browser A's result moves Browser B's orthogonal viewer.
                pendingViewerColor = viewer_color_B
                pendingSourcePlane = sourcePlaneA

                if firstPlaybackPass:
                    # Replay the already-selected initialization frame
                    # without changing to another sequence item.
                    slicer.modules.sequences.logic().UpdateProxyNodesFromSequences(
                        browserA
                    )

                    # The tracking callback has fully returned by this point.
                    # Restore NeedleTip opacity here, outside the tracking
                    # callback, so it cannot be overwritten afterward.
                    fiducialNode = slicer.util.getNode(
                        fiducial_name
                    )
                    displayNode = fiducialNode.GetDisplayNode()

                    if displayNode is not None:
                        displayNode.SetOpacity(1.0)
                        displayNode.SetSliceProjection(True)
                        displayNode.Modified()
                        slicer.util.forceRenderAllViews()

                        print(
                            "NeedleTip restored after first playback "
                            "tracking result: "
                            f"opacity={displayNode.GetOpacity():.1f}, "
                            f"projection={int(displayNode.GetSliceProjection())}"
                        )

                    waitingForFirstPlaybackDetection = False

                else:
                    advanceBrowser(
                        browserA,
                        lastFrameA
                    )

                # Keep Browser A's own viewer on the middle acquired slice
                # of the newly loaded volume.
                setViewerToMiddleSlice(
                    viewer_color_A
                )

                printCurrentFrame(browser_name_A, browserA)

                # Show Browser A's associated slice in 3D
                setActiveSlicePlane(viewer_color_A)
            else:
                pendingViewerColor = None
                pendingSourcePlane = None

            currentBrowser = "B"

        else:

            if (
                firstPlaybackPass
                or getCurrentIndex(browserB) < lastFrameB
            ):
                # Set this BEFORE refreshing/advancing the browser because
                # the tracking module may process the image immediately.
                #
                # Browser B's result moves Browser A's orthogonal viewer.
                pendingViewerColor = viewer_color_A
                pendingSourcePlane = sourcePlaneB

                if firstPlaybackPass:
                    # Replay the already-selected initialization frame
                    # without changing to another sequence item.
                    slicer.modules.sequences.logic().UpdateProxyNodesFromSequences(
                        browserB
                    )

                    # The initial A/B pair has now been replayed.
                    firstPlaybackPass = False
                else:
                    advanceBrowser(
                        browserB,
                        lastFrameB
                    )

                # Keep Browser B's own viewer on the middle acquired slice
                # of the newly loaded volume.
                setViewerToMiddleSlice(
                    viewer_color_B
                )

                printCurrentFrame(browser_name_B, browserB)

                # Show Browser B's associated slice in 3D
                setActiveSlicePlane(viewer_color_B)
            else:
                pendingViewerColor = None
                pendingSourcePlane = None

            currentBrowser = "A"

        browserAHasFinished = (
            getCurrentIndex(browserA) >= lastFrameA
        )

        browserBHasFinished = (
            getCurrentIndex(browserB) >= lastFrameB
        )

        if browserAHasFinished and browserBHasFinished:
            if loop:
                print("Restart...")
                resetPlayback()
            else:
                alternatePlaybackTimer.stop()

                print(
                    f"Last frame reached. "
                    f"Showing both planes in {int(delay_ms)} ms..."
                )

                # Preserve one normal playback pause after the final
                # sequence update before restoring the bi-plane view.
                finalizePlaybackTimer.start()

    currentBrowser = "A"

    # Reset both browsers to their independent initial frames
    resetPlayback()

    alternatePlaybackTimer.timeout.connect(stepPlayback)
    finalizePlaybackTimer.timeout.connect(finalizePlayback)
    confirmationPlaybackTimer.timeout.connect(
        showConfirmationVolume
    )
    confirmationZoomTimer.timeout.connect(
        zoomConfirmationView
    )

    # Observe tracking only after the initialization frames are loaded.
    # The first two confidence updates are treated as initialization.
    observeTrackingResult(
        fiducial_name,
        confidence_node_name,
        initialization_complete_callback=startPlayback
    )

    print(f"Browser A: {browser_name_A}")
    print(f"  Viewer: {viewer_color_A}")
    print(f"  Range: {firstFrameA} to {lastFrameA}")

    print(f"Browser B: {browser_name_B}")
    print(f"  Viewer: {viewer_color_B}")
    print(f"  Range: {firstFrameB} to {lastFrameB}")

    print(
        "Waiting for tracking initialization... "
        "Start tracking when ready."
    )


def stop_alternate_playback():
    """Stop delayed start, playback, finalization, and confidence observer."""

    global startPlaybackTimer
    global alternatePlaybackTimer
    global finalizePlaybackTimer
    global confirmationPlaybackTimer
    global confirmationZoomTimer
    global confidenceNode
    global confidenceObserverTag
    global pendingViewerColor
    global pendingSourcePlane
    global lastCorSuccess
    global lastSagSuccess
    global cycleCount
    global initializingPlayback
    global initializationResultCount
    global waitingForFirstPlaybackDetection

    stopped = False

    if startPlaybackTimer and startPlaybackTimer.isActive():
        startPlaybackTimer.stop()
        stopped = True

    if alternatePlaybackTimer and alternatePlaybackTimer.isActive():
        alternatePlaybackTimer.stop()
        stopped = True

    if finalizePlaybackTimer and finalizePlaybackTimer.isActive():
        finalizePlaybackTimer.stop()
        stopped = True

    if (
        confirmationPlaybackTimer
        and confirmationPlaybackTimer.isActive()
    ):
        confirmationPlaybackTimer.stop()
        stopped = True

    if (
        confirmationZoomTimer
        and confirmationZoomTimer.isActive()
    ):
        confirmationZoomTimer.stop()
        stopped = True

    if (
        confidenceNode is not None
        and confidenceObserverTag is not None
    ):
        confidenceNode.RemoveObserver(
            confidenceObserverTag
        )

        confidenceObserverTag = None
        stopped = True

    pendingViewerColor = None
    pendingSourcePlane = None
    lastCorSuccess = None
    lastSagSuccess = None
    cycleCount = 0
    initializingPlayback = True
    initializationResultCount = 0
    waitingForFirstPlaybackDetection = False
    set3DViewText("")

    if stopped:
        print("Alternate playback stopped.")
    else:
        print("No active timer or observer to stop.")


# Check for external variables and call playback if available

try:
    browserNameA
except NameError:
    browserNameA = None

try:
    browserNameB
except NameError:
    browserNameB = None

try:
    viewerColorA
except NameError:
    viewerColorA = None

try:
    viewerColorB
except NameError:
    viewerColorB = None

try:
    fiducialName
except NameError:
    fiducialName = None

try:
    confidenceNodeName
except NameError:
    confidenceNodeName = None

try:
    confirmationVolumeName
except NameError:
    confirmationVolumeName = ""

try:
    cameraView
except NameError:
    cameraView = None

try:
    delayms
except NameError:
    delayms = None

try:
    firstFrame
except NameError:
    firstFrame = [0, 0]

try:
    lastFrame
except NameError:
    lastFrame = [-1, -1]

try:
    loop
except NameError:
    loop = False


if None in (
    browserNameA,
    browserNameB,
    viewerColorA,
    viewerColorB,
    fiducialName,
    confidenceNodeName,
    delayms
):
    print(
        "Error: Missing 'browserNameA', 'browserNameB', "
        "'viewerColorA', 'viewerColorB', 'fiducialName', "
        "'confidenceNodeName', or 'delayms'. "
        "Please define them before executing the script."
    )
else:
    alternate_playback(
        browser_name_A=browserNameA,
        browser_name_B=browserNameB,
        viewer_color_A=viewerColorA,
        viewer_color_B=viewerColorB,
        fiducial_name=fiducialName,
        confidence_node_name=confidenceNodeName,
        confirmation_volume_name=confirmationVolumeName,
        camera_view=cameraView,
        delay_ms=delayms,
        first_frame=firstFrame,
        last_frame=lastFrame,
        loop=loop
    )