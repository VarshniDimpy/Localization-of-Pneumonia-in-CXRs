# -*- coding: utf-8 -*-
"""mask_rcnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IMXvbEJ6asP4RcAv7MjgHKjH4uhZnsyI
"""

from google.colab import drive
drive.mount('/content/drive')

import os
os.chdir('/content/drive/My Drive/nf/finally_final_training/Disease')

'''
from zipfile import ZipFile
with ZipFile('npys.zip', 'r') as zipObj:
   # Extract all the contents of zip file in different directory
   zipObj.extractall('temp')

!ls
''

"""**Loading Dataset**"""

import numpy as np
x_train=np.load('./x_train.npy')
y_train=np.load("./y_train_mask.npy")
x_val=np.load("./x_test.npy")
y_val=np.load("./y_test_mask.npy")
name_list = np.load("./name_list.npy")

np.unique(y_val),np.unique(y_train)

len(x_val),len(name_list)

print(name_list[0])

"""**Check the data type of train and masks : train should be int**"""

x_train[0].dtype, y_train[0].dtype

"""**Showing an example of a train image & corresponding mask**"""

import matplotlib.pyplot as plt
print(name_list[20])
plt.figure()
plt.imshow(x_val[20])
plt.figure()
plt.imshow(y_val[20],cmap='gray')

"""**Check that masks contain only labels in format 0,1,....**"""

#y_train[0][y_train[0]==255]=1
#np.unique(y_train[100])

np.unique(y_train[100])
np.unique(y_val[100])

new_x_train=[]
new_y_train=[]
count=0
index=0
for mask in y_train:
    
    if len(np.unique(mask))==1:
        index+=1
        count+=1
        continue
    new_x_train.append(x_train[index])
    new_y_train.append(y_train[index])
    index+=1
print("number of healthy masks in training set:", count)

new_x_val=[]
new_y_val=[]

count=0
index=0
for mask in y_val:
    
    if len(np.unique(mask))==1:
        index+=1
        count+=1
        continue
    new_x_val.append(x_val[index])
    new_y_val.append(y_val[index])
    index+=1
print("number of healthy masks in test set:", count)

#len(new_x_train),len(x_train),len(x_val),len(new_x_val)

new_x_train=[]
new_y_train=[]
for img,mask in zip(x_train,y_train):
    mean=np.mean(img)
    std=np.std(img)
    new_img=(img-img.min())/(img.max()-img.min())
    new_x_train.append(new_img.astype(float))
    new_y_train.append(mask.astype(float))

#new_x_train=np.array(new_x_train)
#new_y_train=np.array(new_y_train)

new_x_val=[]
new_y_val=[]
for img,mask in zip(x_val,y_val):
    mean=np.mean(img)
    std=np.std(img)
    new_img=(img-img.min())/(img.max()-img.min())
    new_x_val.append(new_img.astype(float))
    new_y_val.append(mask.astype(float))
#new_x_val=np.array(new_x_val)
#new_y_val=np.array(new_y_val)

len(new_x_train),len(new_y_train),len(new_x_val),len(new_y_val)

new_x_train[0].max(),x_train[0].max()

os.getcwd()

os.chdir('../..')

os.getcwd()

'utils.py' in os.listdir()

"""**Import libraries**"""

import numpy as np
import torch
import torchvision
#from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from PIL import Image
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
import utils
import transforms as T
from engine import train_one_epoch, evaluate

"""**Install cython from the given github link**"""

# Commented out IPython magic to ensure Python compatibility.
# %%shell
# 
# pip install cython
# # Install pycocotools, the version by default in Colab
# # has a bug fixed in https://github.com/cocodataset/cocoapi/pull/354
# pip install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

x_val.shape
y_val=np.zeros((2208,224,224,3))

os.getcwd()

"""**Create train dataloader and model instance ( as given in pytorch link ) : https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html**"""

def get_transform(train):
    transforms = []
    transforms.append(T.ToTensor())
    if train:
        transforms.append(T.RandomHorizontalFlip(0.5))
    return T.Compose(transforms)


def get_model_instance_segmentation(num_classes):
    # load an instance segmentation model pre-trained pre-trained on COCO
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    # and replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,hidden_layer,num_classes)
    return model



class CXRTrainDataset(object):
    def __init__(self, new_x_train,new_y_train,transforms):
       
        self.imgs = new_x_train
        self.masks = new_y_train
        self.transforms=transforms
        
    def __getitem__(self, idx):
        # load images ad masks
        #img_path = os.path.join(self.root, "PNGImages", self.imgs[idx])
        #mask_path = os.path.join(self.root, "PedMasks", self.masks[idx])
        #img = Image.open(img_path).convert("RGB")
        img=self.imgs[idx]
        mask=self.masks[idx]
        # note that we haven't converted the mask to RGB,
        # because each color corresponds to a different instance
        # with 0 being background
        #mask = Image.open(mask_path)
        # convert the PIL Image into a numpy array
        mask = np.array(mask)
        # instances are encoded as different colors
        obj_ids = np.unique(mask)
        # first id is the background, so remove it
        obj_ids = obj_ids[1:]

        # split the color-encoded mask into a set
        # of binary masks
        masks = np.expand_dims(mask,axis=0)

        # get bounding box coordinates for each mask
        num_objs = len(obj_ids)
        boxes = []
        for i in range(num_objs):
            pos = np.where(masks[i])
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        # convert everything into a torch.Tensor
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        # there is only one class
        labels = torch.ones((num_objs,), dtype=torch.int64)
        masks = torch.as_tensor(masks, dtype=torch.uint8)

        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["masks"] = masks
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd
        #target["actual_mask"]=mask

        if self.transforms is not None:
            img, target = self.transforms(img, target)
        
        #print("target : ",target)
        return img, target

    def __len__(self):
        return len(self.imgs)


dataset=CXRTrainDataset(x_train,y_train,get_transform(train=True))

#data_loader=torch.utils.data.DataLoader(dataset,batch_size=8,shuffle=True)
data_loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True,collate_fn=utils.collate_fn)

model=torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
in_features=model.roi_heads.box_predictor.cls_score.in_features
num_classes=2
model.roi_heads.box_predictor=FastRCNNPredictor(in_features,num_classes)
backbone = torchvision.models.mobilenet_v2(pretrained=True).features
backbone.out_channels = 1280
anchor_generator = AnchorGenerator(sizes=((32, 64, 128, 256, 512),),aspect_ratios=((0.5, 1.0, 2.0),))


roi_pooler = torchvision.ops.MultiScaleRoIAlign(featmap_names=[0],output_size=7,sampling_ratio=2)
model = FasterRCNN(backbone,num_classes=2,rpn_anchor_generator=anchor_generator,box_roi_pool=roi_pooler)                                   

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
num_classes = 2

model = get_model_instance_segmentation(num_classes)

model.to(device)
'''
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.02,momentum=0.9, weight_decay=0.0005)
    # and a learning rate scheduler
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,step_size=3,gamma=0.1)

num_epochs = 10
for epoch in range(num_epochs):
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        # update the learning rate
        lr_scheduler.step()
        # evaluate on the test dataset
        #evaluate(model, data_loader_test, device=device)
'''

os.listdir('./finally_final_training/Disease/')

params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=0.002,momentum=0.9)
    # and a learning rate scheduler
#lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,step_size=3,gamma=0.1)
#os.mkdir('lung_segmentation_preds')
num_epochs = 50

for epoch in range(num_epochs):
        # train for one epoch, printing every 10 iterations
        train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)
        # update the learning rate
        #lr_scheduler.step()
        torch.save(model.state_dict(),'./finally_final_training/Disease/model_pretrained_CXR_new.pt')
        # evaluate on the test dataset
        #evaluate(model, data_loader_test, device=device)

#torch.save(model.state_dict(), './preds_kukdu_kukdu/model_pretrained_lung_segmentation_state.pt')

#model.load_state_dict(torch.load('./preds_kukdu_ki/model_pretrained_lung_segmentation_state.pt'))

os.getcwd()

#model.load_state_dict(torch.load('./finally_final_training/Disease/model_pretrained_CXR.pt'))

"""**Create test data loader keep train=False and shuffle=False**"""

class CXRTestDataset(object):
    def __init__(self, new_x_train,new_y_train,name_list,transforms):
       
        self.imgs = new_x_train
        self.masks = new_y_train
        self.names=name_list
        self.transforms=transforms
        
    def __getitem__(self, idx):
        # load images ad masks
        #img_path = os.path.join(self.root, "PNGImages", self.imgs[idx])
        #mask_path = os.path.join(self.root, "PedMasks", self.masks[idx])
        #img = Image.open(img_path).convert("RGB")
        img=self.imgs[idx]
        mask=self.masks[idx]
        name=self.names[idx]
        # note that we haven't converted the mask to RGB,
        # because each color corresponds to a different instance
        # with 0 being background
        #mask = Image.open(mask_path)
        # convert the PIL Image into a numpy array
        mask = np.array(mask)
        # instances are encoded as different colors
        obj_ids = np.unique(mask)
        # first id is the background, so remove it
        obj_ids = obj_ids[1:]

        # split the color-encoded mask into a set
        # of binary masks
        masks = np.expand_dims(mask,axis=0)

        # get bounding box coordinates for each mask
        num_objs = len(obj_ids)
        boxes = []
        for i in range(num_objs):
            pos = np.where(masks[i])
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        # convert everything into a torch.Tensor
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        # there is only one class
        labels = torch.ones((num_objs,), dtype=torch.int64)
        masks = torch.as_tensor(masks, dtype=torch.uint8)

        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # suppose all instances are not crowd
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["masks"] = masks
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd
        target["actual_mask"]=mask
        target["image_name"]=name

        if self.transforms is not None:
            img, target = self.transforms(img, target)
        
        #print("target : ",target)
        return img, target

    def __len__(self):
        return len(self.imgs)

dataset_test=CXRTestDataset(x_val,y_val,name_list,get_transform(train=False))
#data_loader=torch.utils.data.DataLoader(dataset,batch_size=8,shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset_test, batch_size=16, shuffle=False,collate_fn=utils.collate_fn)

class CXRTestDataset(object):
    def __init__(self, new_x_train,new_y_train,name_list,transforms):
       
        self.imgs = new_x_train
        self.masks = new_y_train
        self.names=name_list
        self.transforms=transforms
        
    def __getitem__(self, idx):
        # load images ad masks
        #img_path = os.path.join(self.root, "PNGImages", self.imgs[idx])
        #mask_path = os.path.join(self.root, "PedMasks", self.masks[idx])
        #img = Image.open(img_path).convert("RGB")
        img=self.imgs[idx]
        mask=self.masks[idx]
        name=self.names[idx]
        # note that we haven't converted the mask to RGB,
        # because each color corresponds to a different instance
        # with 0 being background
        #mask = Image.open(mask_path)
        # convert the PIL Image into a numpy array
        mask = np.array(mask)
        # instances are encoded as different colors
        obj_ids = np.unique(mask)
        # first id is the background, so remove it
        obj_ids = obj_ids[1:]

        # split the color-encoded mask into a set
        # of binary masks
        masks = np.expand_dims(mask,axis=0)

        # get bounding box coordinates for each mask
        num_objs = len(obj_ids)
        boxes = []
        for i in range(num_objs):
            pos = np.where(masks[i])
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        # convert everything into a torch.Tensor
        #boxes = torch.as_tensor(boxes, dtype=torch.float32)
        # there is only one class
        #labels = torch.ones((num_objs,), dtype=torch.int64)
        #masks = torch.as_tensor(masks, dtype=torch.uint8)

        #image_id = torch.tensor([idx])
        #area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        # suppose all instances are not crowd
        #iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        #target["boxes"] = boxes
        #target["labels"] = labels
        #target["masks"] = masks
        #target["image_id"] = image_id
        #target["area"] = area
        #target["iscrowd"] = iscrowd
        target["actual_mask"]=mask
        target["image_name"]=name

        if self.transforms is not None:
            img, target = self.transforms(img, target)
        
        #print("target : ",target)
        return img, target

    def __len__(self):
        return len(self.imgs)

dataset_test=CXRTestDataset(x_val,y_val,name_list,get_transform(train=False))
#data_loader=torch.utils.data.DataLoader(dataset,batch_size=8,shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset_test, batch_size=16, shuffle=False,collate_fn=utils.collate_fn)

len(name_list),len(x_val)

"""**Evaluate model**"""

preds=[]
actual=[]
image_names=[]
all_preds=[]
count=0
model.eval()
for i in range(len(dataset_test)):
    test_image,_=dataset_test[i]
    actual.append(_['actual_mask'])
    image_names.append(_["image_name"])
    #test_image=torch.Tensor(test)
    #test_image=test_image.permute(2,0,1)
    prediction=model([test_image.to(device)])
    #all_preds.append(prediction)
    print(prediction[0]['masks'].size())
    if prediction[0]['masks'].size()[0]==0:
       preds.append(np.zeros((256,256)))
       #preds.append('None')
       count+=1
       print("count : ",count)
       continue
    #actual.append(_['actual_mask'])
    new_image=torch.round(prediction[0]['masks'][0,0])
    new_image=new_image.cpu().detach().numpy()
    preds.append(torch.round(prediction[0]['masks'][0, 0]).cpu().detach().numpy())

#all_preds=np.array(all_preds)
actual=np.array(actual)
preds=np.array(preds)
print("total preds :",preds.shape)
print(" not detected any bounding box in images = : ",count)

len(image_names)

model.eval()
#os.mkdir('preds_proper')
#count, ext = 0, '.png'

'''
for batch in testloader:
    images, labels = batch
    images = images.to(device)
    pred = model(images)
    #print(path)
    for xray, img, label in zip(images, pred, labels):
        img = torch.round(img) #thresholding
        #print(xray.shape)
        xray = xray.permute(1, 2, 0)
        xray = xray.squeeze(0).cpu().detach().numpy()
        img = img.squeeze(0).cpu().detach().numpy()
        label = label.numpy()
        
        img = img * 255.0
        label = label * 255.0
        
        cv2.imwrite(os.path.join(path, name_list[count]+'_xray'+ext), xray)
        cv2.imwrite(os.path.join(path, name_list[count]+'_pred'+ext), img)
        cv2.imwrite(os.path.join(path, name_list[count]+'_label'+ext), label)
        
        count += 1
'''

print(image_names[0])

print(image_names[0].split(".")[0])

io.imshow(actual[0])
np.unique(actual[0])

"""**save prediction masks in drive**"""

actual=np.array(actual)
preds=np.array(preds)
import cv2
#os.mkdir('./Test_set_disease/preds_proper_new_')
os.mkdir('./Final_training/Disease/preds_proper_new_')


from skimage import io


count=0
for pred,mask,act in zip(preds,x_val,actual):
    #if pred=='None':
        #pred=np.zeros((256,256))
  
    #s1='actual_'+str(d)+'.jpg'
    #s2='pred_'+str(d)+'.jpg'
    s1=image_names[count].split(".png")[0]+str('_act')+'.jpg'
    s2=image_names[count].split(".png")[0]+str('_pred')+'.jpg'
    s3=image_names[count].split(".png")[0]+str('_label')+'.jpg'
    #plt.imshow(act)
    io.imsave("./Final_training/Disease/preds_proper_new_/"+s1,mask)
    io.imsave("./Final_training/Disease/preds_proper_new_/"+s2,pred)
    #cv2.imwrite("./Test_set_disease/preds_proper_/"+s3,act)
    io.imsave("./Final_training/Disease/preds_proper_new_/"+s3,act*255)
    count+=1

print(count)

len(np.unique(image_names))

image_names[0].split(".png")

len(preds),len(x_val),len(actual)

len(actual)

count

"""**Report F1 SCORE/DICE SCORE and pixACC & confusion matrix**"""

from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

p, l = [], []
for labels,pred in zip(actual,preds):
    if pred=='None':
        pred=np.zeros((256,256))

    labels = labels
    pred = pred.flatten()
    labels = labels.flatten()
    p.extend(pred)
    l.extend(labels)
print(np.array(l).shape, np.array(p).shape)
score = f1_score(l, p, average='macro')
print("f1 score / dice score = ", score)
report = classification_report(l, p, target_names=['class 0', 'class 1'])
print(report)
print("pixAcc score = ",accuracy_score(l,p))
print("confusion matrix : \n",confusion_matrix(l,p))

"""**Report IOU**"""

def IoU(y_true, y_pred):
    """Returns Intersection over Union score for ground truth and predicted masks."""
    #print(y_true.dtype,y_pred.dtype)
    #assert y_true.dtype == bool and y_pred.dtype == bool
    y_true_f = y_true.flatten()
    y_pred_f = y_pred.flatten()
    intersection = np.logical_and(y_true_f, y_pred_f).sum()
    union = np.logical_or(y_true_f, y_pred_f).sum()
    return (intersection + 1) * 1. / (union + 1)

ious=[]

for  act, pred in zip(actual,preds):
    if pred=='None':
        pred=np.zeros((256,256))
        ious.append(IoU(act.astype(float),pred.astype(float)))
    else:
        #pred=np.zeros((256,256))
        ious.append(IoU(act.astype(float),pred.astype(float)))
print("Total predictions :",len(preds))
ious=np.array(ious)
print("Mean IOU :")
print(round(ious.mean(),4))