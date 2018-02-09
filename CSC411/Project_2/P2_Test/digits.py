from pylab import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import time
from scipy.misc import imread
from scipy.misc import imresize
import matplotlib.image as mpimg
from scipy.ndimage import filters
import urllib
from numpy import random

import cPickle

from scipy.io import loadmat

import os

# Constants
# -----------------------------------------------------------------------------
input_size = 28*28
num_digits = 10

# Functions used in multiple parts
# -----------------------------------------------------------------------------
def load_mnist():
    M = loadmat("mnist_all.mat")
    for i in range(num_digits):
        M['train'+str(i)]=M['train'+str(i)]/255.
        M['test'+str(i)]=M['test'+str(i)]/255.
    return M

def create_sets():
    M = load_mnist()
    training_x = np.empty((0,input_size))
    test_x = np.empty((0,input_size))
    training_y = np.empty((0,num_digits))
    test_y = np.empty((0,num_digits))
    for i in range(num_digits):
        training_x = np.vstack((training_x,M['train'+str(i)]))
        test_x = np.vstack((test_x,M['test'+str(i)]))
        temp_train_y = np.zeros((M['train'+str(i)].shape[0],num_digits))
        temp_train_y[:,i]=1
        training_y = np.vstack((training_y,temp_train_y))
        temp_test_y = np.zeros((M['test'+str(i)].shape[0],num_digits))
        temp_test_y[:,i]=1
        test_y = np.vstack((test_y,temp_test_y))
    return training_x, training_y, test_x, test_y

def softmax_forward(y):
    '''Return the output of the softmax function for the matrix of output y. y
    is an NxM matrix where N is the number of outputs for a single case, and M
    is the number of cases'''
    return exp(y)/tile(sum(exp(y),0), (len(y),1))
    
def tanh_layer(y, W, b):    
    '''Return the output of a tanh layer for the input matrix y. y
    is an NxM matrix where N is the number of inputs for a single case, and M
    is the number of cases'''
    return tanh(dot(W.T, y)+b)

def fully_connected_layer_forward(x,W,b):
    """
    Return fully connected layer 
    Input:
        x: N*M where M = 784
        W: 10*784
        b: 10*1
    Output:
        fully connected N*10
    """
    return np.matmul(W,x.T)+b

def softmax_backward(y,output):
    '''Return the output of the softmax function for the matrix of output y. y
    is an NxM matrix where N is the number of outputs for a single case, and M
    is the number of cases'''
    return output-y

def fully_connected_layer_backward(dy,x):
    """
    Return fully connected layer 
    Input:
        dy: 10*N
        x: N*M where M = 784    N*784
        W: 10*784
        b: 10*1
    Output:
        dW: 10*784
        db: 10*1
    """
    dW = np.matmul(dy,x)
    db = np.matmul(dy, np.ones([x.shape[0],1]))
    return dW,db

def NLL(y, output):
    return -sum(y*log(output)) 

# Part 1
# -----------------------------------------------------------------------------
def part1():
    """
    
    """
    try:
        os.makedirs("figures")
    except OSError:
        pass
    
    np.random.seed(0)
    
    #Load the MNIST digit data
    M = load_mnist()
    
    f, axarr = plt.subplots(10, 10)
    for i in range(10):
        np.random.shuffle(M["train"+str(i)])
        for j in range(10):
            axarr[i, j].imshow(M["train"+str(i)][j].reshape((28,28)), cmap=cm.gray)
            axarr[i, j].axes.get_xaxis().set_visible(False)
            axarr[i, j].axes.get_yaxis().set_visible(False)
    plt.savefig('figures/part1f1.jpg')
    plt.show()
    
# Part 2
# -----------------------------------------------------------------------------    
def part2_forward(x, W1, b1):
    L1 = fully_connected_layer_forward(x,W1,b1)
    output = softmax_forward(L1)
    return L1, output

def part2():
    
    #create weights
    W1 = np.random.normal(0.,0.5,[num_digits,input_size])
    b1 = np.random.normal(0.,0.5,[num_digits,1])
    
    #Load the MNIST digit data
    M = load_mnist()
    x = M["train5"][148:149]
    
    L1, output = part2_forward(x, W1, b1)
    #get the index at which the output is the largest
    print x.shape
    print L1
    print output

# Part 3
# -----------------------------------------------------------------------------
def part3_backward(y,output,x):
    dy = softmax_backward(y,output)
    dW,db = fully_connected_layer_backward(dy,x)
    print dW.shape
    print db.shape
    return dW, db
    
def part3_grad_check(training_x, training_y, test_x, test_y):
    
    h = 0.0000001
    
    W1 = np.random.normal(0.,0.5,[num_digits,input_size])
    b1 = np.random.normal(0.,0.5,[num_digits,1])
    
    L1_1, output_1 = part2_forward(training_x, W1, b1)
    
    dW,db = part3_backward(training_y.T,output_1,training_x)
    
    print db[5]
    
    b1[5] += h
    L1_2, output_2 = part2_forward(training_x, W1, b1)
    
    finite_diff = (NLL(training_y.T, output_2)-NLL(training_y.T, output_1))/h
    
    print finite_diff
    
    return 0

def part3():
    #Load the MNIST digit data
    training_x, training_y, test_x, test_y = create_sets()
      
    #create weights
    np.random.seed(0)
    part3_grad_check(training_x, training_y, test_x, test_y)
 
# Part 4
# -----------------------------------------------------------------------------
def part4_forward(x, Wb):
    W1 = Wb[:,:-1]
    b1 = Wb[:,-1:]
    L1 = fully_connected_layer_forward(x,W1,b1)
    output = softmax_forward(L1)
    return output

def part4_backward(y,output,x):
    dy = softmax_backward(y,output)
    dW,db = fully_connected_layer_backward(dy,x)
    return np.hstack((dW, db))

def part4_grad_descent(f, df, loss, x, y, init_t, alpha=0.0001, max_iter=3000, EPS = 1e-5):
    prev_t = init_t-10*EPS
    t = init_t.copy()
    currloss = loss(y, f(x,t))
    curr_alpha = alpha
    iter  = 0
    while norm(t - prev_t) >  EPS and iter < max_iter:
        prev_t = t.copy()
        t -= curr_alpha*df(y, f(x,t), x)
        if iter % 500 == 0:
            print "Iter", iter
            if currloss < loss(y, f(x,t)):
                curr_alpha = curr_alpha/2
            currloss = loss(y, f(x,t))
            print currloss
            #print "Gradient: ", df(x, y, t), "\n"
        iter += 1
    return t

def part4_performance(x, y,Wb):
    output = part4_forward(x,Wb)
    result = 0
    print output.T.shape
    print y.shape
    for i in range(10000):
        if argmax(output.T[i]) == argmax(y[i]):
            result+=1
    print "\nPerformance: "
    print result
    print "/10000\n"

def part4():
    #Load the MNIST digit data
    training_x, training_y, test_x, test_y = create_sets()     
    #create weights
    np.random.seed(0)
    Wb = np.random.normal(0.,0.5,[num_digits,input_size+1])
    part4_performance(test_x, test_y,Wb)
    trained_Wb = part4_grad_descent(part4_forward, part4_backward, NLL, training_x, training_y.T, Wb)
    part4_performance(test_x, test_y,trained_Wb)

# Part 5
# -----------------------------------------------------------------------------

def part5_grad_descent(f, df, loss, x, y, init_t, alpha=0.0001, max_iter=3000, EPS = 1e-5, damping = 0.9):
    v = 0
    prev_t = init_t-10*EPS
    t = init_t.copy()
    currloss = loss(y, f(x,t))
    curr_alpha = alpha
    iter  = 0
    while norm(t - prev_t) >  EPS and iter < max_iter:
        prev_t = t.copy()
        v = damping*v+curr_alpha*df(y, f(x,t), x)
        t -= v
        if iter % 500 == 0:
            print "Iter", iter
            if currloss < loss(y, f(x,t)):
                curr_alpha = curr_alpha/2
            currloss = loss(y, f(x,t))
            print currloss
            #print "Gradient: ", df(x, y, t), "\n"
        iter += 1
    return t

def part5():
    #Load the MNIST digit data
    training_x, training_y, test_x, test_y = create_sets()     
    #create weights
    np.random.seed(0)
    Wb = np.random.normal(0.,0.5,[num_digits,input_size+1])
    part4_performance(test_x, test_y,Wb)
    trained_Wb = part5_grad_descent(part4_forward, part4_backward, NLL, training_x, training_y.T, Wb)
    part4_performance(test_x, test_y,trained_Wb)   
    
if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    #part1()
    #part2()
    #part3()
    part4()
    part5()
    