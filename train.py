from keras.models import Model, load_model
from keras.layers import Input, Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
import keras
import os
import urllib.request
import pickle
import h5py

import numpy as np

with open('data.npy', 'rb') as f:
    image = np.empty(0)
    speed = np.empty(0)
    angle = np.empty(0)

    while True:
        a, b, c = np.load(f)
        image = [image, a]
        speed = [speed, b]
        angle = [angle, c]


img_in = Input(shape=(172, 144, 3), name='img_in')


x = Conv2D(8, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(img_in)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(16, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(32, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

merged = Flatten()(x)

x = Dense(256, kernel_regularizer=keras.regularizers.l2(.005))(merged)
x = Activation('linear')(x)
x = Dropout(.2)(x)

angle_out = Dense(2, kernel_regularizer=keras.regularizers.l2(.005))(x)

model = Model(inputs=img_in, outputs=angle_out)
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()
