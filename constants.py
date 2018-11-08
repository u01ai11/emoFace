# Some text here to explain the experiment.
#
# Version 1 (2018-07-26)

import os

# DISPLAY SETTINGS
# Display back-end ('pygame' or 'psychopy').
# NOTE: Use PsychoPy, as we're doing PsychoPy-specific stuff with orientations.
DISPTYPE = 'psychopy'
# Display resolution (match with your computer screen!).
DISPSIZE = (1440, 900)
DISPCENTRE = (DISPSIZE[0]//2, DISPSIZE[1]//2)
# Foreground and background colour.
FGC = (  0,   0,   0)
BGC = (128, 128, 128)
# Screen size in centimeters (measure your screen!).
# TODO: Measure this in the lab.
SCREENSIZE = (30.0, 20.0)
# Screen-to-participant distance in centimeters.
# TODO: Measure in lab.
SCREENDIST = 62.0
#colour vector for green to red feedback 
#set up list of colours for colour space 


# FILES AND FOLDERS
# Auto-detect folders.
DIR = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(DIR, 'data/')
RESDIR = os.path.join(DIR, 'resources/')
# Check whether these folders exist.
if not os.path.isdir(DATADIR):
    os.mkdir(DATADIR)
if not os.path.isdir(RESDIR):
    raise Exception("ERROR: Missing the 'resources' directory at this directory:\n'%s'" \
        % (RESDIR))

# EXPERIMENT SETTINGS
# response mapping 
# 0 = go squares, no-go circles 
# 1 = go circles, no-go squares
#RESP_MAP = 0 

# Number of times the unique combinations of stim order and cue direction are
# run.

# number of times we see each face 
FACE_REPEATS = 2
RUNS = [0, 1] 
BLOCKS= ['n_g', 'n_n', 'h_g', 'h_n', 's_g', 's_n', 'c_g', 'c_n']

NO_GO_TRIALS = 5 
TRIALS_PER_BLOCK = 18

#MEG Button box info 
# button_list = ["S3", "S4", "S5", "S6", "S7"]
MAIN_BUT = "S3"

LEFT_BUT = "S3"
RIGHT_BUT = "S4"
# TIMING
# ITI in milliseconds
ITI_RANGE = [1242, 1742] 
# Duration of the blank screen between stimulus and cue (ms).
SIGNAL_ONSET_RANGE = [192, 492]
# Duration of the cue.
FACE_DURATION = 742
# response timeout duration.
RESPONSE_TIMEOUT = 992


# EYE TRACKER SETTINGS
# Brand of the eye tracker.
TRACKERTYPE = 'eyelink'
DUMMYMODE = True
# Number of trials between each drift check.
DRIFT_CHECK_FREQ = 20



