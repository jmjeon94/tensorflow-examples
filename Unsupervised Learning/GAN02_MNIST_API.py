
# coding: utf-8

# In[1]:


import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('../MNIST_data',one_hot=True)


# In[2]:


learning_rate=0.0002
training_epoch=100
batch_size=100
n_hidden = 256
n_input=28*28
n_noise=128


# In[3]:


X=tf.placeholder(tf.float32, [None,n_input])
Z=tf.placeholder(tf.float32, [None,n_noise])
'''
G_W1=tf.Variable(tf.random_normal([n_noise,n_hidden], stddev=0.01))
G_b1=tf.Variable(tf.zeros([n_hidden]))
G_W2=tf.Variable(tf.random_normal([n_hidden,n_input], stddev=0.01))
G_b2=tf.Variable(tf.zeros([n_input]))

D_W1=tf.Variable(tf.random_normal([n_input,n_hidden], stddev=0.01))
D_b1=tf.Variable(tf.zeros([n_hidden]))
D_W2=tf.Variable(tf.random_normal([n_hidden,1], stddev=0.01))
D_b2=tf.Variable(tf.zeros([1]))
'''

def generator(noise_z):
    with tf.variable_scope('generator'):
        hidden = tf.layers.dense(noise_z,n_hidden,activation=tf.nn.relu)
        output = tf.layers.dense(hidden,n_input, activation=tf.nn.sigmoid)
    return output

def discriminator(inputs, reuse=False):
    with tf.variable_scope('discriminator') as scope:
        if reuse:
            scope.reuse_variables()
        
        hidden = tf.layers.dense(inputs,n_hidden, activation=tf.nn.relu)
        output = tf.layers.dense(hidden,1, activation=tf.nn.sigmoid)
    return output
    
def get_noise(batch_size, n_noise):
    return np.random.normal(size=(batch_size,n_noise))


# In[4]:


G=generator(Z)
D_gene = discriminator(G)
D_real = discriminator(X,True)

loss_D = tf.reduce_mean(tf.log(1-D_gene)+tf.log(D_real))
loss_G = tf.reduce_mean(tf.log(D_gene))

vars_D=tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='discriminator')
vars_G=tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='generator')

train_D = tf.train.AdamOptimizer(learning_rate).minimize(-loss_D,var_list=vars_D)
train_G = tf.train.AdamOptimizer(learning_rate).minimize(-loss_G,var_list=vars_G)


# In[5]:


sess=tf.Session()
sess.run(tf.global_variables_initializer())

total_batch=int(mnist.train.num_examples/batch_size)
loss_val_D, loss_val_G =0, 0

print('Learning Start')

for epoch in range(training_epoch):
    for i in range(total_batch):
        batch_xs,batch_ys = mnist.train.next_batch(batch_size)
        noise = get_noise(batch_size,n_noise)
        
        _,loss_val_D = sess.run([train_D,loss_D],feed_dict={X:batch_xs, Z:noise})
        _,loss_val_G = sess.run([train_G,loss_G],feed_dict={Z:noise})
        
    print('Epoch','%04d'%(epoch+1), 
          'loss_D:{:.4}'.format(loss_val_D),
          'loss_G:{:.4}'.format(loss_val_G))
    if epoch ==0 or (epoch+1)%10 == 0 :
        sample_size = 10
        noise = get_noise(sample_size, n_noise)
        samples = sess.run(G, feed_dict = {Z:noise})

        fig, ax = plt.subplots(1, sample_size, figsize = (sample_size,1))

        for i in range(sample_size):
            ax[i].set_axis_off()
            ax[i].imshow(np.reshape(samples[i],(28,28)))
        
        plt.savefig('./result/{}.png'.format(str(epoch).zfill(3)),
                        bbox_inches='tight')
        plt.close(fig)
print('Learning Finished')

