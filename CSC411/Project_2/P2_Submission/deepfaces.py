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

import torchvision.models as models
import torchvision

import torch.nn as nn

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
def create_set(classify_act, desired_set,model,foldername = "resized_images_227/",dim=32):
    feature = np.empty((0,9216))
    label = np.empty((6,0))
    for a in classify_act.keys():
        for image in desired_set[a]:
            label = np.hstack((label,np.array(classify_act[a])))
            try:
                im = imread(foldername+image+".jpg")[:,:,:3]
            except IOError:
                try:
                    im = imread(foldername+image+".jpeg")[:,:,:3]
                except IOError:
                    try:
                        im = imread(foldername + image + ".JPG")[:,:,:3]
                    except IOError:
                        try:
                            im = imread(foldername + image + ".PNG")[:,:,:3]
                        except IOError:
                            try:
                                im = imread(foldername + image + ".JPEG")[:,:,:3]
                            except IOError:
                                im = imread(foldername+image+".png")[:,:,:3]
            try:
                im = imresize(im,(dim,dim))
                im = im - np.mean(im.flatten())
                im = im/np.max(np.abs(im.flatten()))
                im = np.rollaxis(im, -1).astype(np.float32)
                im_v = Variable(torch.from_numpy(im).unsqueeze_(0), requires_grad=False)
                im = model.forward(im_v)
            except:
                print ("Cannot process image.")      
            feature = np.vstack((feature,im))
    return feature,label.T

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

# We modify the torchvision implementation so that the features
# after the final pooling layer is easily accessible by calling
#       net.features(...)
# If you would like to use other layer features, you will need to
# make similar modifications.
class MyAlexNet(nn.Module):
    def load_weights(self):
        an_builtin = torchvision.models.alexnet(pretrained=True)
        
        features_weight_i = [0, 3, 6, 8, 10]
        for i in features_weight_i:
            self.features[i].weight = an_builtin.features[i].weight
            self.features[i].bias = an_builtin.features[i].bias
            
        classifier_weight_i = [0, 2]
        for i in classifier_weight_i:
            self.classifier[i].weight.data.normal_(0.0,0.01)
            self.classifier[i].bias.data.normal_(0.0,0.01)

    def __init__(self, num_classes=6):
        super(MyAlexNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(256 * 6 * 6, 12),
            nn.Tanh(),
            nn.Linear(12, num_classes),
            nn.Softmax()
            )
        
        self.load_weights()
        
        for param in self.features.parameters():
            param.requires_grad = False

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), 256 * 6 * 6)
        #x = self.classifier(x)
        return x.data.numpy()
    
def image_processing(model):
    try:
        os.makedirs('figures')
    except OSError:
        pass
    
    full_image_num = get_imag_num(["facescrub_actors.txt","facescrub_actresses.txt"], "resized_images_227/")
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
    
    train_x,train_y = create_set(classify_act, training_set,model,foldername = "resized_images_227/",dim=227)
    test_x,test_y = create_set(classify_act, test_set,model,foldername = "resized_images_227/",dim=227)
    validation_x,validation_y = create_set(classify_act, validation_set,model,foldername = "resized_images_227/",dim=227)
    
    
    train_xy = np.hstack((train_x,np.argmax(train_y, 1).reshape((train_x.shape[0],1))))
    validation_xy = np.hstack((validation_x,np.argmax(validation_y, 1).reshape((validation_x.shape[0],1))))
    test_xy = np.hstack((test_x,np.argmax(test_y, 1).reshape((test_x.shape[0],1))))
    
    
    return train_xy,validation_xy,test_xy


def part10(plot = True,dim = 227):
    
    torch.manual_seed(0)
    
    model = MyAlexNet()
        
    #use 3*227*227
    train_xy, validation_xy,test_xy = image_processing(model)

    n_epoch = 500
    batch_size = 32
    
    dtype_float = torch.FloatTensor
    dtype_long = torch.LongTensor

    dataloader = DataLoader(train_xy, batch_size=batch_size,shuffle=True)
    
    loss_fn = torch.nn.CrossEntropyLoss()
    learning_rate = 1e-4
    momentum_set = 0.9
    
    #optimizer = torch.optim.SGD(model.classifier.parameters(), lr=learning_rate, momentum=momentum_set)
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=learning_rate)
    
    train_x = Variable(torch.from_numpy(train_xy[:,:-1]), requires_grad=False).type(dtype_float)
    validation_x = Variable(torch.from_numpy(validation_xy[:,:-1]), requires_grad=False).type(dtype_float)
    performance_train = []
    performance_validation = []
    num_epoch = []
    
    for epoch in range(n_epoch):
        for i, data in enumerate(dataloader):
            x = Variable(data[:,:-1], requires_grad=False).type(dtype_float)
            y_classes = Variable(data[:,-1], requires_grad=False).type(dtype_long)
            
            y_pred = model.classifier(x)
            loss = loss_fn(y_pred, y_classes)
        
            model.classifier.zero_grad()  # Zero out the previous gradient computation
            loss.backward()    # Compute the gradient
            optimizer.step()   # Use the gradient information to
        
        if epoch % 5 ==0:
            num_epoch.append(epoch)
            y_pred_train_x = model.classifier(train_x).data.numpy()
            performance_train.append((np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1])))
            #print (np.mean(np.argmax(y_pred_train_x, 1) == train_xy[:,-1]))
            y_pred_validation_x = model.classifier(validation_x).data.numpy()
            performance_validation.append((np.mean(np.argmax(y_pred_validation_x, 1) == validation_xy[:,-1])))
            #print (np.mean(np.argmax(y_pred_validation_x, 1) == validation_xy[:,-1]))
        
    if plot==True:
        plt.plot(num_epoch, performance_train,'-',num_epoch, performance_validation,'-')
        plt.legend(['training','validation'])
        plt.xlabel('Number of Epoches')
        plt.ylabel('Performance')
        plt.savefig('figures/part10f1.jpg')
        plt.show()
        
        test_x = Variable(torch.from_numpy(test_xy[:,:-1]), requires_grad=False).type(dtype_float)
        y_pred = model.classifier(test_x).data.numpy()
        print ("Performance on test set is:")
        print (np.mean(np.argmax(y_pred, 1) == test_xy[:,-1]))
    
    return model


if __name__ == "__main__":
    #Important Note: Please uncomment the following line when using an IDE!
    os.chdir(os.path.dirname(__file__))
    #model = part10()
    

