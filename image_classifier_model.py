import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import tensorflow as tf

from PIL import Image
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.utils import to_categorical

# Load CIFAR-10 dataset
(X_train, y_train), (X_val, y_val) = cifar10.load_data()

# Normalize the images
X_train = X_train / 255.0
X_val = X_val / 255.0

# Convert labels to one-hot encoding
y_train = to_categorical(y_train, 10)
y_val = to_categorical(y_val, 10)

# Create the model
model = Sequential([
    Flatten(input_shape=(32, 32, 3)),
    Dense(1000, activation='relu'),
    Dense(10, activation='softmax')
])

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, batch_size=64, epochs=10, validation_data=(X_val, y_val))

# Save the model
model.save('cifar10_model.h5')
