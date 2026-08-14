import slicer
import vtk
import time
from __main__ import qt

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

confidenceNode = None
confidenceObserverTag = None

# Orthogonal slice viewer waiting for the tracking result of the most
# recently updated browser. For example, a COR image updates the SAG
# viewer position, and a SAG image updates the COR viewer position.
# It is set immediately before advancing a browser.
pendingViewerColor = None


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


def initializeViews():
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
    confidence_node_name
):
    """
    Observe the tracking-result TextNode.

    CurrentTipConfidence is expected to contain:
        timestamp; confidence text; confidence value

    When a completed tracking result has High, Medium High, or
    Medium confidence, update only the slice viewer associated
    with the browser that generated that image.
    """

    global confidenceNode
    global confidenceObserverTag
    global pendingViewerColor

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

        # No browser update is currently waiting for a result
        if pendingViewerColor is None:
            return

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
        viewerColor = pendingViewerColor

        print(
            f"Tracking result for {viewerColor}: "
            f"{confidence}"
        )

        if confidence in acceptedConfidence:
            updateSliceViewFromFiducial(
                fiducialNode,
                viewerColor
            )
        else:
            # Do not use the previous/stale NeedleTip position.
            # Keep this viewer at the center in case of no tip detection.
            setViewerToMiddleSlice(
                viewerColor
            )

            print(
                f"{viewerColor} tip not updated "
                f"(confidence: {confidence})"
            )

        # This tracking result has been consumed
        pendingViewerColor = None

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
    global pendingViewerColor

    validViewerColors = ["Red", "Green", "Yellow"]

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

    # Initialize Slicer views for recording
    initializeViews()

    # Observe completed tracking results. The corresponding slice
    # viewer is updated only when confidence is accepted.
    observeTrackingResult(
        fiducial_name,
        confidence_node_name
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

    # Internal playback timers
    startPlaybackTimer = qt.QTimer()
    startPlaybackTimer.setSingleShot(True)
    startPlaybackTimer.setInterval(5000)

    alternatePlaybackTimer = qt.QTimer()
    alternatePlaybackTimer.setInterval(int(delay_ms))

    finalizePlaybackTimer = qt.QTimer()
    finalizePlaybackTimer.setSingleShot(True)
    finalizePlaybackTimer.setInterval(int(delay_ms))

    def printCurrentFrame(browser_name, browser):
        print(
            f"Frame {browser_name} "
            f"#{getCurrentIndex(browser)}"
        )

    def resetPlayback():
        nonlocal currentBrowser
        global pendingViewerColor

        # Initial frame loading is only for playback setup.
        # Do not associate these frame changes with a pending tracking
        # result, because tracking may not be running yet.
        pendingViewerColor = None

        browserA.SetSelectedItemNumber(firstFrameA)
        printCurrentFrame(browser_name_A, browserA)

        browserB.SetSelectedItemNumber(firstFrameB)
        printCurrentFrame(browser_name_B, browserB)

        # Show both initialized slice planes in 3D.
        # Once alternating playback begins, only the currently
        # updated browser's slice plane will be shown.
        showBothSlicePlanes()

        # Browser A is the first active browser during playback
        currentBrowser = "A"

    def startPlayback():
        print("Alternating playback started.")
        alternatePlaybackTimer.start()

    def finalizePlayback():
        """
        After one normal playback delay following the final frame,
        show both slice planes again to finish the recording.
        """
        showBothSlicePlanes()
        print("Playback finished.")

    def stepPlayback():
        nonlocal currentBrowser
        global pendingViewerColor

        if currentBrowser == "A":

            if getCurrentIndex(browserA) < lastFrameA:
                # Set this BEFORE advancing the browser because the
                # tracking module may process the new image immediately.
                #
                # A new image updates the tracked coordinate that belongs
                # to the orthogonal slice plane, so Browser A's tracking
                # result moves Browser B's viewer.
                pendingViewerColor = viewer_color_B
                advanceBrowser(browserA, lastFrameA)

                # Keep Browser A's own viewer on a valid acquired slice
                # of the newly loaded volume.
                setViewerToMiddleSlice(
                    viewer_color_A
                )

                printCurrentFrame(browser_name_A, browserA)

                # Show Browser A's associated slice in 3D
                setActiveSlicePlane(viewer_color_A)
            else:
                pendingViewerColor = None

            currentBrowser = "B"

        else:

            if getCurrentIndex(browserB) < lastFrameB:
                # Set this BEFORE advancing the browser because the
                # tracking module may process the new image immediately.
                #
                # A new image updates the tracked coordinate that belongs
                # to the orthogonal slice plane, so Browser B's tracking
                # result moves Browser A's viewer.
                pendingViewerColor = viewer_color_A
                advanceBrowser(browserB, lastFrameB)

                # Keep Browser B's own viewer on a valid acquired slice
                # of the newly loaded volume.
                setViewerToMiddleSlice(
                    viewer_color_B
                )

                printCurrentFrame(browser_name_B, browserB)

                # Show Browser B's associated slice in 3D
                setActiveSlicePlane(viewer_color_B)
            else:
                pendingViewerColor = None

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
    startPlaybackTimer.timeout.connect(startPlayback)
    finalizePlaybackTimer.timeout.connect(finalizePlayback)

    print(f"Browser A: {browser_name_A}")
    print(f"  Viewer: {viewer_color_A}")
    print(f"  Range: {firstFrameA} to {lastFrameA}")

    print(f"Browser B: {browser_name_B}")
    print(f"  Viewer: {viewer_color_B}")
    print(f"  Range: {firstFrameB} to {lastFrameB}")

    print("Starting playback in 5 seconds...")

    startPlaybackTimer.start()


def stop_alternate_playback():
    """Stop delayed start, playback, finalization, and confidence observer."""

    global startPlaybackTimer
    global alternatePlaybackTimer
    global finalizePlaybackTimer
    global confidenceNode
    global confidenceObserverTag
    global pendingViewerColor

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
        confidenceNode is not None
        and confidenceObserverTag is not None
    ):
        confidenceNode.RemoveObserver(
            confidenceObserverTag
        )

        confidenceObserverTag = None
        stopped = True

    pendingViewerColor = None

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
        delay_ms=delayms,
        first_frame=firstFrame,
        last_frame=lastFrame,
        loop=loop
    )