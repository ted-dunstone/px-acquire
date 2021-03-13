import streamlit as st
import os, uuid, yaml
import pathlib
import pandas as pd
import face_recognition
import math
import re
from datetime import date

st.image('https://bixelab.com/wp-content/uploads/2020/10/bixe-logo.png')

st.header('BixeLab Data Acquistion')

"""
# BixeLab Data Acquistion

Thankyou for agreeing to be part of the BixeLab test crew. The following information will help to make sure the next generation of identity products are secure. 

All information collected will be strictly managed in accordance with the Australian data privacy principles. 

This form should take between 5 and 10 minutes.

For more information please contact info@bixelab.com.

"""

#uid = str(uuid.uuid1())
#outdir = os.path.join('uploads', uid)
email = st.text_input('Your Email')

if not email:
  st.stop()

if re.match(r'[\w\.-]+@[\w\.-]+(\.[\w]+)+',email) is None:
  st.info("enter a valid email address")
  st.stop()

email_hash = str(abs(hash(email)))

outdir = os.path.join('uploads', email_hash, date.today().strftime("%Y-%m-%d"))
if not os.path.isdir(outdir):
    os.makedirs(outdir)


"""
## General Information

Please answer some general information about yourself.

**Note** To participate, you must be 18 years or older.
"""

left, center, right = st.beta_columns(3)
age = left.number_input('Your Age', min_value=18, max_value=120)
sex = right.radio('Your Sex', ('Male', 'Female', 'Other'))

"""
## Upload Photos

Please upload a photo for each of the following sections.
"""
def save_file(file, name):
    print(f"uploading file: {email} {name}")
    fname, ext = os.path.splitext(file.name)
    new_name = os.path.join(outdir, email_hash+'_'+name + ext)
    with open(new_name, 'wb') as f:
      f.write(file.getvalue())
    return new_name

def check_face(filename):
  image = face_recognition.load_image_file(filename)
  
  face_locations = face_recognition.face_locations(image)
  face_landmarks_list = face_recognition.face_landmarks(image)
  #st.write(face_landmarks_list)
  x_size,y_size,_ = image.shape

  import numpy as np

  cropped_img = None
  pixels_eyes = None
  roll = None
  shadow = None
  if len(face_locations)==1:
    top, right, bottom, left = face_locations[0]
    cropped_img = image[left:right,top:bottom].copy()
    half_width=int((right-left)/2)
    left_bright = np.mean(cropped_img[0:half_width,:])
    right_bright = np.mean(cropped_img[half_width:half_width*2-1,:])
    shadow = (left_bright-right_bright)/np.mean(cropped_img)
    
    face_pnts = face_landmarks_list[0]
    pixels_eyes = distance(face_pnts['left_eye'][0],face_pnts['right_eye'][0])
    #st.write("%3.2f %%"%(100.0*pixels_eyes/x_size))
    roll=(angle(face_pnts['left_eye'][0],face_pnts['right_eye'][0]))
  return {'found':len(face_locations),"crop":cropped_img, "eye_dist": pixels_eyes,"roll":roll, "shadow": shadow}

def distance(p1,p2):
  return math.sqrt(math.pow(p1[0]-p2[0],2)+math.pow(p1[1]-p2[1],2))

def angle_trunc(a):
    while a < 0.0:
        a += math.pi * 2
    return a

def angle(p1, p2):
    return 180-math.degrees(angle_trunc(math.atan2(p1[1]-p2[1], p1[0]-p2[0])))

def upload_face_image(title,instruction,description,is_face=True):
  st.header(title)
  st.markdown(instruction)
  cols = st.beta_columns(2)
  upload_file = cols[0].file_uploader(description,key=title)
  if not upload_file:
    st.stop()
  fname = save_file(upload_file,description)
  
  results = check_face(fname)
  
  if is_face and results['found']!=1:
    st.error('No face found in the image. Please try again.')
    st.stop()
  
  if results["eye_dist"]<70:
    st.error(f'The face is not big enough. Only {int(results["eye_dist"])} pixels between the eyes.')
    st.stop()

  if results["roll"]>10:
    st.error(f'The face is not straight. Please try taking a straighter `selfie`. ({results["roll"]})')
    st.stop()

  st.info('face OK')
  cols[1].image(results["crop"])

upload_face_image("selfie_front","""
Take a `selfie` with this following:
* looking straight at the camera
* with your face filling most of the picture
* with even lighting 
* and with a neutral expression. 
""","good")
upload_face_image("selfie_expression","""
Take a `selfie` with this following:
* looking at the camera with a slight head turn
* with your face filling most of the picture
* with normal lighting 
* and with a relaxed expression. 
""","natural")
upload_face_image("selfie_distance","""
Take a `selfie` with this following:
* looking at the camera with a slight head turn
* with your face a bit further away
""","distant")
upload_face_image("passport_style","""
A high quality older picture (passport or drivers licence style). Do not take a photo of your passport or driver licence as the photo's will not be good quailty. This photo should be:
* More than 1 year ago and less than 10 years ago 
* Be full frontal and with you looking directly at the camera
* Have good lighting 
* With the face filling most of the photo
""","passport")

approx_age = st.radio('Approximately how long ago was this photo taken', ('1-2 year', '2-4 years', '4-7 years', '7-10 years'))

"""
## Data Usage

Your data will be securely stored ....

You can opt in to allow us to retain your data for future use.
"""

  
retain_data = st.checkbox('Allow data reuse')

st.subheader('Do you accept terms and conditions?')
accept_terms = st.checkbox('Accept terms and conditions')

if not accept_terms:
  st.stop()

# validate
#if not (selfie and document):
#  st.warning('Selfie and document photo are required.')
#  st.stop()

complete = st.button('submit')

# print(f'{uid} {email}, {age}, {sex}, {len(files)}, {complete}')

if complete:
  data = {
    'date': str(date.today()),
    'email': email,
    'appox_ref_age':approx_age,
    'age': age,
    'sex': sex,
    'allow_reuse': retain_data,
    'accept_terms': accept_terms,
  }
  
  with open(os.path.join(outdir, '_info.yaml'), 'w') as f:
    f.write(yaml.dump(data))

  """
  # Finished

  Thank you for providing your information. 

  If this is the first time *please* come back and do this again next week
  """

  
  

