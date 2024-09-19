import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import tensorflow as tf
from PIL import Image

def image_classifier():
    # Add custom CSS for background and text styling
    st.markdown(
        """
        <style>
        body {
            background-color: #f5f5f5;
        }
        .stApp {
            background-image: url("https://www.transparenttextures.com/patterns/asfalt-light.png");
            background-size: cover;
        }
        h1 {
            color: #4B0082;
            font-family: 'Arial', sans-serif;
            text-align: center;
        }
        .stImage > img {
            border-radius: 10px;
        }
        .stFileUploader > div {
            background-color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('CIFAR-10 Web Classifier')
    st.write(
        "Upload an image from the following categories: **airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck**.")

    file = st.file_uploader('Upload your image:', type=['jpg', 'png'])

    if file:
        # Display the uploaded image
        image = Image.open(file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Preprocess the image
        resized_image = image.resize((32, 32))
        img_array = np.array(resized_image) / 255.0
        img_array = img_array.reshape((1, 32, 32, 3))

        # Load the trained model
        model = tf.keras.models.load_model('cifar10_model.h5')

        # Make predictions
        predictions = model.predict(img_array)
        cifar10_classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

        # Plot the predictions
        fig, ax = plt.subplots()
        y_pos = np.arange(len(cifar10_classes))
        ax.barh(y_pos, predictions[0], align='center', color='skyblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cifar10_classes)
        ax.invert_yaxis()  # Invert y-axis to have the highest probability on top
        ax.set_xlabel("Probability")
        ax.set_title("CIFAR-10 Predictions")

        st.pyplot(fig)

        # Show the top predicted class
        top_pred_index = np.argmax(predictions)
        st.subheader(
            f"Prediction: {cifar10_classes[top_pred_index].capitalize()} with confidence {predictions[0][top_pred_index]:.2f}")
    else:
        st.text("You haven't uploaded an image yet.")

if __name__ == '__main__':
    image_classifier()
