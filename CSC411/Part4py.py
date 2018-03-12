import numpy as np
from numpy import random
import os


def grad_descent(f, df, x, t, init_W, alpha):
    """
    the gradient descent function without momentum
    """
    #performanceM = array([])
    #performanceMTest = array([])
    EPS = 1e-5   #EPS = 10**(-5)
    prev_W = init_W-10*EPS
    W = init_W.copy()
    max_iter = 3000
    iter  = 0
    while norm(W - prev_W) >  EPS and iter < max_iter:
        prev_W = W.copy()
        W -= alpha*df(x, t, W)
        #performanceM = np.append(performanceM,performance(W,x,t))
        #performanceMTest = np.append(performanceMTest,performance(W,xTest,tTest))
        if iter % 100 == 0:
            print "Iter", iter
            print f(x,t,W)
            print "Gradient: ", sum(df(x, t, W))
            #print "Train Performance:", performanceM[iter]
            #print "Test Perofrmance:", performanceMTest[iter]
        iter += 1
    return W #, performanceM, performanceMTest


def sigmoid(o):
    """
    sigmoid function
    """
    y = 1/(1+np.exp(-o))
    return y

def loss_fn(y, t):
    """
    loss function
    """
    return sum(-t*np.log(y) - (1-t)*np.log(1-y))


def f(x,t,W):
    """
    combined function of forward part
    """
    o = np.dot(x,W.T)
    y = sigmoid(o)
    return loss_fn(y, t)

def df(x,t,W):
    """
    combined function of back propagation part
    """
    o = np.dot(x,W.T)
    y = sigmoid(o)
    lossGradient = y-t
    combined_grad = np.dot(lossGradient.T, x)
    return combined_grad

def performance(trainedW,x,t):
    """
    evaluate the performance of the learning
    """
    o = np.dot(x,trainedW.T)
    y = sigmoid(o)
    corrNum = 0
    for i in range(y.shape[0]):
        if y[i,0] > 0.5:
            y[i,0] = 1
        else:
            y[i,0] = 0
    for i in range(y.shape[0]):
        if y[i,0] == t[i,0]:
            corrNum += 1
    return corrNum / y.shape[0]                

training_xy = np.load('training.npy')

X = training_xy[:-1,:].T
t = training_xy[-1, :].T

print t.shape
print X.shape

# construct W
np.random.seed(1)
W = np.random.normal(0, 0.0001, (1,5833))

trainedW = grad_descent(f, df, X, t, W, 0.0001)
# print the result
print("The accuracy rate for training set is:", performance(trainedW,X,t))

