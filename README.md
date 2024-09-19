# AI-ML-projects
# News Summarizer

A simple Python application built using Tkinter that summarizes news articles and performs sentiment analysis on the text. It extracts the article's title, author, publication date, and summary, along with analyzing the sentiment of the article text (positive, neutral, or negative).

## Features

- Extracts and displays the article's title, author, and publication date.
- Summarizes the article using `newspaper3k`.
- Performs sentiment analysis using `TextBlob`.
- Error handling for invalid or empty URLs.
- Clear button to reset all fields.

## Requirements

To run this project, you need to install the following dependencies:

nltk==3.8.1
textblob==0.17.1
newspaper3k==0.2.8
lxml==4.9.3


# CIFAR-10 Web Classifier
This project is a web-based image classifier built using Streamlit and TensorFlow. It allows users to upload an image belonging to one of the CIFAR-10 classes (e.g., airplane, automobile, bird, etc.) and receive predictions based on a pre-trained neural network model.
## Project Overview
Users can upload an image from one of the ten CIFAR-10 classes (airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck).
The model processes the image and returns a probability distribution over the 10 classes.
The top prediction is highlighted along with a bar chart showing the probability for each class.
## Prerequisites
Python 3.x
TensorFlow 2.x
Streamlit
NumPy
Pillow (PIL)
Matplotlib
## Technologies Used
Streamlit: A web framework to build interactive applications.
TensorFlow: For building and training the deep learning model.
Keras (TensorFlow API): Used to construct the model architecture.
Pillow: For image preprocessing.
Matplotlib: To visualize the prediction probabilities.
## Model Information
The model is a simple neural network with the following layers:

Input Layer: A flattened 32x32x3 input image.
Dense Layer: A fully connected layer with 1000 units and ReLU activation.
Output Layer: A softmax layer with 10 output units for class probabilities.
The model is trained on the CIFAR-10 dataset, which includes 60,000 32x32 color images in 10 different categories.

## Future Improvements
Add more complex architectures like CNNs for improved accuracy.
Implement image augmentation for better generalization.
Integrate an option to visualize the model’s activations or intermediate layers.
