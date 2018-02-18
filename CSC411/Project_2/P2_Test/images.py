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
from torch.utils.data import Dataset, DataLoader,TensorDataset
import hashlib

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

    return gray

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

def sha256_check(filename, block_size = 65536):
    """
    sha256 check sum
    """
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


# Part 8_1
# -----------------------------------------------------------------------------
"""
def part_1_imdl(source_file_name,folder_name,folder_name2,dim = 32):
    
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
                
                #sha256 check
                check = sha256_check(folder_name+filename)
                if not check == line.split()[6]:
                    print "SHA256 does not match! Delete file."
                    time.sleep(5)
                    try:
                        os.remove(folder_name+filename)
                    except:
                        print "Can not remove file!"
                    continue
    
                #crop and resize the images here
                try:
                    im = imread(folder_name+filename)
                except IOError:
                    print"Cannot read image"
                    time.sleep(5)
                    try:
                        os.remove(folder_name+filename)
                    except:
                        print "Can not remove file!"                 
                    continue
                
                crop = line.split("\t")[4].split(",")
                if im.ndim == 3:
                    imc = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2]),:]
                    result = rgb2gray(imresize(imc,(dim,dim)))
                else:
                    imc = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2])]
                    result = (imresize(imc,(dim,dim)))/255.
                #imsave("cropped_images/"+filename, result)
                plt.imsave(folder_name2+filename, result,cmap = cm.gray)
                
                print(filename)
                i += 1
"""
def part_1_imdl(source_file_name,folder_name,folder_name2):
    
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
                
                #sha256 check
                check = sha256_check(folder_name+filename)
                if not check == line.split()[6]:
                    print "SHA256 does not match! Delete file."
                    time.sleep(1)
                    try:
                        os.remove(folder_name+filename)
                    except:
                        print "Can not remove file!"
                    continue
    
                #crop and resize the images here
                try:
                    im = imread(folder_name+filename)
                except IOError:
                    print"Cannot read image"
                    time.sleep(1)
                    try:
                        os.remove(folder_name+filename)
                    except:
                        print "Can not remove file!"                 
                    continue
                
                crop = line.split("\t")[4].split(",")
                if im.ndim == 3:
                    result = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2]),:]
                else:
                    result = im[int(crop[1]):int(crop[3]),int(crop[0]):int(crop[2])]
                #imsave("cropped_images/"+filename, result)
                plt.imsave(folder_name2+filename, result,cmap = cm.gray)
                
                print(filename)
                i += 1
                
def get_imag_num(source_file_names, foldername):
    
    image_names = os.listdir('./'+foldername)
    image_num = {}
    #get the name of actors
    act = []
    for source_file_name in source_file_names:
        act+=list(set([a.split("\t")[0] for a in open(source_file_name).readlines()]))
    
    for a in act:
        name = a.split()[1].lower()
        i = -1
        for image in image_names:
            if name in image:
                i += 1
        image_num[name] = i
    return image_num
        
def delete_imag(folder_name, image_num, delete_images):
    num = image_num.copy()
    
    for delete_image in delete_images:
        time.sleep(5)
        try:
            os.remove(folder_name+delete_image)
        except:
            print "Can not remove file!"
            break
        for name in num.keys():
            if name in delete_image:
                try:
                    os.rename(folder_name+name+str(num[name])+".jpg",folder_name+delete_image.split(".")[0]+".jpg")
                except:
                    try:
                        os.rename(folder_name+name+str(num[name])+".JPG",folder_name+delete_image.split(".")[0]+".JPG")
                    except:
                        try:
                            os.rename(folder_name+name+str(num[name])+".jpeg",folder_name+delete_image.split(".")[0]+".jpeg")
                        except:
                            try:
                                os.rename(folder_name+name+str(num[name])+".JPEG",folder_name+delete_image.split(".")[0]+".JPEG")
                            except:
                                try:
                                    os.rename(folder_name+name+str(num[name])+".png",folder_name+delete_image.split(".")[0]+".png")
                                except:
                                    try:
                                        os.rename(folder_name+name+str(num[name])+".PNG",folder_name+delete_image.split(".")[0]+".PNG")
                                    except:  
                                        print "Can not rename file!"
                                        break
                num[name] -= 1

def get_faces():
    try:
        os.makedirs("cropped_images")
    except OSError:
        pass
    
    part_1_imdl("facescrub_actors.txt","actors_uncropped/","cropped_images/")
    part_1_imdl("facescrub_actresses.txt","actresses_uncropped/","cropped_images/")
    
    image_num = get_imag_num(["facescrub_actors.txt","facescrub_actresses.txt"], "cropped_images")
    
    #this is hard code part, do not run it twice!
    delete_imag("cropped_images/", image_num, ["chenoweth71.jpg","baldwin91.jpg","drescher69.jpg","drescher81.jpg","drescher31.jpg"])

def resize_faces(size,folder_name, need_gray = True):
    
    folder_name2 = "resized_images_"+str(size)+"/"
    try:
        os.makedirs(folder_name2)
    except OSError:
        pass
    
    image_names = os.listdir('./'+folder_name)
    
    for image_name in image_names:
        im = imread(folder_name+image_name)
        if need_gray:
            result = rgb2gray(imresize(im,(size,size)))
            plt.imsave(folder_name2+image_name, result, cmap = cm.gray)
        else:
            result = imresize(im,(size,size))
            plt.imsave(folder_name2+image_name, result)

if __name__ == "__main__":
    #Important Note: Please uncomment the following line when using an IDE!
    os.chdir(os.path.dirname(__file__))
    #get_faces()
    resize_faces(227,"cropped_images/", need_gray = False)
    resize_faces(32,"cropped_images/", need_gray = True)