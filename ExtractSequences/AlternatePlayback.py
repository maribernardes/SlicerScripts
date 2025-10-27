import slicer
import time
from __main__ import qt

"""
# Example execution snippet:
filePath = "/home/mariana/SlicerScripts/ExtractSequences/AlternatePlayback.py"

#T1
script_globals = {'browserNameA': '33-34 SAG', 'browserNameB': '33-34 COR', 'delayms': 1000, 'firstFrame': 26, 'loop': False}

#T2
script_globals = {'browserNameA': '47-48 SAG', 'browserNameB': '47-48 COR', 'delayms': 1000, 'firstFrame': 20, 'lastFrame': 29,'loop': False}

#T3
script_globals = {'browserNameA': '57-58 SAG', 'browserNameB': '57-58 COR', 'delayms': 1000, 'firstFrame': 5, 'lastFrame': 29,'loop': False}

# T8:
script_globals = {'browserNameA': '33-34 COR Browser', 'browserNameB': '33-34 SAG Browser', 'delayms': 1000, 'firstFrame': 55, 'loop': False}


exec(open(filePath, encoding='utf-8').read(), script_globals)

# To stop the execution
script_globals['stop_alternate_playback']()
"""

# Global timer handle to allow external stop
startPlaybackTimer = None
alternatePlaybackTimer = None

def alternate_playback(browser_name_A: str, browser_name_B: str, delay_ms: float = 1000, first_frame: int = 0, last_frame: int = -1, loop: bool = False):
    """
    Alternates frame-by-frame playback between two sequence browsers.
    :param browser_name_A: Name of the Sequence Browser for sequence A.
    :param browser_name_B: Name of the Sequence Browser for sequence B.
    :param delay_ms: Delay in milliseconds between frames.
    """
    global startPlaybackTimer
    global alternatePlaybackTimer

    # Load sequence browser node names
    browserA = slicer.util.getNode(browser_name_A)
    browserB = slicer.util.getNode(browser_name_B)

    # Internal playback timers
    startPlaybackTimer = qt.QTimer()
    startPlaybackTimer.setInterval(5000)

    alternatePlaybackTimer = qt.QTimer()
    alternatePlaybackTimer.setInterval(delay_ms)

    def getCurrentIndex(browser):
        return browser.GetSelectedItemNumber()

    def getMaxIndex(browser):
        return browser.GetNumberOfItems() - 1

    def advanceBrowser(browser, maxIndex):
        index = getCurrentIndex(browser)
        if index < maxIndex:
            browser.SetSelectedItemNumber(index + 1)
            return True
        return False

    def startPlayback():
        print("Alternating playback started.")
        startPlaybackTimer.stop()
        alternatePlaybackTimer.timeout.connect(stepPlayback)
        alternatePlaybackTimer.start()

    def stepPlayback():
        nonlocal currentBrowser
        nonlocal lastFrameA
        nonlocal lastFrameB

        if currentBrowser == 'A':
            advanceBrowser(browserA, lastFrameA)
            print('Frame ' + browser_name_A + ' #' + str(getCurrentIndex(browserA)))
            currentBrowser = 'B'
        else:
            advanceBrowser(browserB, lastFrameB)
            print('Frame ' + browser_name_B + ' #' + str(getCurrentIndex(browserB)))
            currentBrowser = 'A'

        if getCurrentIndex(browserA) >= lastFrameA and \
            getCurrentIndex(browserB) >= lastFrameB:
            if loop is True:
                print("Restart...")
                browserA.SetSelectedItemNumber(0)
                browserB.SetSelectedItemNumber(0)
            else:
                print("Playback finished.")
                alternatePlaybackTimer.stop()

    # Set final frame
    if last_frame >=0:
        lastFrameA = last_frame
        lastFrameB = last_frame
    else:
        lastFrameA = getMaxIndex(browserA)
        lastFrameB = getMaxIndex(browserB)

    # Reset both to first frame
    browserA.SetSelectedItemNumber(first_frame)
    browserB.SetSelectedItemNumber(first_frame)
    print('Frame ' + browser_name_A + ' #' + str(getCurrentIndex(browserA)))
    print('Frame ' + browser_name_B + ' #' + str(getCurrentIndex(browserB)))
    currentBrowser = 'A'

    print('Starting playback in 5 seconds...')
    startPlaybackTimer.timeout.connect(startPlayback)
    startPlaybackTimer.start()



def stop_alternate_playback():
    """Stop the alternating playback if it's running."""
    global alternatePlaybackTimer
    if alternatePlaybackTimer and alternatePlaybackTimer.isActive():
        alternatePlaybackTimer.stop()
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
    firstFrame = 0
try:
    lastFrame
except NameError:
    lastFrame = -1
try:
    loop
except NameError:
    loop = False

if None in (browserNameA, browserNameB, delayms):  
    print("Error: Missing 'browserNameA',  'browserNameB', 'delayms'. Please define it before executing the script.")
else:
    alternate_playback(browser_name_A=browserNameA, browser_name_B=browserNameB, delay_ms=delayms, first_frame=firstFrame, last_frame=lastFrame, loop=loop)
