# -*- coding: utf-8 -*-
"""alt chest predictions

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/111h3O8oP7_RPtLQbVlzZmDRIH-zA6zzE
"""

# from google.colab import drive
# drive.mount('/content/drive')

import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
import time
from torch.utils.data import Dataset, DataLoader
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
import torchvision.models as models
import cv2 
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report

x_train = []
x_test = []
# Dummy dataset
data = np.load('chestmnist.npz', allow_pickle=True)
# print(data.files)
# print(data['test_labels'])
x=data['train_images']
y=data['train_labels']

#plt.scatter(x[:, 0], x[:, 1], c=y)
print(x[0].shape)
print(y.shape)
print("The first sample : ", x[0],"belong to cluster", y[0])
print("The tenth sample : ", x[10],"belong to cluster", y[10])


# Split to a train set (80%), and a test set (20%)
x_testPre, y_test = data["test_images"], data["test_labels"]
x_trainPre, y_train = data["train_images"], data["train_labels"]
x_valPre, y_val = data["val_images"], data["val_labels"]
# plt.gray()
#

img = x_trainPre[5].astype('float32')
img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
plt.imshow(img)

# for i in range(len(x_train)):
#   x_train[i] = color_img = cv2.cvtColor(x_train[i], cv2.cv.CV_GRAY2RGB)
# plt.imshow(x_train[1], interpolation='nearest')

plt.imshow(x[0])

print(data.files)

#img = x_train[5].astype('float32')\
x_train = []
x_test = []
x_val = []
for i in range(len(x_trainPre)):
  var = cv2.cvtColor(x_trainPre[i],cv2.COLOR_GRAY2RGB)
  var = np.transpose(var, [2, 0, 1])
  x_train.append(var)
for i in range(len(x_testPre)):
  var = cv2.cvtColor(x_testPre[i],cv2.COLOR_GRAY2RGB)
  var = np.transpose(var, [2, 0, 1])
  x_test.append(var)
for i in range(len(x_valPre)):
  var = cv2.cvtColor(x_testPre[i],cv2.COLOR_GRAY2RGB)
  var = np.transpose(var, [2, 0, 1])
  x_val.append(var)
print(x_train[0].shape)
print(x_test[0].shape)
print(x_val[0].shape)

!ls
print(x_train[500].shape)

net = models.resnet18(pretrained=True).cuda()
net.fc = nn.Linear(512, 14)
print(net)

class MyDataset(Dataset):
  def __init__(self, x, y):
      super().__init__()
      self.x = x
      self.y = y 
  
  def __getitem__(self, idx):
    return self.x[idx], self.y[idx]

  def __repr__(self):
      return "This is my dataset and it has length {}".format(len(self))

  def __len__(self):
    #assert len(self.x) == len(self.y)
    return len(self.y)

# Dataloader
my_dataset = MyDataset(x_train,y_train)
print(my_dataset.__getitem__(0)[0].shape)
my_dataloader = DataLoader(my_dataset, batch_size=64, shuffle=True)


# Optimizer
optimizer = torch.optim.SGD(net.parameters(), lr=0.1)

# Loss function (cross entropy for classification)
loss_func = nn.BCEWithLogitsLoss()

# Training time !
net.cuda()
net.train() # Put model in training mode

net.cuda()
net.train() # Put model in training mode

count = 0
prev_loss = 0
learning_rate = 0.1
mean = 0
for epoch in range(100): # We go over the data ten times
  loss_list = []
  prev_loss = mean
  sum = 0
  for batch in my_dataloader:
    optimizer.zero_grad()

    # Forward pass 
    inp, labels = batch
    inp = torch.tensor(inp.cuda(), dtype=torch.float32)
    labels = labels.cuda()
    out = net(inp.cuda())
    loss = loss_func(out, labels.float())
    loss_list.append(loss)
    # Backward pass
    loss.backward()
    optimizer.step()
  for i in loss_list:
    sum +=i
  mean = sum/len(loss_list)
  if count >= 3 and mean > prev_loss:
    learning_rate = learning_rate/2
    count = 0
    for g in optimizer.param_groups:
      g['lr'] = learning_rate
  elif mean < prev_loss:
    count+=1
  else:
    count = 0



 
# print('Accuracy', np.mean(network_answers==y)*100)

# try to test the machine before training, how much is the accuracy ?
  print(f"{epoch}: {mean}", end = "")
  print(f", learning rate: {learning_rate}", end = "")
  print(f", count: {count}", end="")

torch.save(net, 'chestModelTrain.pt')

net = torch.load('model5.pt')

# Test time

net.eval()

# Dataloader
my_dataset = MyDataset(x_train,y_train)
my_dataloader = DataLoader(my_dataset, batch_size=64)

network_answers = []
true_answers = []
for batch in my_dataloader:
  # Forward pass 
  inp, labels = batch
  inp = torch.tensor(inp.cuda(), dtype=torch.float32)
  out = net(inp)
  # print(out)

  # out is batch_size x 2 (one score for each cluster)
  sigmoid_layer = torch.nn.Sigmoid()
  answers = sigmoid_layer(out).cpu().detach().numpy()

  # Recording values
  # if answers >= 0.5:
  #   answers = 1
  # else:
  #   answers[i] = 0
  preds = answers >= 0.4
  # print(preds)
  network_answers.extend(np.asarray(preds))
  true_answers.extend(labels.data.cpu().numpy())
# print(y_test)
# print()
# print(true_answers)
label_mapping = ["atelectasis", "cardiomegaly", "effusion", "infiltration", "mass", "nodule", "pneumonia", "pneumothorax", "consolidation", "edema", "emphysema", "fibrosis", "pleural", "hernia"]


print(f" Accuracy Score: {accuracy_score(true_answers, network_answers)}")
print(f" Precision Score: {precision_score(true_answers, network_answers, average='micro')}")
print(f" Recall Score: {recall_score(true_answers, network_answers, average='micro')}")
print(f"{classification_report(true_answers, network_answers, target_names = label_mapping)}")
# print('Accuracy', np.mean(network_answers==y)*100)

# try to test the machine before training, how much is the accuracy ?

# for i in range(100):
#   print(network_answers[i] >)

my_dataset = MyDataset(x_test[:2],y_test[:2])
my_dataloader = DataLoader(my_dataset, batch_size=64)

network_answers = []
true_answers = []
for batch in my_dataloader:
  # Forward pass 
  inp, labels = batch
  inp = torch.tensor(inp.cuda(), dtype=torch.float32)
  out = net(inp)
  # print(out)

  # out is batch_size x 2 (one score for each cluster)
  sigmoid_layer = torch.nn.Sigmoid()
  answers = sigmoid_layer(out).cpu().detach().numpy()

  # Recording values
  # if answers >= 0.5:
  #   answers = 1
  # else:
  #   answers[i] = 0
  preds = answers >= 0.4
  # print(preds)
  network_answers.extend(np.asarray(preds))
  print(network_answers)
  true_answers.extend(labels.data.cpu().numpy())
  print(true_answers[1])
# print(y_test)
# print()
# print(true_answers)