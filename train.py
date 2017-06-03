from keras.models import Model, load_model
from keras.layers import Input, Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
import keras
import os
from keras import callbacks
import numpy as np


import matplotlib.pyplot as plt
import matplotlib.image as mpimg


with open('data.npy', 'rb') as f:
    X = []
    Y = []
    while 1:
        try:
            temp = np.load(f)
            X.append(temp[0])
            Y.append(temp[1])
        except OSError:
            break

    #print(X)
    #print(Y)


X = np.array(X)
Y = np.array(Y)

#imgplot = plt.imshow(X[0])
#plt.show()

from sklearn.utils import shuffle
shuffled_X, shuffled_Y = shuffle(X, Y, random_state=0)

test_cutoff = int(len(X) * .6) # 80% of data used for training
val_cutoff = test_cutoff + int(len(X) * .2) # 10% of data used for validation and test data

train_X, train_Y = shuffled_X[:test_cutoff], shuffled_Y[:test_cutoff]
val_X, val_Y = shuffled_X[test_cutoff:val_cutoff], shuffled_Y[test_cutoff:val_cutoff]
test_X, test_Y = shuffled_X[val_cutoff:], shuffled_Y[val_cutoff:]

len(train_X) + len(val_X) + len(test_X)

'''
X_flipped = np.array([np.fliplr(i) for i in train_X])
Y_flipped = np.array([-i for i in train_Y])
train_X = np.concatenate([train_X, X_flipped])
train_Y = np.concatenate([train_Y, Y_flipped])
len(train_X)
'''


print(train_X.shape)
#print(train_X[0].shape())
img_in = Input(shape=(144, 176, 3), name='img_in')

x = Conv2D(4, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(img_in)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(8, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(16, (3, 3), kernel_regularizer=keras.regularizers.l2(.005))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

merged = Flatten()(x)

x = Dense(128, kernel_regularizer=keras.regularizers.l2(.005))(merged)
x = Activation('linear')(x)
x = Dropout(.2)(x)

speed_and_angle = Dense(2, kernel_regularizer=keras.regularizers.l2(.005))(x)

model = Model(inputs=img_in, outputs=speed_and_angle)
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

model_path = os.path.expanduser('~/best_autopilot.hdf5')

#Save the model after each epoch if the validation loss improved.
save_best = callbacks.ModelCheckpoint(model_path, monitor='val_loss', verbose=1,
                                     save_best_only=True, mode='min')

calls = [save_best]

model.fit(train_X, train_Y, batch_size=1, epochs=10, validation_data=(val_X, val_Y), callbacks=calls)
