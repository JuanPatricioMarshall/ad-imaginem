# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py

# import the necessary packages
from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import requests
import flask
from flask import Flask, request
import io
import json
from jinja2 import Template
import os


from flask import render_template, redirect, url_for



# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
# set the project root directory as the static folder, you can set others.
#app = Flask(__name__, static_url_path='')
model = None

def load_model():
	# load the pre-trained Keras model (here we are using a model
	# pre-trained on ImageNet and provided by Keras, but you can
	# substitute in your own networks just as easily)
	global model
	model = ResNet50(weights="imagenet")

def prepare_image(image, target):
	# if the image mode is not RGB, convert it
	if image.mode != "RGB":
		image = image.convert("RGB")

	# resize the input image and preprocess it
	image = image.resize(target)
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	image = imagenet_utils.preprocess_input(image)

	# return the processed image
	return image


	
@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}

	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":

		if flask.request.form.get("image_url"):
			response = requests.get(flask.request.form.get("image_url"))
			image = Image.open(io.BytesIO(response.content))
			# read the image in PIL format
			#image = flask.request.files["image"].read()
			#image = Image.open(io.BytesIO(image))

			# preprocess the image and prepare it for classification
			image = prepare_image(image, target=(224, 224))

			# classify the input image and then initialize the list
			# of predictions to return to the client
			preds = model.predict(image)
			results = imagenet_utils.decode_predictions(preds)
			data["predictions"] = []

			# loop over the results and add them to the list of
			# returned predictions
			for (imagenetID, label, prob) in results[0]:
				r = {"label": label, "probability": round(float(prob),2)}
				data["predictions"].append(r)

			# indicate that the request was a success
			data["success"] = True
			data["image_url"] = flask.request.form.get("image_url")
	# return the data dictionary as a JSON response
	return render_template('response.html', data=data)

@app.route("/predict_p", methods=["POST"])
def predict_p():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}
	print(flask.request.form)
	# ensure an image was properly uploaded to our endpoint
	if flask.request.method == "POST":

		if flask.request.files.get("image"):
			#response = requests.get(flask.request.form.get("image_url"))
			#image = Image.open(io.BytesIO(response.content))
			# read the image in PIL format
			image = flask.request.files["image"].read()
			image = Image.open(io.BytesIO(image))
			# preprocess the image and prepare it for classification
			image = prepare_image(image, target=(224, 224))

			# classify the input image and then initialize the list
			# of predictions to return to the client
			preds = model.predict(image)
			results = imagenet_utils.decode_predictions(preds)
			data["predictions"] = []

			# loop over the results and add them to the list of
			# returned predictions
			for (imagenetID, label, prob) in results[0]:
				r = {"label": label, "probability": round(float(prob),2)}
				data["predictions"].append(r)

			# indicate that the request was a success
			data["success"] = True
			data["image"] = flask.request.files["image"]
	# return the data dictionary as a JSON response
	return render_template('response2.html', data=data)

@app.route('/')
def index():
    return render_template("index.html")




# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))
	load_model()
	app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"))
	port = int(os.environ.get("PORT", 33507))
app.run(host='0.0.0.0', port=port)
