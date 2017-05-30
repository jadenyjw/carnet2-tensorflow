from keras.models import Model, load_model
from keras.layers import Input, Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense

img_in = Input(shape=(172, 144, 3), name='img_in')

x = Conv2D(4, (3, 3))(img_in)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(8, (3, 3))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

x = Conv2D(16, (3, 3))(x)
x = Activation('relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)

merged = Flatten()(x)

x = Dense(128)(merged)
x = Activation('linear')(x)
x = Dropout(.2)(x)

angle_out = Dense(2)(x)

model = Model(inputs=img_in, outputs=angle_out)
model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()
