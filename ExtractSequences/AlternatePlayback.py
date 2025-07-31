import slicer
from __main__ import qt

"""
# Example execution snippet:
filePath = "/home/mariana/SlicerScripts/ExtractSequences/AlternatePlayback.py"
script_globals = {'browserNameA': 'COR', 'browserNameB': 'SAG', 'delayms': 500, 'loop': False}
exec(open(filePath, encoding='utf-8').read(), script_globals)

# To stop the execution
script_globals['stop_alternate_playback']()
"""

# Global timer handle to allow external stop
alternatePlaybackTimer = None

def alternate_playback(browser_name_A: str, browser_name_B: str, delay_ms: float = 1000, loop: bool = False):
    """
    Alternates frame-by-frame playback between two sequence browsers.
    :param browser_name_A: Name of the Sequence Browser for sequence A.
    :param browser_name_B: Name of the Sequence Browser for sequence B.
    :param delay_ms: Delay in milliseconds between frames.
    """
    global alternatePlaybackTimer

    # Load sequence browser node names
    browserA = slicer.util.getNode(browser_name_A)
    browserB = slicer.util.getNode(browser_name_B)


    # Internal playback state
    currentBrowser = 'A'
    alternatePlaybackTimer = qt.QTimer()
    alternatePlaybackTimer.setInterval(delay_ms)

    def getCurrentIndex(browser):
        return browser.GetSelectedItemNumber()

    def getMaxIndex(browser):
        return browser.GetNumberOfItems() - 1

    def advanceBrowser(browser):
        index = getCurrentIndex(browser)
        maxIndex = getMaxIndex(browser)
        if index < maxIndex:
            browser.SetSelectedItemNumber(index + 1)
            return True
        return False

    def stepPlayback():
        nonlocal currentBrowser

        if currentBrowser == 'A':
            advanceBrowser(browserA)
            currentBrowser = 'B'
        else:
            advanceBrowser(browserB)
            currentBrowser = 'A'

        if getCurrentIndex(browserA) >= getMaxIndex(browserA) and \
           getCurrentIndex(browserB) >= getMaxIndex(browserB):
            if loop is True:
                print("Restart...")
                browserA.SetSelectedItemNumber(0)
                browserB.SetSelectedItemNumber(0)
            else:
                print("Playback finished.")
                alternatePlaybackTimer.stop()

    # Reset both to first frame
    browserA.SetSelectedItemNumber(0)
    browserB.SetSelectedItemNumber(0)
    currentBrowser = 'A'

    # Connect and start the timer
    alternatePlaybackTimer.timeout.connect(stepPlayback)
    alternatePlaybackTimer.start()
    print("Alternating playback started.")

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
    loop
except NameError:
    loop = None

if None in (browserNameA, browserNameB, delayms, loop):  
    print("Error: Missing 'browserNameA',  'browserNameB', 'delayms' or 'loop'. Please define it before executing the script.")
else:
    alternate_playback(browser_name_A=browserNameA, browser_name_B=browserNameB, delay_ms=delayms, loop=loop)
