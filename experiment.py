import os
import copy
import random

import numpy

from constants import *
from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze.mouse import Mouse
from pygaze.logfile import Logfile
from pygaze.eyetracker import EyeTracker
import pygaze.libtime as timer

from libmri import *


MRI = False; # Flag for using button box and waiting for pulses/ seinding triggers etc 

##############
# INITIALISE #
##############

# get participant info etc
LOGFILENAME = input("Participant name: ") 
LOGFILE = LOGFILENAME[:] +'_trials'

# response mapping 
# 0 = go squares, no-go circles 
# 1 = go circles, no-go squares
RESPMAP = int(input("Response Mapping: "))

# Initialise a new Display instance.
disp = Display()

# Present a start-up screen.
scr = Screen()
scr.draw_text("Loading, please wait...", fontsize=24)
disp.fill(scr)
disp.show()

# Open a new log file.
log = Logfile(filename = LOGFILE)
# TODO: Write header.
log.write(["trialnr", "block", "run","stim", "keypress", "go_nogo", "face_onset", "signal_onset","resp_onset", "RT", "accuracy", "respmap"])

# Initialise the eye tracker.
tracker = EyeTracker(disp)

# Create a new Keyboard instance to process key presses.
kb = Keyboard(keylist=None, timeout=5000)
mouse = Mouse()

# intitliase the MEG interface NI box 
if MRI:
	trigbox = MRITriggerBox()

###################
# GENERATE TRIALS #
###################
""" 
A run is a split of experiment, so each run should be matched by randomised 
We have 8 blocks: 4 distractors types x 2 go or no-go conditions 

The trial information is head in the trial object. The structure is as follows:

trial[runNo][blockNo][trialNo][infoNo]

infoNo is:
0 = distractor filename 
1 = trial type 
2 = ITI 
3 = Stimonset 
4 = screens 
	0 = face only screen
	1 = face + signal screen 
"""


trials = [[]] * len(RUNS) # for populating

# calulate range of ITIs and Stim onsets 
stepsize = (ITI_RANGE[1] - ITI_RANGE[0]) /TRIALS_PER_BLOCK
itis = numpy.arange(ITI_RANGE[0], ITI_RANGE[1], stepsize).astype(int)

stepsize = (SIGNAL_ONSET_RANGE[1] - SIGNAL_ONSET_RANGE[0]) /TRIALS_PER_BLOCK
onsets = numpy.arange(SIGNAL_ONSET_RANGE[0], SIGNAL_ONSET_RANGE[1], stepsize).astype(int)

for run in RUNS: # for each run
	trials[run] = [[]] * len(BLOCKS) 
	for i, block in enumerate(BLOCKS):# for each block 
		trials[run][i] = [[]] * TRIALS_PER_BLOCK
		prefix = block[0] # get filename the prefix for the image we need
		if block[-1] == 'n': # generate condition vector for this block based on condition
			conds = ['go'] * (TRIALS_PER_BLOCK - NO_GO_TRIALS) + ['no-go']*NO_GO_TRIALS # go/no-go block
			random.shuffle(conds)
		else:
			conds = ['go'] * TRIALS_PER_BLOCK # go only block
		# shuffle the jittering 
		random.shuffle(itis)
		random.shuffle(onsets)
		print(itis[0])
		for ii in range(TRIALS_PER_BLOCK): # loop through all the trials 
			trials[run][i][ii] = [[]] * 5
			trials[run][i][ii][0] = prefix + '_' + str(ii) + '.jpg' #image name 
			trials[run][i][ii][1] = conds[ii] # trial type 
			trials[run][i][ii][2] = itis[ii] # iti time
			trials[run][i][ii][3] = onsets[ii] # signal onset time 
			trials[run][i][ii][4] = [[]] * 3
			# now pre-generate the screens! 
			# Note: this is code efficient but not memory efficient (i.e. I am lazy and would rather pre-load almost twice the number of screens, because this is why we have RAM)

			tempstim = Screen()
			#tempstim.draw_image(RESDIR + trials[run][i][ii][0], pos=DISPCENTRE)# draw face on center of screen 
			tempstim.draw_image(RESDIR + trials[run][i][ii][0], pos=DISPCENTRE, scale=0.5)# draw face on center of screen 
			trials[run][i][ii][4][0] = tempstim

			tempsig = Screen()
			#tempsig.draw_image(RESDIR + trials[run][i][ii][0], pos=DISPCENTRE)# draw face on center of screen
			tempsig.draw_image(RESDIR + trials[run][i][ii][0], pos=DISPCENTRE, scale=0.5)# draw face on center of screen 

			tempfeed = Screen()
			tempfeed.draw_image(RESDIR + trials[run][i][ii][0], pos=DISPCENTRE, scale=0.5)#
			#RESPMAP 0 = go squares, no-go circles 

			square_sz = 100
			square_off = square_sz/2
			pen_width = 6
			circle_sz = 50
			# 1 = go circles, no-go squares
			if conds[ii] == 'go':
				if RESPMAP == 0:
					tempsig.draw_rect(colour=None, x=DISPCENTRE[0]-square_off, y=DISPCENTRE[1]-square_off, w=square_sz, h=square_sz, pw=pen_width, fill=False)
					tempfeed.draw_rect(colour=(128,128,128), x=DISPCENTRE[0]-square_off, y=DISPCENTRE[1]-square_off, w=square_sz, h=square_sz, pw=pen_width, fill=False)
				else: 
					tempsig.draw_circle(colour=None, pos=DISPCENTRE, r=circle_sz, pw=pen_width, fill=False)
					tempfeed.draw_circle(colour=(128,128,128), pos=DISPCENTRE, r=circle_sz, pw=pen_width, fill=False)
			if conds[ii] == 'no-go':
				if RESPMAP == 1:
					tempsig.draw_rect(colour=None, x=DISPCENTRE[0]-square_off, y=DISPCENTRE[1]-square_off, w=square_sz, h=square_sz, pw=pen_width, fill=False)
					tempfeed.draw_rect(colour=(128,128,128), x=DISPCENTRE[0]-square_off, y=DISPCENTRE[1]-square_off, w=square_sz, h=square_sz, pw=pen_width, fill=False)
				else: 
					tempsig.draw_circle(colour=None, pos=DISPCENTRE, r=circle_sz, pw=pen_width, fill=False)
					tempfeed.draw_circle(colour=(128,128,128), pos=DISPCENTRE, r=circle_sz, pw=pen_width, fill=False)
			trials[run][i][ii][4][1] = tempsig 
			trials[run][i][ii][4][2] = tempfeed



# now shuffe the order of blocks and shuffle the trials in each block 
for i in range(len(trials)):
	random.shuffle(trials[i])
	for ii in range(len(trials[i])):
		random.shuffle(trials[i][ii])


#############################
# GENERATE STANDARD SCREENS #
#############################

"""
These are screens that we re-use multiple times with no changes, so pre-generation is optimal 
"""

# Fixation cross - we use this for ITI and the response window 
fix_screen = Screen()
fix_screen.draw_fixation(fixtype='cross', pw=3, diameter=8)

# Inter run screen 
inter_run = Screen()
txt = \
"""
This is the screen before a run of trials 

PRESS ANY BUTTON TO START RUN
"""
inter_run.draw_text(txt, fontsize=24)

#inter block screen 
inter_block = Screen()
txt = \
"""
This is the screen before a block of trials 

PRESS ANY BUTTON TO START BLOCK
"""
inter_block.draw_text(txt, fontsize=24)


# loop through runs 
for i, currRun in enumerate(trials):
	disp.fill(inter_run) # fill display
	disp.show()# show display
	### CONTINUE WHEN BUTTON PRESSED ###
	if MRI: # if MEG repeatedly loop until button state changes
		btn_pressed = False # set flag to false
		while btn_pressed != True:
			btn_list, state = MRI.get_button_state(button_list = [MAIN_BUT])
			if state[0] != 0:
				btn_pressed = True
	else: 
		mouse.get_clicked()

	# loop through blocks
	for ii, currBlock in enumerate(currRun): 
		disp.fill(inter_block); # fill display
		disp.show() # show display
		
		### CONTINUE WHEN BUTTON PRESSED ###
		if MRI: # if MEG repeatedly loop until button state changes
			btn_pressed = False # set flag to false
			while btn_pressed != True:
				btn_list, state = MRI.get_button_state(button_list = [MAIN_BUT])
				if state[0] != 0:
					btn_pressed = True
		else: 
			mouse.get_clicked()

		#loop through trials 
		for iii, currTrial in enumerate(currBlock): 
			
			key, presstime = kb.get_key(keylist=['q', 'f', 'j'], timeout=1, flush=False)
			if key == 'q':
				log.close()
				tracker.close()
				disp.close()
				raise Exception('DEBUG KILL')
			"""trial[runNo][blockNo][trialNo][infoNo]
			infoNo is:
			0 = distractor filename 
			1 = trial type 
			2 = ITI 
			3 = Stimonset 
			4 = screens 
				0 = face only screen
				1 = face + signal screen 
			"""

			#display ITI and pause for length of ITI 
			disp.fill(fix_screen)
			iti_onset = disp.show()
			timer.pause(currTrial[2]) 

			#display face only and pause for the stimulus onset
			disp.fill(currTrial[4][0])
			stim_onset = disp.show()
			timer.pause(currTrial[3])

			#display face and signal and pause for the remainder of face duration 
			disp.fill(currTrial[4][1])
			signal_onset = disp.show()
			#timer.pause(FACE_DURATION - currTrial[3])

			# response window and wait for response or timeout 
			#disp.fill(fix_screen)
			#response_onset = disp.show()
			t1 = copy.copy(signal_onset)

			if MRI: # if MRI repeatedly loop until button state changes or response timeout is met
				btn_pressed = False # set flag to false
				while btn_pressed != True and t1 - signal_onset < RESPONSE_TIMEOUT:
					btn_list, state = MRI.get_button_state(button_list = [MAIN_BUT])
					if state[0] != 0:
						btn_pressed = True
			else: 
				mouse.get_clicked(timeout = RESPONSE_TIMEOUT)



			disp.fill(currTrial[4][2])
			time_resp = disp.show()
			rt = time_resp - t1
			if rt >= RESPONSE_TIMEOUT:
				keypress = 0
			else:
				keypress = 1 
			time_left = RESPONSE_TIMEOUT - rt
			print(rt, time_left)
			timer.pause(time_left)

			# log this trial
			if currTrial[1] == 'go':
				if keypress == 1: 
					accu = 1
				else:
					accu = 0
			else:
				if keypress == 1:
					accu = 0
				else:
					accu = 1 
			#log.write(["trialnr", "block", "run","stim", "keypress", "go_nogo", "face_onset", "signal_onset","resp_onset", "RT", "accuracy", "respmap"])
			#log.write(["trialnr", "block","run", "stim", "keypress", "go_nogo", "face_onset", "signal_onset","resp_onset", "RT", "accuracy", "respmap"])
			log.write([str(iii), str(ii), str(i), currTrial[0], str(keypress), currTrial[1], str(stim_onset), str(signal_onset), str(time_resp), str(rt), str(accu), str(RESPMAP)])



#Ending stuff 
log.close()
tracker.close()
disp.close()


