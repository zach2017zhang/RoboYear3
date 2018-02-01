"""
Created on Tue Jan 16 00:14:57 2018

@author: yuchen
"""

from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import random
import time
from copy import deepcopy
from scipy.misc import imread
from scipy.misc import imresize
from scipy.misc import imsave
import matplotlib.image as mpimg
import os
from scipy.ndimage import filters
import urllib
from random import *


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
Create feature matrix X and corresponding label matrix Y
Take:
    classify_act: a dictionary stores the desired label of each actor
    desired_set: training / test / validation set
Return:
    feature: the feature matrix
    label: the label matrix
"""
def create_set(classify_act, desired_set):
    feature = np.array([])
    label = np.array([])
    feature = feature.reshape(1025,0)
    for a in classify_act.keys():
        for image in desired_set[a]:
            label = np.hstack((label,np.array([classify_act[a]])))
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
            im = np.vstack((np.array([1]),im))
            feature = np.hstack((feature,im))
    return feature,label


"""
Quadratic loss function and its gradient
Take:
Return:
"""
def f(x, y, theta):
    # theta = np.array([t1, t2, t3])
    return sum( (y - dot(theta.T,x)) ** 2)

def df(x, y, theta):
    return -2*sum((y-dot(theta.T, x))*x, 1)

"""
Gradient Descent
Take:
Return:
"""
def grad_descent(f, df, x, y, init_t, alpha=0.00001, max_iter=6000, EPS = 1e-5):
    #EPS = 1e-5   #EPS = 10**(-5)
    prev_t = init_t-10*EPS
    t = init_t.copy()
    iter  = 0
    while norm(t - prev_t) >  EPS and iter < max_iter:
        prev_t = t.copy()
        t -= alpha*df(x, y, t)
        #if iter % 500 == 0:
            #print "Iter", iter
            #print "f(x) = %.9f" % f(x, y, t)
            #print "Gradient: ", df(x, y, t), "\n"
        iter += 1
    return t
    
"""
Compute the output of the Classifier
Take:
    x: input
    theta: trained parameters
    anti_classify_act: a dictionary that stores the correct label of each actor
        example: {-1 : 'Alec Baldwin', 1:'Steve Carell'}
Return:
    result: output of the classifier
    
"""
def output(x,theta,anti_classify_act):
    result = []
    for k in np.matmul(theta,x):
        if k > 0 :
            result.append(anti_classify_act[1])
        else:
            result.append(anti_classify_act[-1])
    return result


"""
Compute the number of correctly classified pictures
Return:
    result: number of correctly classified pictures for each actor in a dictionary
    
"""
def performance_detail(feature, theta, label, anti_classify_act):
    result = {}
    for a in anti_classify_act.values():
        result[a] = 0
    classification = output(feature,theta,anti_classify_act)
    for i in range(label.size):
        if classification[i] == anti_classify_act[label[i]]:
            result[anti_classify_act[label[i]]]+=1
    return result

"""
Compute the performance (accuracy) of the classifier
Return:
    result: accuracy of the classifier on the input set
"""
def performance(feature, theta, label, anti_classify_act):
    detail = performance_detail(feature, theta, label, anti_classify_act)
    num_correct = 0.0
    for i in detail.keys():
        num_correct += detail[i]
    return num_correct / feature[0].size

# Part 1
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
                    print "Cannot read image"
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
                
                print filename
                i += 1
def part_1():
    print "Part 1"
    try:
        os.makedirs("cropped_images")
    except OSError:
        pass
    part_1_imdl("facescrub_actors.txt","actors_uncropped/")
    part_1_imdl("facescrub_actresses.txt","actresses_uncropped/")


# Part 2
# -----------------------------------------------------------------------------
"""
Separate the dataset into three non-overlapping parts: 
    the training set (100 UPDATE: 70 face images per actor), 
    the validation set (10 face images per actor), 
    and the test set (10 face images per actor).
Take:
Return:
    result: number of correctly classified pictures
"""
def part_2(seed=0):
    
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    
    set_size_pact = 90
    vsize_pact = 10
    tsize_pact = 10
    
    training_set,validation_set,test_set = build_sets(act,act_num, set_size_pact,vsize_pact, tsize_pact,seed)
    
    return training_set,validation_set,test_set

# Part 3
# -----------------------------------------------------------------------------
"""
Build a classifier to distinguish pictures of Alec Baldwin form pictures of Steve Carell
Take:
Return:
    result: number of correctly classified pictures
"""
def part_3_classifier(seed=0):
    training_set,validation_set,test_set = part_2(seed)
    classify_act = {'Alec Baldwin' : -1, 'Steve Carell' : 1}

    data,dlabel = create_set(classify_act, training_set)
    test,tlabel = create_set(classify_act, test_set)
    validation,vlabel = create_set(classify_act, validation_set)
    
    return data,dlabel,test,tlabel,validation,vlabel

"""
Gradient Descent
Take:
Return:
"""
def part_3_grad_descent(f, df, x, y, init_t, alpha=0.00001, max_iter=6000,recording_step=500, EPS = 1e-5):
    iter_num = []
    f_value = []
    prev_t = init_t-10*EPS
    t = init_t.copy()
    iter  = 0
    initf = f(x, y, init_t)
    while norm(t - prev_t) >  EPS and iter < max_iter and f(x, y, t)<=initf*2:
        prev_t = t.copy()
        t -= alpha*df(x, y, t)
        if iter % recording_step == 0:
            f_value.append(f(x, y, t))
            iter_num.append(iter)
            #print "Iter", iter
            #print "f(x) = %.9f" % f(x, y, t)
            #print "Gradient: ", df(x, y, t), "\n"
        iter += 1
    return t, f_value, iter_num

"""
Build a classifier to distinguish pictures of Alec Baldwin form pictures of Steve Carell
Take:
Return:
    result: number of correctly classified pictures
"""
def part_3():
    print "Part 3"
    
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    data,dlabel,test,tlabel,validation,vlabel = part_3_classifier()
    anti_classify_act = {-1 : 'Alec Baldwin', 1:'Steve Carell'}
    
    # -------------------------------------------------------------------------
    print "Tune Learning Rate #1"
    plt.figure(1)
    theta0 = np.random.normal(0,0.,1025)
    legend = []
    max_iter = 100
    recording_step = 20
    for alpha in [0.000001*x for x in range(16,26,2)]:
        theta,f_value,iter_num = part_3_grad_descent(f, df, data, dlabel, theta0, alpha, max_iter,recording_step)
        plt.plot(iter_num, f_value,'^-')
        legend.append("alpha = "+str(alpha))
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Cost Function Value on Training Set')
    plt.savefig('figures/part3f1.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "\nTune Learning Rate #2"
    plt.figure(2)
    theta0 = np.random.normal(0,0.,1025)
    legend = []
    max_iter = 1000
    recording_step = 200
    for alpha in [0.000001*x for x in range(12,24,2)]:
        theta,f_value,iter_num = part_3_grad_descent(f, df, data, dlabel, theta0, alpha, max_iter,recording_step)
        plt.plot(iter_num, f_value,'^-')
        legend.append("alpha = "+str(alpha))
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Cost Function Value on Training Set')
    plt.savefig('figures/part3f2.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "\nTheta Initialization"
    np.random.seed(0)
    for i in [0.,0.0001,0.001,0.01,0.1,1]:
        f_value = []
        for j in range(5):
            theta0 = np.random.normal(0,i,1025)
            f_value.append((f(data, dlabel, theta0)))
        print "Initial value of cost function on the training set with standard deviation of theta to be %.4f : Mean: f(x) = %.2f  Standard Error: %.2f" % (i, np.mean(f_value), np.std(f_value))
    
    # -------------------------------------------------------------------------
    print "\nReport the values of the cost function on the training and the validation sets"
    print "Report performance on the training and the validation sets\n"
    alpha = 0.000015
    max_iter = 100000
    cost_t = []
    cost_v = []
    perf_t = []
    perf_v = []
    for seed in range(5):
        theta0 = np.random.normal(0,0.,1025)
        data,dlabel,test,tlabel,validation,vlabel = part_3_classifier(seed)
        theta = grad_descent(f, df, data, dlabel, theta0, alpha, max_iter)
        cost_t.append(f(data, dlabel, theta)/(2*dlabel.size))
        cost_v.append(f(validation, vlabel, theta)/(2*vlabel.size))

    # -------------------------------------------------------------------------
        perf_t.append(performance(data, theta, dlabel, anti_classify_act)*100)
        perf_v.append(performance(validation, theta, vlabel, anti_classify_act)*100)
    print "Value of cost function on the training set: f(x) = %f +/- %f" % (np.mean(cost_t),np.std(cost_t))
    print "Value of cost function on the validation set: f(x) = %f +/- %f" % (np.mean(cost_v),np.std(cost_v))
    print "Performance of the classifier on the training set:  %.2f%% +/- %f%%" % (np.mean(perf_t),np.std(perf_t))
    print "Performance of the classifier on the validation set:  %.2f%% +/- %f%% \n" % (np.mean(perf_v),np.std(perf_v))
# Part 4
# -----------------------------------------------------------------------------
"""
Display image Gradient Descent produced
Take:
Return:
"""
def part_4a():
    print "Part 4a"
        
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    classify_act = {'Alec Baldwin' : -1, 'Steve Carell' : 1}
    set_size_pact = 90
    vsize_pact = 10
    tsize_pact = 10
    
    # -------------------------------------------------------------------------
    print "Display the thetas obtained by training using the full training dataset"
    training_set,validation_set,test_set = build_sets(act,act_num, set_size_pact,vsize_pact, tsize_pact)
    data,dlabel = create_set(classify_act, training_set)

    theta0 = np.random.normal(0,0.0,1025)
    alpha = 0.000015
    max_iter = 100000
    theta = grad_descent(f, df, data, dlabel, theta0, alpha, max_iter)
    plt.imshow((theta[1:]).reshape(32,32), cmap=cm.gray)
    plt.savefig('figures/part4f1.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "Display the thetas obtained by training using a training set that contains only two images of each actor"
    training_set = resize_set(training_set, 2)
    data,dlabel = create_set(classify_act, training_set)
    
    theta0 = np.random.normal(0,0.0,1025)
    alpha = 0.000015
    max_iter = 100000
    theta = grad_descent(f, df, data, dlabel, theta0, alpha, max_iter)
    plt.imshow((theta[1:]).reshape(32,32), cmap=cm.gray)
    plt.savefig('figures/part4f2.jpg')
    plt.show()
    
    
"""
Display image Gradient Descent produced
Take:
Return:
"""
def part_4b():
    print "Part 4b"
        
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    data,dlabel,test,tlabel,validation,vlabel = part_3_classifier()
    
    # -------------------------------------------------------------------------
    print "Initializing the thetas with different standard deviation"
    alpha = 0.000015
    max_iter = 1000
    np.random.seed(0)
    figure = 3
    for i in [0.,0.1]:
        theta0 = np.random.normal(0,i,1025)
        print "The standard deviation of initialized theta is %.4f" % i
        theta = grad_descent(f, df, data, dlabel, theta0, alpha, max_iter)
        #plt.figure(figure)
        plt.imshow((theta[1:]).reshape(32,32), cmap=cm.gray)
        plt.savefig('figures/part4f'+str(figure)+'.jpg')
        plt.show()
        figure +=1
        
    # -------------------------------------------------------------------------
    print "\nStopping the Gradient Descent process earlier and later in the process"
    theta0 = np.random.normal(0,0.0,1025)
    alpha = 0.000015
    for max_iter in [100,10000]:
        print "The maximum number of iterations is %d" % max_iter
        theta = grad_descent(f, df, data, dlabel, theta0, alpha, max_iter)
        plt.imshow((theta[1:]).reshape(32,32), cmap=cm.gray)
        plt.savefig('figures/part4f'+str(figure)+'.jpg')
        plt.show()
        figure +=1

# Part 5
# -----------------------------------------------------------------------------
"""
Display image Gradient Descent produced
Take:
Return:
"""
def part_5_diff_training_set_size(trsize_pact,vsize_pact,tsize_pact):
    
    #build training&validation set
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    training_set,validation_set,test_set1 = build_sets(act,act_num, trsize_pact+vsize_pact,vsize_pact, 0)
    
    #build test set
    act = ['Kristin Chenoweth', 'Fran Drescher', 'America Ferrera', 'Daniel Radcliffe', 'Gerard Butler', 'Michael Vartan']
    act_num = {'Kristin Chenoweth':171, 'Fran Drescher':169, 'America Ferrera':180, 'Daniel Radcliffe':145, 'Gerard Butler':140, 'Michael Vartan':138} 
    training_set1,validation_set1,test_set = build_sets(act,act_num, tsize_pact,0, tsize_pact)
    
    #training and validation set
    classify_act1 = {'Lorraine Bracco':-1, 'Peri Gilpin':-1, 'Angie Harmon':-1, 'Alec Baldwin':1, 'Bill Hader':1, 'Steve Carell':1}
    #build test set
    classify_act2 = {'Kristin Chenoweth':-1, 'Fran Drescher':-1, 'America Ferrera':-1, 'Daniel Radcliffe':1, 'Gerard Butler':1, 'Michael Vartan':1}
    
    data,data_label = create_set(classify_act1, training_set)
    validation,vlabel = create_set(classify_act1, validation_set)
    test,tlabel = create_set(classify_act2, test_set)
    
    return data,data_label,validation,vlabel,test,tlabel

def part_5():
    print "Part 5"
        
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    classify_act1 = {'Lorraine Bracco':-1, 'Peri Gilpin':-1, 'Angie Harmon':-1, 'Alec Baldwin':1, 'Bill Hader':1, 'Steve Carell':1}
    classify_act2 = {'Kristin Chenoweth':-1, 'Fran Drescher':-1, 'America Ferrera':-1, 'Daniel Radcliffe':1, 'Gerard Butler':1, 'Michael Vartan':1}
    
    anti_classify_act = {-1: 'female', 1:'male'}
    
    training_set_size = []
    perform_test_mean = []
    perform_validation_mean = []
    perform_training_mean = []
    perform_test_err = []
    perform_validation_err = []
    perform_training_err = []
    
    
    #Method 1
    act = ['Kristin Chenoweth', 'Fran Drescher', 'America Ferrera', 'Daniel Radcliffe', 'Gerard Butler', 'Michael Vartan']
    act_num = {'Kristin Chenoweth':171, 'Fran Drescher':169, 'America Ferrera':180, 'Daniel Radcliffe':145, 'Gerard Butler':140, 'Michael Vartan':138} 
    training_set_not_used,validation_set_not_used,test_set = build_sets(act,act_num, 10,0, 10)
    test,tlabel = create_set(classify_act2, test_set)
    
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    alpha = 0.000005
    max_iter = 10000
    
    print "Report performance on the test set:"

    for i in range(10,80,10):
        perform_test = []
        perform_validation = []
        perform_training = []
        training_set_size.append(i*6)
        for j in range(10):
            training_set,validation_set,test_set_not_used = build_sets(act,act_num, i+10,10, 0,j)
            validation,vlabel = create_set(classify_act1, validation_set)
            data,data_label = create_set(classify_act1, training_set)

            theta0 = np.random.normal(0,0.0,1025)
            theta = grad_descent(f, df, data, data_label, theta0, alpha,max_iter)
            perform_test.append(performance(test, theta, tlabel, anti_classify_act))
            perform_training.append(performance(data, theta, data_label, anti_classify_act))
            perform_validation.append(performance(validation, theta, vlabel, anti_classify_act))
        
        perform_test_mean.append(np.mean(perform_test))
        perform_validation_mean.append(np.mean(perform_validation))
        perform_training_mean.append(np.mean(perform_training))
        
        perform_test_err.append(np.std(perform_test))
        perform_validation_err.append(np.std(perform_validation))
        perform_training_err.append(np.std(perform_training))
        
        print "Performance on the test set is %f+/-%f when training set size is %d." %(np.mean(perform_test),np.std(perform_test),i*6)
    
    plt.errorbar(training_set_size,perform_test_mean,yerr=perform_test_err,fmt='r.-')
    plt.errorbar(training_set_size,perform_validation_mean,yerr=perform_validation_err,fmt='g.-')
    plt.errorbar(training_set_size,perform_training_mean,yerr=perform_training_err,fmt='b.-')
    plt.xlabel('Training Set Size')
    plt.ylabel('Performance')
    plt.legend(['test', 'validation','training'])
    plt.savefig('figures/part5f1.jpg')
    plt.show()
        
# Part 6
# -----------------------------------------------------------------------------
"""
Quadratic loss function and its gradient for part 6
"""
def part_6_f(x, y, theta):
    cost = np.matmul(theta.transpose(),x)-y 
    return np.trace(np.matmul(cost,cost.transpose()))

def part_6_df(x, y, theta):
    cost = np.matmul(theta.transpose(),x)-y 
    return 2*np.matmul(x,cost.transpose())

"""
Create feature matrix X and corresponding label matrix Y for part 6
Take:
    classify_act: a dictionary stores the desired label of each actor
    desired_set: training / test / validation set
Return:
    feature: the feature matrix
    label: the label matrix
"""
def part_6_create_set(classify_act, desired_set):
    feature = np.array([])
    label = np.array([])
    feature = feature.reshape(1025,0)
    label = label.reshape(6,0)
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
            im = np.vstack((np.array([1]),im))
            feature = np.hstack((feature,im))
    return feature,label

"""
Compute the gradient component theta_pq
Take:
    f: the cost function
    x: input features
    y: labels
    theta: weights
"""
def part_6d_finite_diff_approx(f,x,y,theta,h,p,q):
    thetah = theta.copy()
    thetah[p][q] += h
    return (f(x, y, thetah)-f(x, y, theta))/h

"""
Compare the error of the pq component of gradient wrt theta between the finite 
difference approximation and value obtained from function in Part 6b
Take:
    f: the cost function
    x: input features
    y: labels
    theta: weights
    h: finite difference
    p and q: coordinates
"""
def part_6_d_error(f,x,y,theta,h,p,q):
    approx = part_6d_finite_diff_approx(f, x, y, theta,h,p,q)
    actual = part_6_df(x, y, theta)[p][q]
    #Compute the relative error between approximation and the actual value
    #The formula for relative error is error(a,b)=|a-b|/(|a|+|b|)
    error = np.abs(approx-actual)/(np.abs(approx)+np.abs(actual))
    return error

def part_6d_gradient_fda(f,x,y,theta,h,p,q):
    result = np.zeros((theta.shape[0],theta.shape[1]))
    for p in range(theta.shape[0]):
        for p in range(theta.shape[1]):
            result[p][q]=part_6d_finite_diff_approx(f,x,y,theta,h,p,q)
    return result

def part_6d():
    print "Part 6d"
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
    
    data,dlabel = part_6_create_set(classify_act, training_set)
    test,tlabel = part_6_create_set(classify_act, test_set)
    validation,vlabel = part_6_create_set(classify_act, validation_set)

    np.random.seed(0)
    
    mean_error = []
    std_error = []

    theta0 = np.random.normal(0,0.0,(1025,6))
    h = 1e-13
    for h in [10**x for x in range(-13,-5)]:
        error = []
        for i in range(10):
            p = int(round((theta0.shape[0]-1)*np.random.rand()))
            q = int(round((theta0.shape[1]-1)*np.random.rand()))
            error.append(part_6_d_error(part_6_f, data, dlabel, theta0,h,p,q))
        mean_error.append(np.mean(error))
        std_error.append(np.std(error))

    print "Select the value of h based on mean relative error between approximation and true gradient"
    f,ax = plt.subplots()
    ax.set_xscale("log", nonposx='clip')
    ax.set_yscale("log", nonposy='clip')
    ax.errorbar([10**x for x in range(-13,-5)],mean_error,yerr = std_error,fmt='.-')
    plt.xlabel('Value of h')
    plt.ylabel('Average Relative Error over 5 Coordinates')
    plt.savefig('figures/part6f1.jpg')
    plt.show()
    
# Part 7
# -----------------------------------------------------------------------------
"""
Gradient Descent
Take:
Return:
"""
def part_7_grad_descent(f, df, x, y, init_t, alpha=0.00001, max_iter=6000,recording_step=500, EPS = 1e-5):
    iter_num = [0]
    f_value = [f(x, y, init_t)]
    prev_t = init_t-10*EPS
    t = init_t.copy()
    iter  = 1
    initf = f(x, y, init_t)
    while norm(t - prev_t) >  EPS and iter < max_iter and f(x, y, t)<=initf*50:
        prev_t = t.copy()
        t -= alpha*df(x, y, t)
        if iter % recording_step == 0:
            f_value.append(f(x, y, t))
            iter_num.append(iter)
            #print "Iter", iter
            #print "f(x) = %.9f" % f(x, y, t)
            #print "Gradient: ", df(x, y, t), "\n"
        iter += 1
    return t, f_value, iter_num

def part_7_output(x,theta,anti_classify_act):
    result = []
    for k in np.transpose(np.matmul(theta.transpose(),x)):
        result.append(anti_classify_act[k.argmax()])
    return result

def part_7_performance_detail(feature, theta, label, anti_classify_act):
    desired_classification = []
    classification = []
    result = {}
    
    for k in label.transpose():
        desired_classification.append(anti_classify_act[k.argmax()])
    classification = part_7_output(feature,theta,anti_classify_act)
    
    for a in anti_classify_act.values():
        result[a] = 0
        
    for i in range(label[0].size):
        if classification[i] == desired_classification[i]:
            result[desired_classification[i]]+=1
    return result

"""
Compute the performance (accuracy) of the classifier
Take:
Return:
    result: number of correctly classified pictures
"""
def part_7_performance(feature, theta, label, anti_classify_act):
    detail = part_7_performance_detail(feature, theta, label, anti_classify_act)
    num_correct = 0.0
    for i in detail.keys():
        num_correct += detail[i]
    return num_correct / feature[0].size

def part_7():
    print "Part 7"
    try:
        os.makedirs('figures')
    except OSError:
        pass

    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    sets_size_pact = 80
    vsize_pact = 10
    tsize_pact = 0
    
    training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact)

    classify_act = {'Lorraine Bracco':[[1],[0],[0],[0],[0],[0]], 'Peri Gilpin':[[0],[1],[0],[0],[0],[0]], 'Angie Harmon':[[0],[0],[1],[0],[0],[0]], 'Alec Baldwin':[[0],[0],[0],[1],[0],[0]], 'Bill Hader':[[0],[0],[0],[0],[1],[0]], 'Steve Carell':[[0],[0],[0],[0],[0],[1]]}
    anti_classify_act = {0:'Lorraine Bracco', 1:'Peri Gilpin', 2:'Angie Harmon', 3:'Alec Baldwin', 4:'Bill Hader', 5:'Steve Carell'}
    
    data,dlabel = part_6_create_set(classify_act, training_set)
    test,tlabel = part_6_create_set(classify_act, test_set)
    validation,vlabel = part_6_create_set(classify_act, validation_set)

    
    # -------------------------------------------------------------------------
    print "Tune Learning Rate #1"
    plt.figure(1)
    legend = []
    max_iter = 100
    recording_step = 20
    theta0 = np.random.normal(0,0.000,(1025,6))
    for alpha in [0.0000005*x for x in range(10,16,1)]:
        theta,f_value,iter_num = part_7_grad_descent(part_6_f, part_6_df, data, dlabel, theta0, alpha, max_iter,recording_step)
        plt.semilogy(iter_num, f_value,'^-')
        legend.append("alpha = "+str(alpha))
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Cost Function Value on Training Set')
    plt.savefig('figures/part7f1.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "\nTune Learning Rate #2"
    plt.figure(2)
    legend = []
    max_iter = 1000
    recording_step = 200
    theta0 = np.random.normal(0,0.000,(1025,6))
    for alpha in [0.0000005*x for x in range(10,15,1)]:
        theta,f_value,iter_num = part_7_grad_descent(part_6_f, part_6_df, data, dlabel, theta0, alpha, max_iter,recording_step)
        plt.plot(iter_num, f_value,'^-')
        legend.append("alpha = "+str(alpha))
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Cost Function Value on Training Set')
    plt.savefig('figures/part7f2.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "\nSelect Maximum Number of Iterations"
    
    training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact)    
    data,dlabel = part_6_create_set(classify_act, training_set)
    test,tlabel = part_6_create_set(classify_act, test_set)
    validation,vlabel = part_6_create_set(classify_act, validation_set)
    
    plt.figure(3)
    alpha = 0.000006
    theta0 = np.random.normal(0,0.000,(1025,6))
    performance = []
    performance_training = []
    maxiters = [10,100,1000,10000,50000]
    thetas = []
    for i in range(3):
        training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact,i)    
        data,dlabel = part_6_create_set(classify_act, training_set)
        test,tlabel = part_6_create_set(classify_act, test_set)
        validation,vlabel = part_6_create_set(classify_act, validation_set)
        performance.append([])
        performance_training.append([])
        for max_iter in maxiters:
            theta = grad_descent(part_6_f, part_6_df, data, dlabel, theta0, alpha, max_iter)
            performance[i].append(part_7_performance(validation, theta, vlabel, anti_classify_act))
            performance_training[i].append(part_7_performance(data, theta, dlabel, anti_classify_act))
    
    f,ax = plt.subplots()
    ax.set_xscale("log", nonposx='clip')
    ax.errorbar(maxiters, np.mean(performance,axis=0),yerr = np.std(performance,axis=0),fmt = '^-')
    plt.xlabel('Maximum Number of Iterations')
    plt.ylabel('Performance on the Validation Set')
    plt.savefig('figures/part7f3.jpg')
    plt.show()
    
    # -------------------------------------------------------------------------
    print "\nReport Performance (Choose best performance when number of maximum iteration = %i)" %(maxiters[argmax(np.mean(performance,axis=0))])
    print "Perform on the training set is : %f+/-%f" %(np.mean(performance_training,axis=0)[[argmax(np.mean(performance,axis=0))]],np.std(performance_training,axis=0)[[argmax(np.mean(performance,axis=0))]])
    print "Perform on the validation set is : %f+/-%f" %(np.mean(performance,axis=0)[[argmax(np.mean(performance,axis=0))]],np.std(performance,axis=0)[[argmax(np.mean(performance,axis=0))]])

# Part 8
# -----------------------------------------------------------------------------

def part_8():
    print "Part 8"
    try:
        os.makedirs('figures')
    except OSError:
        pass

    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    act_num = {'Lorraine Bracco':119, 'Peri Gilpin':87, 'Angie Harmon':127, 'Alec Baldwin':136, 'Bill Hader':139, 'Steve Carell':133}
    sets_size_pact = 80
    vsize_pact = 10
    tsize_pact = 0
    
    training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact)

    classify_act = {'Lorraine Bracco':[[1],[0],[0],[0],[0],[0]], 'Peri Gilpin':[[0],[1],[0],[0],[0],[0]], 'Angie Harmon':[[0],[0],[1],[0],[0],[0]], 'Alec Baldwin':[[0],[0],[0],[1],[0],[0]], 'Bill Hader':[[0],[0],[0],[0],[1],[0]], 'Steve Carell':[[0],[0],[0],[0],[0],[1]]}
    anti_classify_act = {0:'Lorraine Bracco', 1:'Peri Gilpin', 2:'Angie Harmon', 3:'Alec Baldwin', 4:'Bill Hader', 5:'Steve Carell'}

    data,dlabel = part_6_create_set(classify_act, training_set)
    test,tlabel = part_6_create_set(classify_act, test_set)
    validation,vlabel = part_6_create_set(classify_act, validation_set)

    theta0 = np.random.normal(0,0.0,(1025,6))
    
    alpha = 0.000006
    max_iter = 10000
    theta = grad_descent(part_6_f, part_6_df, data, dlabel, theta0, alpha ,max_iter)

    for i in range(6):
        plt.figure(i+1)
        plt.imshow((theta[1:,i]).reshape(32,32),interpolation='none', cmap=cm.gray)
        plt.show()
        print "Actor"+ str(i+1)+": " + anti_classify_act[dlabel[:,i*dlabel[0].size/(np.transpose(dlabel)[0].size)].argmax()]
        plt.imsave("figures/part8f"+str(i+1)+".jpg",(theta[1:,i]).reshape(32,32), cmap=cm.gray)

if __name__ == "__main__":
    #Important Note: Please uncomment the following line when using an IDE!
    #os.chdir(os.path.dirname(__file__))
    
    #Important Note: If want to run Part_1(), please make sure there is no folder named cropped_images under the same directory with this script
    #part_1()
    training_set_example,validation_set_example,test_set_example = part_2() #Check the return values of this function
    data,dlabel,test,tlabel,validation,vlabel = part_3_classifier(seed=0) #Check the return values of this function
    part_3()
    part_4a()
    part_4b()
    part_5()
    part_6d()
    part_7()
    part_8()

    
    