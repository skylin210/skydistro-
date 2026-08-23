import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import mediapipe as mp
import numpy as np

# Page config
st.set_page_config(page_title="Real-Time Face Swap", layout="wide")
st.title("🎭 Real-Time Face Overlay Web App")
st.markdown("Upload a photo in the sidebar, allow camera access, and watch the magic!")

# --- Sidebar for Image Upload ---
st.sidebar.header("Upload Target Face")
uploaded_file = st.sidebar.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "png", "jpeg"])

target_face = None
if uploaded_file is not None:
    # Convert uploaded file to OpenCV image format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    target_face = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

# --- Initialize MediaPipe Face Mesh ---
# We use a singleton pattern so it doesn't re-initialize on every frame
@st.cache_resource
def load_face_mesh():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

face_mesh = load_face_mesh()

# --- Video Processing Callback ---
def video_frame_callback(frame):
    # Convert frame to OpenCV format (numpy array)
    img = frame.to_ndarray(format="bgr24")
    
    # If a target face is uploaded, process the frame
    if target_face is not None:
        # Convert to RGB for MediaPipe
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_img)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = img.shape
                x_min, x_max = w, 0
                y_min, y_max = h, 0
                
                # Find the bounding box of the face
                for lm in face_landmarks.landmark:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if cx < x_min: x_min = cx
                    if cx > x_max: x_max = cx
                    if cy < y_min: y_min = cy
                    if cy > y_max: y_max = cy
                
                # Add some padding to the bounding box
                padding = int((x_max - x_min) * 0.2)
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                face_w = x_max - x_min
                face_h = y_max - y_min
                
                if face_w > 0 and face_h > 0:
                    # Resize the target face to match the detected face size
                    resized_target = cv2.resize(target_face, (face_w, face_h))
                    
                    # Simple overlay (replace pixels in the bounding box)
                    # Note: For a seamless blend, you would use alpha masking or Poisson blending here
                    img[y_min:y_max, x_min:x_max] = resized_target

    # Convert back to av.VideoFrame for Streamlit
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- Streamlit WebRTC Camera Component ---
webrtc_streamer(
    key="face-swap-camera",
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": True,
        "audio": False
    },
    async_processing=True,
)

st.info("⚠️ **Note:** Browsers require HTTPS to access the camera. Streamlit Cloud provides this automatically. If the camera doesn't load, ensure you clicked 'Allow' on the browser permission prompt.")
