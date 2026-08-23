import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

st.set_page_config(page_title="Real-Time Face Overlay", layout="wide")
st.title(" Face Overlay App")
st.markdown("Upload a photo and use your camera to see the overlay!")

# Sidebar for image upload
st.sidebar.header("Upload Target Face")
uploaded_file = st.sidebar.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "png", "jpeg"])

target_face = None
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    target_face = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

# Initialize MediaPipe
@st.cache_resource
def load_face_mesh():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

# Use Streamlit's built-in camera input
st.markdown("### Take a photo with your camera:")
img_file_buffer = st.camera_input("Take a photo")

if img_file_buffer is not None:
    # Read the image
    image = Image.open(img_file_buffer)
    img_array = np.array(image)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    if target_face is not None:
        # Process the image
        face_mesh = load_face_mesh()
        rgb_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_img)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = img_bgr.shape
                x_min, x_max = w, 0
                y_min, y_max = h, 0
                
                for lm in face_landmarks.landmark:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if cx < x_min: x_min = cx
                    if cx > x_max: x_max = cx
                    if cy < y_min: y_min = cy
                    if cy > y_max: y_max = cy
                
                face_w = x_max - x_min
                face_h = y_max - y_min
                
                if face_w > 0 and face_h > 0:
                    resized_target = cv2.resize(target_face, (face_w, face_h))
                    img_bgr[y_min:y_max, x_min:x_max] = resized_target
        
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), caption="Result with Face Overlay")
    else:
        st.image(image, caption="Your photo")
else:
    st.write("⬆️ Upload a target face in the sidebar and click the camera button above!")
