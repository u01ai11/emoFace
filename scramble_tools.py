#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Face 
"""
Created on Mon Nov 19 14:28:41 2018

@author: Alex Irvine 

set of functions for finding a thresholded image and 
"""


from PIL import Image
from PIL import ImageStat as imstat
import random
import numpy as np
import cv2

def scramble_blocks(im_name,granularity,password,nshuffle, threshold, file_or_not):
    
    if file_or_not == True:
        im=Image.open(im_name);
    else:
        im = Image.fromarray(im_name)

    width=im.size[0]
    height=im.size[1]
    

        
    
    block_width=find_block_dim(granularity,width)       #find the possible block dimensions
    block_height=find_block_dim(granularity,height)

    grid_width_dim=int(width//block_width)                #dimension of the grid
    grid_height_dim=int(height//block_height)

    nblocks=grid_width_dim*grid_height_dim          #number of blocks
    nblocks = int(nblocks)
    print("nblocks: ",nblocks," block width: ",block_width," block height: ",block_height)
    print("image width: ",width," image height: ",height)
    print("getting all the blocks ...")
    blocks=[]
    thresh_blk = []
    # binary list of can we swap this block or can we not
    thresh_map = [] 
    
    arr_face = np.array(im)
    hsv = cv2.cvtColor(arr_face, cv2.COLOR_RGB2HSV)
    lower = np.array([1,1, 70])
    upper = np.array([220,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    res = cv2.bitwise_and(arr_face,arr_face, mask= mask)
    dst = cv2.fastNlMeansDenoisingColored(res,None,90,10,7,21)
    #plt.imshow(mask)
    im_thresh2 = Image.fromarray(dst)
    im_thresh = im_thresh2.point(lambda p: p > threshold and 255)  # threshold map
    for n in range(int(nblocks)): #get all the image blocks
        thresh_blk += [get_block(im_thresh,n,block_width,block_height)]
        threshtmp = np.sum(imstat.Stat(thresh_blk[n]).sum)
        if threshtmp > 0:
            blocks += [get_block(im,n,block_width,block_height)]
            thresh_map += [1]
        else:
            thresh_map += [0] 


        

    print("shuffling ...")
    #shuffle the order of the blocks
    #new_order=list(range(nblocks))
    new_order = list(range(np.sum(thresh_map)))
    for n in range(nshuffle):
        random.shuffle(new_order)

    print("building final image ...")
    new_image=im.copy()
    count = 0 # counter for the blocks! 
    err_cnt = 0
    for n in range(nblocks):
        # if this is a non-swap block don't bother 
        if thresh_map[n] > 0: 
            #define the target box where to paste the new block
            i=int((n%grid_width_dim)*block_width)                #i,j -> upper left point of the target image
            j=int((n//grid_width_dim)*block_height)
            box = (i,j,i+block_width,j+block_height)
            #check if this is an allowed location against threshold
            
            #paste it   
            try:
                new_image.paste(blocks[new_order[count]],box)
                count+= 1
            except:
                print('weird dimensions', box)
                err_cnt += 1
                x, y = blocks[new_order[count]].size
                box = (i,j,i+x,j+y)
                new_image.paste(blocks[new_order[count]],box)
                count+=1

    return new_image



#find the dimension(height or width) according to the desired granularity (a lower granularity small blocks)
def find_block_dim(granularity,dim):
    assert(granularity>0)
    candidate=0
    block_dim=1
    counter=0
    while counter!=granularity:         #while we dont achive the desired granularity
        candidate+=1
        while((dim%candidate)!=0):      
            candidate+=1
            if candidate>dim:
                counter=granularity-1
                break

        if candidate<=dim:
            block_dim=candidate         #save the current feasible lenght

        counter+=1

    assert(dim%block_dim==0 and block_dim<=dim)
    return int(block_dim)


#get a block of the image
def get_block(im,n,block_width,block_height):

    width=im.size[0]

    grid_width_dim=width/block_width                        #dimension of the grid

    i=(n%grid_width_dim)*block_width                        #i,j -> upper left point of the target block
    j=(n/grid_width_dim)*block_height

    box = (i,j,i+block_width,j+block_height)
    block_im = im.crop(box)
    return block_im

#set random seed based on the given password
def set_seed(password):
    passValue=0
    for ch in password:                 
        passValue=passValue+ord(ch)
    random.seed(passValue)
