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
def build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact,seed=0, same_num_pact = False):

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
        if same_num_pact:
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
Create feature matrix X and corresponding label matrix Y for part 6
Take:
    classify_act: a dictionary stores the desired label of each actor
    desired_set: training / test / validation set
Return:
    feature: the feature matrix
    label: the label matrix
"""
def create_set(classify_act, desired_set,foldername = "resized_images_32/",dim=32):
    feature = np.empty((dim*dim,0))
    label = np.empty((6,0))
    for a in classify_act.keys():
        for image in desired_set[a]:
            label = np.hstack((label,np.array(classify_act[a])))
            try:
                im = imread(foldername+image+".jpg")
            except IOError:
                try:
                    im = imread(foldername+image+".jpeg")
                except IOError:
                    try:
                        im = imread(foldername + image + ".JPG")
                    except IOError:
                        try:
                            im = imread(foldername + image + ".PNG")
                        except IOError:
                            try:
                                im = imread(foldername + image + ".JPEG")
                            except IOError:
                                im = imread(foldername+image+".png")
            try:
                im = (im/255.).reshape(dim*dim,1)
            except:
                try:
                    im = (im[:,:,0]/255.).reshape(dim*dim,1)
                except:
                    print ("Cannot reshape image.")
            feature = np.hstack((feature,im))
    return feature.T,label.T

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

# Part 8_1
# -----------------------------------------------------------------------------
def part8_1(dimension = 32):
    
    print "Running Part 8 1"
    
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    full_image_num = get_imag_num(["facescrub_actors.txt","facescrub_actresses.txt"], "resized_images_32/")
    act =['Lorraine Bracco', 'Peri Gilpin', 'Angie Harmon', 'Alec Baldwin', 'Bill Hader', 'Steve Carell']
    
    act_num = {}
    
    for a in act:
        act_num[a] = full_image_num[a.split()[1].lower()]
        
    sets_size_pact = 50
    vsize_pact = 10
    tsize_pact = 20
    
    training_set,validation_set,test_set = build_sets(act,act_num, sets_size_pact,vsize_pact, tsize_pact)

    classify_act = {'Lorraine Bracco':[[1],[0],[0],[0],[0],[0]], 'Peri Gilpin':[[0],[1],[0],[0],[0],[0]], 'Angie Harmon':[[0],[0],[1],[0],[0],[0]], 'Alec Baldwin':[[0],[0],[0],[1],[0],[0]], 'Bill Hader':[[0],[0],[0],[0],[1],[0]], 'Steve Carell':[[0],[0],[0],[0],[0],[1]]}
    #anti_classify_act = {0:'Lorraine Bracco', 1:'Peri Gilpin', 2:'Angie Harmon', 3:'Alec Baldwin', 4:'Bill Hader', 5:'Steve Carell'}
    
    train_x,train_y = create_set(classify_act, training_set,foldername = "resized_images_"+str(dimension)+"/",dim=dimension)
    test_x,test_y = create_set(classify_act, test_set,foldername = "resized_images_"+str(dimension)+"/",dim=dimension)
    validation_x,validation_y = create_set(classify_act, validation_set,foldername = "resized_images_"+str(dimension)+"/",dim=dimension)
    
    
    train_xy = np.hstack((train_x,np.argmax(train_y, 1).reshape((train_x.shape[0],1))))
    validation_xy = np.hstack((validation_x,np.argmax(validation_y, 1).reshape((validation_x.shape[0],1))))
    test_xy = np.hstack((test_x,np.argmax(test_y, 1).reshape((test_x.shape[0],1))))
    
    
    return train_xy,validation_xy,test_xy

# Part 8_2
# -----------------------------------------------------------------------------
def part8_CAL():
    print "Running Part 8 3"
    print "Choose Activation Layer"
    
    train_xy, validation_xy,test_xy =part8_1()

    dim_x = 32*32
    dim_h = 12
    dim_out = 6
    n_epoch = 6000
    batch_size = train_xy.shape[0]
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor


    dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)
    
    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 2e-4
    momentum_set = 0.9
    
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    performance_train_1 = []
    performance_train_2 = []
    num_iter = []

    model = torch.nn.Sequential(
            torch.nn.Linear(dim_x, dim_h),
            torch.nn.Tanh(),
            torch.nn.Linear(dim_h, dim_out),
            torch.nn.Softmax()
            )

    #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    torch.manual_seed(0)
    #initialize weight
    model[0].weight.data.normal_(0.0,0.01)
    model[2].weight.data.normal_(0.0,0.01)
    model[0].bias.data.normal_(0.0,0.01)
    model[2].bias.data.normal_(0.0,0.01)
    
    for epoch in range(n_epoch):
        for i, data in enumerate(dataloader):
            x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
            y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
            
            y_pred = model(x)
            loss = loss_fn(y_pred, y_classes)
        
            model.zero_grad()  # Zero out the previous gradient computation
            loss.backward()    # Compute the gradient
            optimizer.step()   # Use the gradient information to
            
            if (epoch*ceil(train_xy.shape[0]/batch_size)+i) % 200 ==0:
                num_iter.append(epoch*ceil(train_xy.shape[0]/batch_size)+i)
                y_pred_train_x = model(train_x).data.numpy()
                performance_train_1.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))

    model = torch.nn.Sequential(
            torch.nn.Linear(dim_x, dim_h),
            torch.nn.ReLU(),
            torch.nn.Linear(dim_h, dim_out),
            torch.nn.Softmax()
            )

    #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    torch.manual_seed(0)
    #initialize weight
    model[0].weight.data.normal_(0.0,0.01)
    model[2].weight.data.normal_(0.0,0.01)
    model[0].bias.data.normal_(0.0,0.01)
    model[2].bias.data.normal_(0.0,0.01)
    
    for epoch in range(n_epoch):
        for i, data in enumerate(dataloader):
            x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
            y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
            
            y_pred = model(x)
            loss = loss_fn(y_pred, y_classes)
        
            model.zero_grad()  # Zero out the previous gradient computation
            loss.backward()    # Compute the gradient
            optimizer.step()   # Use the gradient information to
        
            if (epoch*ceil(train_xy.shape[0]/batch_size)+i) % 200 ==0:
                y_pred_train_x = model(train_x).data.numpy()
                performance_train_2.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
    print num_iter    
    plt.plot(num_iter, performance_train_1,'-',num_iter, performance_train_2,'-')
    plt.legend(['Tanh','ReLU'])
    plt.xlabel('Number of Iterations')
    plt.ylabel('Performance')
    plt.savefig('figures/part8fcal.jpg')
    plt.show()

# Part 8_2
# -----------------------------------------------------------------------------
def part8_NHN():
    print "Running Part 8 3"
    print "Choose Number of Hidden Layer "
    
    train_xy, validation_xy,test_xy =part8_1()

    dim_x = 32*32
    #dim_h = 12
    dim_out = 6
    n_epoch = 4000
    batch_size = train_xy.shape[0]
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor


    dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)
    
    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 2e-4
    momentum_set = 0.9
    
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    
    legend = []
    
    for dim_h in [6, 12, 24]:
        num_iter = []
        performance_train = []
        model = torch.nn.Sequential(
                torch.nn.Linear(dim_x, dim_h),
                torch.nn.Tanh(),
                torch.nn.Linear(dim_h, dim_out),
                torch.nn.Softmax()
                )
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        
        torch.manual_seed(0)
        #initialize weight
        model[0].weight.data.normal_(0.0,0.01)
        model[2].weight.data.normal_(0.0,0.01)
        model[0].bias.data.normal_(0.0,0.01)
        model[2].bias.data.normal_(0.0,0.01)
        
        for epoch in range(n_epoch):
            for i, data in enumerate(dataloader):
                x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
                y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
                
                y_pred = model(x)
                loss = loss_fn(y_pred, y_classes)
            
                model.zero_grad()  # Zero out the previous gradient computation
                loss.backward()    # Compute the gradient
                optimizer.step()   # Use the gradient information to
                
                if (epoch*ceil(train_xy.shape[0]/batch_size)+i) % 20 ==0:
                    num_iter.append(epoch*ceil(train_xy.shape[0]/batch_size)+i)
                    y_pred_train_x = model(train_x).data.numpy()
                    performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
        legend.append("# of Hidden Neuron = "+ str(dim_h))
        plt.plot(num_iter, performance_train,'-')
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Performance')
    plt.savefig('figures/part8fnhn.jpg')
    plt.show()

# Part 8_2
# -----------------------------------------------------------------------------
def part8_DIM():
    print "Running Part 8 3"
    print "Change Input Dimension "
    
    #dim_x = 32*32
    dim_h = 12
    dim_out = 6
    n_epoch = 2000
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor

    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 2e-4
    momentum_set = 0.9
    
    legend = []
    
    for dim in [32, 64]:
        dim_x = dim*dim
        
        train_xy, validation_xy,test_xy =part8_1(dimension = dim)
        batch_size = train_xy.shape[0]
        dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)
        train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
        
        num_iter = []
        performance_train = []
        model = torch.nn.Sequential(
                torch.nn.Linear(dim_x, dim_h),
                torch.nn.Tanh(),
                torch.nn.Linear(dim_h, dim_out),
                torch.nn.Softmax()
                )
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        
        torch.manual_seed(0)
        #initialize weight
        model[0].weight.data.normal_(0.0,0.01)
        model[2].weight.data.normal_(0.0,0.01)
        model[0].bias.data.normal_(0.0,0.01)
        model[2].bias.data.normal_(0.0,0.01)
        
        for epoch in range(n_epoch):
            for i, data in enumerate(dataloader):
                x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
                y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
                
                y_pred = model(x)
                loss = loss_fn(y_pred, y_classes)
            
                model.zero_grad()  # Zero out the previous gradient computation
                loss.backward()    # Compute the gradient
                optimizer.step()   # Use the gradient information to
                
                if (epoch*ceil(train_xy.shape[0]/batch_size)+i) % 20 ==0:
                    num_iter.append(epoch*ceil(train_xy.shape[0]/batch_size)+i)
                    y_pred_train_x = model(train_x).data.numpy()
                    performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
        legend.append("Input Dimension = "+ str(dim))
        plt.plot(num_iter, performance_train,'-')
    plt.legend(legend)
    plt.xlabel('Number of Iterations')
    plt.ylabel('Performance')
    plt.savefig('figures/part8fdim.jpg')
    plt.show()

# Part 8_2
# -----------------------------------------------------------------------------
def part8_MB():
    print "Running Part 8 3"
    print "Choose MiniBatch Size "
    
    dim_x = 64*64
    dim_h = 12
    dim_out = 6
    n_epoch = 200
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor

    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 2e-4
    momentum_set = 0.9
    
    legend = []
    
    train_xy, validation_xy,test_xy =part8_1(dimension = 64)
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    
    for batch_size in [8, 16, 32, 64]:

        dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)

        num_iter = []
        performance_train = []
        model = torch.nn.Sequential(
                torch.nn.Linear(dim_x, dim_h),
                torch.nn.Tanh(),
                torch.nn.Linear(dim_h, dim_out),
                torch.nn.Softmax()
                )
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        
        torch.manual_seed(0)
        #initialize weight
        model[0].weight.data.normal_(0.0,0.01)
        model[2].weight.data.normal_(0.0,0.01)
        model[0].bias.data.normal_(0.0,0.01)
        model[2].bias.data.normal_(0.0,0.01)
        
        for epoch in range(n_epoch):
            for i, data in enumerate(dataloader):
                x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
                y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
                
                y_pred = model(x)
                loss = loss_fn(y_pred, y_classes)
            
                model.zero_grad()  # Zero out the previous gradient computation
                loss.backward()    # Compute the gradient
                optimizer.step()   # Use the gradient information to
                
            if (epoch) % 20 ==0:
                num_iter.append(epoch)
                y_pred_train_x = model(train_x).data.numpy()
                performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
        legend.append("MiniBatch Size = "+ str(batch_size))
        plt.plot(num_iter, performance_train,'-')
    plt.legend(legend)
    plt.xlabel('Number of Epochs')
    plt.ylabel('Performance')
    plt.savefig('figures/part8fmb.jpg')
    plt.show()

# Part 8_2
# -----------------------------------------------------------------------------
def part8_W():
    print "Running Part 8 3"
    print "Weights Initialization "
    
    dim_x = 64*64
    dim_h = 12
    dim_out = 6
    n_epoch = 1000
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor

    loss_fn = torch.nn.CrossEntropyLoss()
    #learning_rate = 2e-4
    batch_size = 32
    learning_rate = 0.0003
    
    legend = []
    
    train_xy, validation_xy,test_xy =part8_1(dimension = 64)
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    
    for var in [0.001, 0.01, 0.1, 1]:

        dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)

        num_iter = []
        performance_train = []
        model = torch.nn.Sequential(
                torch.nn.Linear(dim_x, dim_h),
                torch.nn.Tanh(),
                torch.nn.Linear(dim_h, dim_out),
                torch.nn.Softmax()
                )
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        
        torch.manual_seed(0)
        #initialize weight
        model[0].weight.data.normal_(0.0,var)
        model[2].weight.data.normal_(0.0,var)
        model[0].bias.data.normal_(0.0,var)
        model[2].bias.data.normal_(0.0,var)
        
        for epoch in range(n_epoch):
            for i, data in enumerate(dataloader):
                x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
                y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
                
                y_pred = model(x)
                loss = loss_fn(y_pred, y_classes)
            
                model.zero_grad()  # Zero out the previous gradient computation
                loss.backward()    # Compute the gradient
                optimizer.step()   # Use the gradient information to
                
            if (epoch) % 20 ==0:
                num_iter.append(epoch)
                y_pred_train_x = model(train_x).data.numpy()
                performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
        legend.append("Variance = "+ str(var))
        plt.plot(num_iter, performance_train,'-')
    plt.legend(legend)
    plt.xlabel('Number of Epochs')
    plt.ylabel('Performance')
    plt.savefig('figures/part8fw.jpg')
    plt.show()

# Part 8_2
# -----------------------------------------------------------------------------
def part8_LR():
    print "Running Part 8 3"
    print "Choose Learning Rate "
    
    dim_x = 64*64
    dim_h = 12
    dim_out = 6
    n_epoch = 1000
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor

    loss_fn = torch.nn.CrossEntropyLoss()
    #learning_rate = 2e-4
    batch_size = 32
    momentum_set = 0.9
    
    legend = []
    
    train_xy, validation_xy,test_xy =part8_1(dimension = 64)
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    
    for learning_rate in [x * 1e-4 for x in range(1,8,2)]:

        dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)

        num_iter = []
        performance_train = []
        model = torch.nn.Sequential(
                torch.nn.Linear(dim_x, dim_h),
                torch.nn.Tanh(),
                torch.nn.Linear(dim_h, dim_out),
                torch.nn.Softmax()
                )
    
        #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        
        torch.manual_seed(0)
        #initialize weight
        model[0].weight.data.normal_(0.0,0.01)
        model[2].weight.data.normal_(0.0,0.01)
        model[0].bias.data.normal_(0.0,0.01)
        model[2].bias.data.normal_(0.0,0.01)
        
        for epoch in range(n_epoch):
            for i, data in enumerate(dataloader):
                x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
                y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
                
                y_pred = model(x)
                loss = loss_fn(y_pred, y_classes)
            
                model.zero_grad()  # Zero out the previous gradient computation
                loss.backward()    # Compute the gradient
                optimizer.step()   # Use the gradient information to
                
            if (epoch) % 20 ==0:
                num_iter.append(epoch)
                y_pred_train_x = model(train_x).data.numpy()
                performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
        legend.append("LR = "+ str(learning_rate))
        plt.plot(num_iter, performance_train,'-')
    plt.legend(legend)
    plt.xlabel('Number of Epochs')
    plt.ylabel('Performance')
    plt.savefig('figures/part8flr.jpg')
    plt.show()

# Part 8_3
# -----------------------------------------------------------------------------
def part8_3(plot = True,dim = 64):
    
    print "Running Part 8 3"
    
    torch.manual_seed(0)
    
    train_xy, validation_xy,test_xy =part8_1(dimension = dim)
    
    dim_x = dim*dim
    dim_h = 12
    dim_out = 6
    
    n_epoch = 2000
    batch_size = 32
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor
    

    model = torch.nn.Sequential(
            torch.nn.Linear(dim_x, dim_h),
            torch.nn.Tanh(),
            torch.nn.Linear(dim_h, dim_out),
            torch.nn.Softmax()
            )
    
    #initialize weight
    model[0].weight.data.normal_(0.0,0.1)
    model[2].weight.data.normal_(0.0,0.1)
    model[0].bias.data.normal_(0.0,0.1)
    model[2].bias.data.normal_(0.0,0.1)
    
    dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)
    
    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 2e-4
    momentum_set = 0.9
    
    #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum_set)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    validation_x = Variable(torch.from_numpy(validation_xy[:,:-1]), requires_grad=False).type(dtype_float)
    performance_train = []
    performance_validation = []
    num_iter = []
    
    for epoch in range(n_epoch):
        for i, data in enumerate(dataloader):
            x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
            y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
            
            y_pred = model(x)
            loss = loss_fn(y_pred, y_classes)
        
            model.zero_grad()  # Zero out the previous gradient computation
            loss.backward()    # Compute the gradient
            optimizer.step()   # Use the gradient information to
        
            if (epoch*ceil(train_xy.shape[0]/batch_size)+i) % 20 ==0:
                num_iter.append(epoch*ceil(train_xy.shape[0]/batch_size)+i)
                y_pred_train_x = model(train_x).data.numpy()
                performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
                #print (np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1]))
                y_pred_validation_x = model(validation_x).data.numpy()
                performance_validation.append((np.mean(np.argmax(y_pred_validation_x, 1) == validation_xy[:,-1])))
                #print (np.mean(np.argmax(y_pred_validation_x, 1) == validation_xy[:,-1]))
        
    if plot==True:
        plt.plot(num_iter, performance_train,'-',num_iter, performance_validation,'-')
        plt.legend(['training','validation'])
        plt.xlabel('Number of Iterations')
        plt.ylabel('Performance')
        plt.savefig('figures/part8f1.jpg')
        plt.show()
        
        test_x = Variable(torch.from_numpy(test_xy[:,:-1]), requires_grad=False).type(dtype_float)
        y_pred = model(test_x).data.numpy()
        print ("Performance on test set is:")
        print (np.mean(np.argmax(y_pred, 1) == test_xy[:,-1]))
    
    return model
    
# Part 9
# -----------------------------------------------------------------------------
def part9(dim = 64):
    
    print "Running Part 9"
    
    model = part8_3(False)
    
    for i in range(5):
        print ("Node " +str(i)+" looks like:")
        plt.imshow(model[0].weight.data.numpy()[i, :].reshape((dim, dim)), cmap=plt.cm.coolwarm)
        plt.savefig('figures/part9f'+str(i)+'.jpg')
        plt.show()
    
    
    
    
if __name__ == "__main__":
    #Important Note: Please uncomment the following line when using an IDE!
    os.chdir(os.path.dirname(__file__))
    #train_xy,validation_xy,test_xy = part8_1()
    #part8_CAL
    #part8_NHN()
    #part8_DIM()
    #part8_MB()
    part8_W()
    #part8_LR()
    #part8_3()
    #part9()


# Test Code
# -----------------------------------------------------------------------------
