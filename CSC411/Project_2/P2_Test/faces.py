#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 01:55:50 2018

@author: yuchen
"""
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import time
from copy import deepcopy
from scipy.misc import imread
from scipy.misc import imresize
from scipy.misc import imsave
import matplotlib.image as mpimg
import os
from scipy.ndimage import filters
import urllib
from torch.autograd import Variable
import torch
from scipy.io import loadmat

# Constants
# -----------------------------------------------------------------------------

# Functions used in multiple parts
# -----------------------------------------------------------------------------
def rgb2gray(rgb):
    '''Return the grayscale version of the RGB image rgb as a 2D numpy array
    whose range is 0..1
    Arguments:
    rgb -- an RGB image, represented as a numpy array of size n x m x 3. The
    range of the values is 0..255
    '''
    
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray/255.

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    '''From:
    http://code.activestate.com/recipes/473878-timeout-function-using-threading/'''
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return False
    else:
        return it.result

"""
A randomized algorithm that builds training, validation and test set
Take:
    act: a list of full name of actors
    act_num: a dictionary stores available pictures of each actor
    sets_size_pact: total number of pictures of training+validation+test set for each actor
    vsize_pact: number of pictures in validation set for each actor
    tsize_pact: number of pictures in test set for each actor
Return:
    training_set: a dictionary stores pictures used in training set
    validation_set: a dictionary stores pictures used in validation set
    test_set: a dictionary stores pictures used in test set
"""
def build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact,seed=0):
    training_set = {}
    validation_set = {}
    test_set = {}
    np.random.seed(seed)
    for a in act:
        name = a.split()[1].lower()
        training_set[a] = [name+str(x) for x in range(act_num[a])]
        validation_set[a] = []
        test_set[a] = []
        total_num = act_num[a]
        i = act_num[a]-sets_size_pact
        while i >0:
            pop_index = int(round((total_num-1)*np.random.rand()))
            pop_im = training_set[a].pop(pop_index)
            i -= 1
            total_num-=1
        i = vsize_pact
        while i >0:
            pop_index = int(round((total_num-1)*np.random.rand()))
            pop_im = training_set[a].pop(pop_index)
            validation_set[a].append(pop_im)
            i -= 1
            total_num-=1
        i = tsize_pact
        while i >0:
            pop_index = int(round((total_num-1)*np.random.rand()))
            pop_im = training_set[a].pop(pop_index)
            test_set[a].append(pop_im)
            i -= 1
            total_num-=1
    return training_set,validation_set,test_set

"""
Resize a set to a smaller size
Take:
    set_for_resizing:
    desired_num_pact
Return:
    resized_set
"""
def resize_set(set_for_resizing, desired_num_pact,seed=0):
    resized_set = deepcopy(set_for_resizing)
    np.random.seed(seed)
    for a in resized_set.keys():
        total_num = len(resized_set[a])
        i = len(resized_set[a])-desired_num_pact
        while i >0:
            pop_index = int(round((total_num-1)*np.random.rand()))
            pop_im = resized_set[a].pop(pop_index)
            i -= 1
            total_num-=1
    return resized_set


"""
Create feature matrix X and corresponding label matrix Y for part 6
Take:
    classify_act: a dictionary stores the desired label of each actor
    desired_set: training / test / validation set
Return:
    feature: the feature matrix
    label: the label matrix
"""
def create_set(classify_act, desired_set):
    feature = np.empty((1024,0))
    label = np.empty((6,0))
    for a in classify_act.keys():
        for image in desired_set[a]:
            label = np.hstack((label,np.array(classify_act[a])))
            try:
                im = imread("cropped_images/"+image+".jpg")
            except IOError:
                try:
                    im = imread("cropped_images/"+image+".jpeg")
                except IOError:
                    try:
                        im = imread("cropped_images/" + image + ".JPG")
                    except IOError:
                        try:
                            im = imread("cropped_images/" + image + ".PNG")
                        except IOError:
                            try:
                                im = imread("cropped_images/" + image + ".JPEG")
                            except IOError:
                                im = imread("cropped_images/"+image+".png")
            im = (im/255.).reshape(1024,1)
            feature = np.hstack((feature,im))
    return feature.T,label.T

# Part 8_1
# -----------------------------------------------------------------------------
def part_1_imdl(source_file_name,folder_name):
    
    try:
        os.makedirs(folder_name)
    except OSError:
        pass
    
    #get the name of actors
    act = list(set([a.split("\t")[0] for a in open(source_file_name).readlines()]))
    
    testfile = urllib.URLopener()            
    
    #Note: you need to create the uncropped folder first in order 
    #for this to work
    
    for a in act:
        name = a.split()[1].lower()
        i = 0
        for line in open(source_file_name):
            if a in line.split("\t"):
                filename = name+str(i)+'.'+line.split()[4].split('.')[-1]
                #A version without timeout (uncomment in case you need to 
                #unsupress exceptions, which timeout() does)
                #testfile.retrieve(line.split()[4], "actors_uncropped/"+filename)
                #timeout is used to stop downloading images which take too long to download
                timeout(testfile.retrieve, (line.split()[4], folder_name+filename), {}, 30)
                if not os.path.isfile(folder_name+filename):
                    continue
    
                #crop and resize the images here
                try:
                    im = imread(folder_name+filename)
                except IOError:
                    os.remove(folder_name+filename)
                    print("Cannot read image")
                    continue
                
                crop = line.split("\t")[4].split(",")
                if im.ndim == 3:
                    imc = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2]),:]
                    result = rgb2gray(imresize(imc,(32,32)))
                else:
                    imc = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2])]
                    result = (imresize(imc,(32,32)))/255.
                #imsave("cropped_images/"+filename, result)
                plt.imsave("cropped_images/"+filename, result,cmap = cm.gray)
                
                print(filename)
                i += 1
def part8_1():
    try:
        os.makedirs("cropped_images")
    except OSError:
        pass
    part_1_imdl("facescrub_actors.txt","actors_uncropped/")
    part_1_imdl("facescrub_actresses.txt","actresses_uncropped/")

# Part 8_2
# -----------------------------------------------------------------------------
def part8_2():
    print ("Part 6d")
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    sets_size_pact = 80
    vsize_pact = 10
    tsize_pact = 10
    
    training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact)

    classify_act = {'Lorraine Bracco':[[1],[0],[0],[0],[0],[0]], 'Peri Gilpin':[[0],[1],[0],[0],[0],[0]], 'Angie Harmon':[[0],[0],[1],[0],[0],[0]], 'Alec Baldwin':[[0],[0],[0],[1],[0],[0]], 'Bill Hader':[[0],[0],[0],[0],[1],[0]], 'Steve Carell':[[0],[0],[0],[0],[0],[1]]}
    anti_classify_act = {0:'Lorraine Bracco', 1:'Peri Gilpin', 2:'Angie Harmon', 3:'Alec Baldwin', 4:'Bill Hader', 5:'Steve Carell'}
    
    data,dlabel = create_set(classify_act, training_set)
    test,tlabel = create_set(classify_act, test_set)
    validation,vlabel = create_set(classify_act, validation_set)
    
    return data,dlabel,test,tlabel,validation,vlabel 

# Part 8_3
# -----------------------------------------------------------------------------
def part8_3(data,dlabel,test,tlabel,validation,vlabel):
    
    dim_x = 32*32
    dim_h = 20
    dim_out = 6
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor 
    
    x = Variable(torch.from_numpy(data), requires_grad=False).type(dtype_float)
    y_classes = Variable(torch.from_numpy(np.argmax(dlabel, 1)), requires_grad=False).type(dtype_long)
    
    model = torch.nn.Sequential(
            torch.nn.Linear(dim_x, dim_h),
            torch.nn.ReLU(),
            torch.nn.Linear(dim_h, dim_out),
            )
    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 1e-4
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    for t in range(10000):
        y_pred = model(x)
        loss = loss_fn(y_pred, y_classes)
        
        model.zero_grad()  # Zero out the previous gradient computation
        loss.backward()    # Compute the gradient
        optimizer.step()   # Use the gradient information to 
        
    x = Variable(torch.from_numpy(test), requires_grad=False).type(dtype_float)
    y_pred = model(x).data.numpy()
    print (np.mean(np.argmax(y_pred, 1) == np.argmax(tlabel, 1)))
   
if __name__ == "__main__":
    #Important Note: Please uncomment the following line when using an IDE!
    os.chdir(os.path.dirname(__file__))
    data,dlabel,test,tlabel,validation,vlabel =part8_2()
    part8_3(data,dlabel,test,tlabel,validation,vlabel)

# Test Code
# -----------------------------------------------------------------------------
