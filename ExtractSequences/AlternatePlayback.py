import slicer
from __main__ import qt

"""
# Example execution snippet:
filePath = "/home/mariana/SlicerScripts/ExtractSequences/AlternatePlayback.py"
script_globals = {'browserNameA': 'COR', 'browserNameB': 'SAG', 'delayms': 500}
exec(open(filePath, encoding='utf-8').read(), script_globals)
"""

def alternate_playback(browser_name_A: str, browser_name_B: str, delay_ms: float = 1000):
    """
    Alternates frame-by-frame playback between two sequence browsers.
    :param browser_name_A: Name of the Sequence Browser for sequence A.
    :param browser_name_B: Name of the Sequence Browser for sequence B.
    :param delay_ms: Delay in milliseconds between frames.
    """

    # Load sequence browser node names
    browserA = slicer.util.getNode(browser_name_A)
    browserB = slicer.util.getNode(browser_name_B)

    # Internal playback state
    currentBrowser = 'A'
    timer = qt.QTimer()
    timer.setInterval(delay_ms)

    def getCurrentIndex(browser):
        return browser.GetSelectedItemNumber()

    def getMaxIndex(browser):
        return browser.GetNumberOfItems() - 1

    def advanceBrowser(browser):
        index = getCurrentIndex(browser)
        maxIndex = getMaxIndex(browser)
        if index < maxIndex:
            browser.SetSelectedItemNumber(index + 1)
            return True  # advanced
        return False  # already at the end

    def stepPlayback():
        nonlocal currentBrowser  # <-- Fix: use nonlocal instead of global

        if currentBrowser == 'A':
            advanceBrowser(browserA)
            currentBrowser = 'B'
        else:
            advanceBrowser(browserB)
            currentBrowser = 'A'

        # Stop the timer if both have reached their ends
        if getCurrentIndex(browserA) >= getMaxIndex(browserA) and \
           getCurrentIndex(browserB) >= getMaxIndex(browserB):
            print("Playback finished.")
            timer.stop()

    # Connect timer to the playback function
    timer.timeout.connect(stepPlayback)

    # Reset both to first frame
    browserA.SetSelectedItemNumber(0)
    browserB.SetSelectedItemNumber(0)
    currentBrowser = 'A'

    # Start alternating playback
    timer.start()
    print("Alternating playback started.")

# Check if the required variables are defined
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

# Run if all inputs are available
if None in (browserNameA, browserNameB, delayms):  
    print("Error: Missing 'browserNameA',  'browserNameB' or 'delayms'. Please define it before executing the script.")
else:
    alternate_playback(browser_name_A=browserNameA, browser_name_B=browserNameB, delay_ms=delayms)