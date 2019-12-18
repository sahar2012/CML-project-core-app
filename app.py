#
# Cloud for ML Final Project
# Sahar Siddiqui
# app.py
#

from flask import Flask
import os
import urllib.request
from flask import Flask, flash, request, redirect, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import base64
import sys
from io import BytesIO
import requests

UPLOAD_FOLDER = '.'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

SALIENCY_APP_URL = 'http://184.172.253.3:31546/'
GRADCAM_APP_URL = 'http://173.193.112.169:30719'
WTVIZ_APP_URL = 'http://184.173.1.97:30769'

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('index2.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			print('No file')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No image selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):

			viz_choice = request.form['radio-inline']
			filename = secure_filename(file.filename)
			original_image = Image.open(file, mode='r')
			original_image.save(filename)
			original_image.close()
			file.seek(0)
			encoded_img = base64.b64encode(file.read())
			data = {'img': encoded_img.decode("utf-8")}

			if(viz_choice=="saliency"):

				r = requests.post(url=SALIENCY_APP_URL, json=data)
				print(r.json().keys())

				predictedLabel = "%r" % r.json()['class']
				predProbability = "%r" % r.json()['probability']
			
			
				raw1 = "%r" % r.json()['blurredImage']
				b1 = BytesIO(base64.b64decode(raw1))
				im1 = Image.open(b1)
				result_filename1 = 'blurred_' + filename
				im1.save(result_filename1)

				raw2 = "%r" % r.json()['maskImage']
				b2 = BytesIO(base64.b64decode(raw2))
				im2 = Image.open(b2)
				result_filename2 = 'masked_' + filename
				im2.save(result_filename2)

				raw3 = "%r" % r.json()['unblurredMask']
				b3 = BytesIO(base64.b64decode(raw3))
				im3 = Image.open(b3)
				result_filename3 = 'unblurredMask_' + filename
				im3.save(result_filename3)

				return redirect(url_for('uploaded_file_saliency', filename = filename, filename1=result_filename1, 
					filename2=result_filename2, filename3=result_filename3, predictedLabel = predictedLabel, 
					predProbability = predProbability))

			elif(viz_choice=="gradcam"):

				r = requests.post(url=GRADCAM_APP_URL, json=data)
				print(r.json().keys())

				predictedLabel = "%r" % r.json()['class']
				predProbability = "%r" % r.json()['probability']

				raw1 = "%r" % r.json()['gradCAM']
				b1 = BytesIO(base64.b64decode(raw1))
				im1 = Image.open(b1)
				result_filename1 = 'gradCAM_' + filename
				im1.save(result_filename1)

				raw2 = "%r" % r.json()['cropped']
				b2 = BytesIO(base64.b64decode(raw2))
				im2 = Image.open(b2)
				result_filename2 = 'cropped_' + filename
				im2.save(result_filename2)

				raw3 = "%r" % r.json()['gradCAM_unguided']
				b3 = BytesIO(base64.b64decode(raw3))
				im3 = Image.open(b3)
				result_filename3 = 'gradCAM_unguided_' + filename
				im3.save(result_filename3)

				return redirect(url_for('uploaded_file_gradcam', filename = filename, filename1=result_filename1, 
					filename2=result_filename2, filename3=result_filename3, predictedLabel = predictedLabel, 
					predProbability = predProbability))

			elif(viz_choice=="wtviz"):
				layer_choice = request.form['layer-select']
				data['layer'] = layer_choice

				r = requests.post(url=WTVIZ_APP_URL, json=data)
				print(r.json().keys())

				predictedLabel = "%r" % r.json()['class']
				predProbability = "%r" % r.json()['probability']

				raw1 = "%r" % r.json()['layer_weight_output']
				b1 = BytesIO(base64.b64decode(raw1))
				im1 = Image.open(b1)
				result_filename1 = 'layer_weight_output_' + layer_choice + "_" + filename
				im1.save(result_filename1)

				return redirect(url_for('uploaded_file_wtviz', filename = filename, filename1=result_filename1, 
					predictedLabel = predictedLabel, predProbability = predProbability))
				
		else:
			flash('Allowed file types are png, jpg, jpeg')
			return redirect(request.url)

@app.route('/show/<filename>&<filename1>&<filename2>&<filename3>&<predictedLabel>&<predProbability>')
def uploaded_file_saliency(filename,filename1,filename2,filename3,predictedLabel,predProbability):
	print("uploaded: " + filename)
	print("uploaded: " + filename1)
	print("uploaded: " + filename2)
	print("uploaded: " + filename3)
	print("predictedLabel: " + predictedLabel)
	print("predProbability: " + predProbability)
	return render_template('timeline.html', filename=filename, filename1=filename1, 
		filename2=filename2, filename3=filename3, predictedLabel = predictedLabel, 
		predProbability = predProbability)

@app.route('/show2/<filename>&<filename1>&<filename2>&<filename3>&<predictedLabel>&<predProbability>')
def uploaded_file_gradcam(filename,filename1,filename2,filename3,predictedLabel,predProbability):
	print("uploaded: " + filename)
	print("uploaded: " + filename1)
	print("uploaded: " + filename2)
	print("uploaded: " + filename3)
	print("predictedLabel: " + predictedLabel)
	print("predProbability: " + predProbability)
	return render_template('timeline2.html', filename=filename, filename1=filename1, 
		filename2=filename2, filename3=filename3, predictedLabel = predictedLabel, 
		predProbability = predProbability)

@app.route('/show/<filename>&<filename1>&<predictedLabel>&<predProbability>')
def uploaded_file_wtviz(filename,filename1,predictedLabel,predProbability):
	print("uploaded: " + filename)
	print("uploaded: " + filename1)
	print("predictedLabel: " + predictedLabel)
	print("predProbability: " + predProbability)
	return render_template('timeline3.html', filename=filename, filename1=filename1, 
		predictedLabel = predictedLabel, predProbability = predProbability)

@app.route('/uploads/<filename>')
def send_file(filename):
	print("send_file: " + filename)
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5003)