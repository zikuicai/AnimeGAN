import math
import numpy as np
import tensorflow as tf
from utils import *


class batch_norm(object):
    def __init__(self, epsilon=1e-5, momentum=0.9, name="batch_norm"):
        with tf.variable_scope(name):
            self.epsilon = epsilon
            self.momentum = momentum
            self.name = name

    def __call__(self, x, train=True):
        return tf.contrib.layers.batch_norm(x,
                                            decay=self.momentum,
                                            updates_collections=None,
                                            epsilon=self.epsilon,
                                            scale=True,
                                            is_training=train,
                                            scope=self.name)


def conv2d(x, output_dim, name="conv2d"):
    # 5x5 filter size [filter_height, filter_width, in_channels, out_channels]
    # 2x2 strides [batch, height, width, channels]
    with tf.variable_scope(name):
        w = tf.get_variable('w', [5, 5, x.get_shape()[-1], output_dim],
                            initializer=tf.truncated_normal_initializer(stddev=0.02))
        b = tf.get_variable('b', [output_dim], 
                            initializer=tf.constant_initializer(0.0))
        conv = tf.nn.conv2d(x, w, strides=[1, 2, 2, 1], padding='SAME')
        conv = tf.reshape(tf.nn.bias_add(conv, b), conv.get_shape())
        return conv


def deconv2d(x, output_shape, name="deconv2d"):
    # filter : [height, width, output_channels, in_channels]
    with tf.variable_scope(name):
        w = tf.get_variable('w', [5, 5, output_shape[-1], x.get_shape()[-1]],
                            initializer=tf.random_normal_initializer(stddev=0.02))
        b = tf.get_variable('b', [output_shape[-1]], 
                            initializer=tf.constant_initializer(0.0))
        deconv = tf.nn.conv2d_transpose(x, w, output_shape=output_shape, strides=[1, 2, 2, 1])
        deconv = tf.reshape(tf.nn.bias_add(deconv, b), deconv.get_shape())
        return deconv


def conv_out_size(h, w, stride_h, stride_w):
    """Calculate the output size from conv layer
    Every time divide h,w by the stride sizes in h,w
    """
    h = int(math.ceil(float(h) / float(stride_h)))
    w = int(math.ceil(float(w) / float(stride_w)))
    return h,w


def lrelu(x, alpha=0.2, name="lrelu"):
    return tf.nn.leaky_relu(x, alpha, name=name)


def dense(x, output_size, name='dense'):
    """Densely connected layer
    """
    shape = x.get_shape().as_list()

    with tf.variable_scope(name):
        matrix = tf.get_variable("Matrix", [shape[1], output_size], tf.float32,
                                 tf.random_normal_initializer(stddev=0.02))
        bias = tf.get_variable("bias", [output_size],
                               initializer=tf.constant_initializer(0.0))
        return tf.matmul(x, matrix) + bias


def loss(x, y):
    """Cost function
    Define the loss function as sigmoid_cross_entropy_with_logits
    http://neuralnetworksanddeeplearning.com/chap3.html#introducing_the_cross-entropy_cost_function

    Returns:
      y * -log(sigmoid(x)) + (1 - y) * -log(1 - sigmoid(x))
      the loss is minimal when sigmoid(x) and y are both 0 or both 1
    """
    return tf.nn.sigmoid_cross_entropy_with_logits(logits=x, labels=y)
