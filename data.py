import streamlit as st
import os, uuid, yaml
import pathlib
import pandas as pd

st.header('Upload test app')

uid = str(uuid.uuid1())
email = st.text_input('Your Email')

if not email:
  st.stop()

st.markdown(
  '''
  ## General Information

  Please answer some general information about yourself.

  **Note** To participate, you must be 18 years or older.
  '''
)

left, center, right = st.beta_columns(3)
age = left.number_input('Your Age', min_value=18, max_value=120)
sex = right.radio('Your Sex', ('Male', 'Female', 'Other'))

st.markdown(
  '''
  ## Upload Photos

  Please upload a photo for each of the following sections.
  '''
)

st.header('Document')
document = st.file_uploader('Upload/Take photo of document')

st.header('Front selfie')
selfie = st.file_uploader('Upload/Take Selfie')

st.markdown(
  '''
  ## Data Usage

  Your data will be securely stored ....

  You can opt in to allow us to retain your data for future use.
  '''
)
retain_data = st.checkbox('Allow data reuse')

st.subheader('Do you accept terms and conditions?')
accept_terms = st.checkbox('Accept terms and conditions')

if not accept_terms:
  st.stop()

# validate
if not (selfie and document):
  st.warning('Selfie and document photo are required.')
  st.stop()

complete = st.button('submit')

# print(f'{uid} {email}, {age}, {sex}, {len(files)}, {complete}')

if complete:
  outdir = os.path.join('uploads', uid)
  if not os.path.isdir(outdir):
    os.makedirs(outdir)
  
  def save_file(file, name):
    print(f"uploading file: {email} {name}")
    fname, ext = os.path.splitext(file.name)
    with open(os.path.join(outdir, name + ext), 'wb') as f:
      f.write(file.getvalue())
  
  save_file(document, 'document')
  save_file(selfie, 'selfie')

  data = {
    'uuid': uid,
    'email': email,
    'age': age,
    'sex': sex,
    'allow_reuse': retain_data,
    'accept_terms': accept_terms,
  }
  
  with open(os.path.join(outdir, '_info.yaml'), 'w') as f:
    f.write(yaml.dump(data))

  st.markdown(
    '''
    # Form Success

    Thank you for providing your information. We will be in contact.
    '''
  )
