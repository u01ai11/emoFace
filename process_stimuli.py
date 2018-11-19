#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 13:14:14 2018

@author: root
"""

#%%
import cv2

import dlib
import sys, os 
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt 
import numpy as np
from PIL import Image
from scramble_tools import *
#%%

# check if we are in interactive shell or not. If not we can get relative path to the script 
if sys.__stdin__.isatty():
    #Do some stuff to make it this path
    abspath = os.path.abspath('__file__')
    dname = os.path.dirname(abspath)
    os.chdir(dname)
else:
    dname = '/Users/ai05/ownCloud/emoFace'
    os.chdir(dname)

indir = 'selected_faces'
outdir = 'output'
onlyfiles = [f for f in listdir(indir) if isfile(join(indir, f))]

#%% set up some dlib stuff
pred = 'dlib.face.landmarks.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(pred)

#%% set up desied atributes 
desiredLeftEye=(0.35, 0.4)
desiredFaceWidth=1024
desiredFaceHeight=1300
#%% read image 
for file_name in onlyfiles:
    fname = indir + '/' + file_name
    #fname = 'S27_9yoM_Neutral_front_1040.JPG'
    im = cv2.imread(fname, 1)
    #gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    # detect rect with faces and points 
    rects = detector(im)
    points = predictor(im, rects[0]).parts()
    
    #get the points we want ()
    l_eye = [points[i] for i in [37, 38, 39, 40, 41, 42]]
    r_eye = [points[i] for i in [43, 44, 45, 46, 47, 48]]
    # eye centroid
    av_l =  np.mean(l_eye)
    av_r =  np.mean(r_eye)
    # compute the angle between the eye centroids
    dY = av_r.y - av_l.y
    dX = av_r.x - av_l.x
    angle = np.degrees(np.arctan2(dY, dX)) 
    
    # desired right eye x coordiante based on the x corridnates of the left eye 
    desiredRightEyeX = 1.0 - desiredLeftEye[0]
    
    # determine the scale of the new resulting image by taking
    # the ratio of the distance between eyes in the *current*
    # image to the ratio of distance between eyes in the
    # *desired* image
    dist = np.sqrt((dX ** 2) + (dY ** 2))
    desiredDist = (desiredRightEyeX - desiredLeftEye[0])
    desiredDist *= desiredFaceWidth
    scale = desiredDist / dist
    
    # compute center (x, y)-coordinates (i.e., the median point)
    # between the two eyes in the input image
    eyesCenter = ((av_l.x + av_r.x) // 2,
        (av_l.y + av_r.y) // 2)
     
    # grab the rotation matrix for rotating and scaling the face
    M = cv2.getRotationMatrix2D(eyesCenter, angle-13, scale)
     
    # update the translation component of the matrix
    tX = desiredFaceWidth * 0.5
    tY = desiredFaceHeight * desiredLeftEye[1]
    M[0, 2] += (tX - eyesCenter[0])
    M[1, 2] += (tY - eyesCenter[1])
    
     # apply the affine transformation
    (w, h) = (desiredFaceWidth, desiredFaceHeight)
    output = cv2.warpAffine(im, M, (w, h),
        flags=cv2.INTER_CUBIC)
    
    
    RGB_img = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    grey = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(outdir +'/'+ file_name ,grey)
    #cv2.circle(output, (int(desiredFaceWidth/2), int(desiredFaceHeight/2)),10,255,-2)
    #plt.imshow(output), plt.show()
    

    #    
    #    # threshold 
    #    ret,thresh1 = cv2.threshold(output,50,1,cv2.THRESH_BINARY)
    #    
    #    #scramble non-zero pixels 
    #    #for i in output: 
    #        
    #    
    #    plt.imshow(thresh1, 'gray')
    #    
    #    #%% colour thresholding?
    #    # define range of blue color in HSV
    #    cim = cv2.imread(fname,cv2.COLOR_RGB2HSV)
    #    lower = np.array([10,20, 75])
    #    upper = np.array([220,255,255])
    #    mask = cv2.inRange(cim, lower, upper)
    #    plt.imshow(mask)
    #%%
    password = 'helloo'
    filename= outdir +'/'+ file_name
    nshuffle=1
    granularity=6
    threshold =100;
    file = False
    
    
    new_image=scramble_blocks(RGB_img,granularity,password,nshuffle, threshold, file)
    
    #save scrambled image 
    scramblecv = np.array(new_image); # np array for CV 
    scramblecv = cv2.cvtColor(scramblecv, cv2.COLOR_RGB2GRAY)
    cv2.imwrite(outdir +'/scr_'+ file_name ,grey)
    
