import gzip
import struct
import random
import numpy as np

with gzip.open('train-labels-idx1-ubyte.gz','rb') as f:
    f_label = f.read()
label = []
for i in f_label:
    label.append(i)
label = label[8:]

#print(label)
with gzip.open('train-images-idx3-ubyte.gz','rb') as f:
    f_image = f.read()
image = []
for i in range(16,len(f_image),784):
    temp = []
    for j in range(784):
        temp.append(f_image[i+j])
    temp = np.array(temp)
    thisLabel = np.zeros((10))
    thisLabel[ int( label[int((i-16)/784)] ) ] = 1
    temp = [temp, thisLabel]
    image.append(temp)

with gzip.open('t10k-labels-idx1-ubyte.gz','rb') as f:
    f_tlabel = f.read()
tlabel = []
for i in f_tlabel:
    tlabel.append(i)
tlabel = tlabel[8:]

with gzip.open('t10k-images-idx3-ubyte.gz','rb') as f:
    f_timage = f.read()
timage = []
for i in range(16,len(f_timage),784):
    temp = []
    for j in range(784):
        temp.append(f_timage[i+j])
    timage.append(temp)

print("Read Finished")

import tensorflow as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784,10]))
b = tf.Variable(tf.zeros([10]))
y = tf.nn.softmax(tf.matmul(x,W) + b)

clip_y = tf.clip_by_value(y, 1e-11, 1e100)

y_ = tf.placeholder("float",[None,10])
cross_entropy = -tf.reduce_sum(y_ * tf.log(clip_y));
#cross_entropy = tf.reduce_mean( -tf.reduce_sum(y_ * tf.log(clip_y), 1) )
train_step = tf.train.GradientDescentOptimizer(1e-9).minimize(cross_entropy)

init = tf.global_variables_initializer()

sess = tf.Session()
sess.run(init)

import sys
print("Begin Training")
for i in range(10000): #1000
    slice = random.sample(image, 100)
    batch_x = []
    batch_y = []
    for j in range(100):
        batch_x.append(slice[j][0])
        batch_y.append(slice[j][1])
    batch_xs = np.array(batch_x)
    batch_ys = np.array(batch_y)
    sess.run(train_step, feed_dict = {x: batch_xs, y_: batch_ys})
    if (i%100 == 0):
        print(i)
        print(sess.run(cross_entropy, feed_dict = {x: batch_xs, y_: batch_ys}))

test_xs = []
for i in timage:
    test_xs.append(np.array(i))
test_xs = np.array(test_xs)

test_ys = []
for i in tlabel:
    temp = np.zeros(10)
    temp[i] = 1
    test_ys.append(temp)
test_ys = np.array(test_ys)

correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
print("accuracy : ")
print(sess.run(accuracy, feed_dict={x: test_xs, y_: test_ys }))
