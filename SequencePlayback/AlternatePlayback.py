import slicer
import time
from __main__ import qt

"""
# Example execution snippet:
filePath = "/home/mariana/SlicerScripts/ExtractSequences/AlternatePlayback.py"
filePath = "/Users/pl771/SlicerScripts/ExtractSequences/AlternatePlayback.py"

# firstFrame and lastFrame are two-element arrays:
# [frame for browserNameA, frame for browserNameB]

# T1
script_globals = {
    'browserNameA': '33-34 SAG',
    'browserNameB': '33-34 COR',
    'delayms': 1000,
    'firstFrame': [32, 32],
    'lastFrame': [40, 39],
    'loop': False
}

# T2
script_globals = {
    'browserNameA': '47-48 SAG',
    'browserNameB': '47-48 COR',
    'delayms': 1000,
    'firstFrame': [22, 22],
    'lastFrame': [29, 29],
    'loop': False
}

# T3
script_globals = {
    'browserNameA': '57-58 SAG',
    'browserNameB': '57-58 COR',
    'delayms': 1000,
    'firstFrame': [10, 10],
    'lastFrame': [29, 29],
    'loop': False
}

# T4
script_globals = {
    'browserNameA': '60-61 SAG',
    'browserNameB': '60-61 COR',
    'delayms': 1000,
    'firstFrame': [33, 34],
    'lastFrame': [47, 48],
    'loop': False
}

# T5
script_globals = {
    'browserNameA': '71-72 SAG',
    'browserNameB': '71-72 COR',
    'delayms': 1000,
    'firstFrame': [21, 21],
    'lastFrame': [34, 33],
    'loop': False
}

# T6
script_globals = {
    'browserNameA': '77-78 SAG Browser',
    'browserNameB': '77-78 COR Browser',
    'delayms': 1000,
    'firstFrame': [14, 14],
    'lastFrame': [26, 26],
    'loop': False
}

# T7
script_globals = {
    'browserNameA': '82-83 COR',
    'browserNameB': '82-83 SAG',
    'delayms': 1000,
    'firstFrame': [0, 1],
    'lastFrame': [22, 23],
    'loop': False
}

# T8
script_globals = {
    'browserNameA': '33-34 COR Browser',
    'browserNameB': '33-34 SAG Browser',
    'delayms': 1000,
    'firstFrame': [55, 55],
    'lastFrame': [70, 69],
    'loop': False
}

exec(open(filePath, encoding='utf-8').read(), script_globals)

# To stop the execution:
script_globals['stop_alternate_playback']()
"""

# Global timer handles to allow external stopping
startPlaybackTimer = None
alternatePlaybackTimer = None


def alternate_playback(
    browser_name_A: str,
    browser_name_B: str,
    delay_ms: float = 1000,
    first_frame=(0, 0),
    last_frame=(-1, -1),
    loop: bool = False
):
    """
    Alternates frame-by-frame playback between two sequence browsers.

    :param browser_name_A: Name of Sequence Browser A.
    :param browser_name_B: Name of Sequence Browser B.
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

    # Load Sequence Browser nodes
    browserA = slicer.util.getNode(browser_name_A)
    browserB = slicer.util.getNode(browser_name_B)

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

    # Internal playback timers
    startPlaybackTimer = qt.QTimer()
    startPlaybackTimer.setSingleShot(True)
    startPlaybackTimer.setInterval(5000)

    alternatePlaybackTimer = qt.QTimer()
    alternatePlaybackTimer.setInterval(int(delay_ms))

    def printCurrentFrame(browser_name, browser):
        print(
            f"Frame {browser_name} "
            f"#{getCurrentIndex(browser)}"
        )

    def resetPlayback():
        nonlocal currentBrowser

        browserA.SetSelectedItemNumber(firstFrameA)
        browserB.SetSelectedItemNumber(firstFrameB)

        printCurrentFrame(browser_name_A, browserA)
        printCurrentFrame(browser_name_B, browserB)

        currentBrowser = "A"

    def startPlayback():
        print("Alternating playback started.")
        alternatePlaybackTimer.start()

    def stepPlayback():
        nonlocal currentBrowser

        if currentBrowser == "A":
            advanceBrowser(browserA, lastFrameA)
            printCurrentFrame(browser_name_A, browserA)
            currentBrowser = "B"

        else:
            advanceBrowser(browserB, lastFrameB)
            printCurrentFrame(browser_name_B, browserB)
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
                print("Playback finished.")
                alternatePlaybackTimer.stop()

    currentBrowser = "A"

    # Reset both browsers to their independent initial frames
    resetPlayback()

    alternatePlaybackTimer.timeout.connect(stepPlayback)
    startPlaybackTimer.timeout.connect(startPlayback)

    print(f"Browser A range: {firstFrameA} to {lastFrameA}")
    print(f"Browser B range: {firstFrameB} to {lastFrameB}")
    print("Starting playback in 5 seconds...")

    startPlaybackTimer.start()


def stop_alternate_playback():
    """Stop the delayed start or alternating playback."""
    global startPlaybackTimer
    global alternatePlaybackTimer

    stopped = False

    if startPlaybackTimer and startPlaybackTimer.isActive():
        startPlaybackTimer.stop()
        stopped = True

    if alternatePlaybackTimer and alternatePlaybackTimer.isActive():
        alternatePlaybackTimer.stop()
        stopped = True

    if stopped:
        print("Alternate playback stopped.")
    else:
        print("No active timer to stop.")


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


if None in (browserNameA, browserNameB, delayms):
    print(
        "Error: Missing 'browserNameA', 'browserNameB', or 'delayms'. "
        "Please define them before executing the script."
    )
else:
    alternate_playback(
        browser_name_A=browserNameA,
        browser_name_B=browserNameB,
        delay_ms=delayms,
        first_frame=firstFrame,
        last_frame=lastFrame,
        loop=loop
    )