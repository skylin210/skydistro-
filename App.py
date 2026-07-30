import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

st.set_page_config(page_title="SkyDistro", page_icon="🚀", layout="centered")

ADMIN_PASSWORD = "skylin123"
UPLOAD_FOLDER = "uploads"
os.makedirs(f"{UPLOAD_FOLDER}/audio", exist_ok=True)
os.makedirs(f"{UPLOAD_FOLDER}/covers", exist_ok=True)
DB_FILE = "releases.csv"

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["date","artist","song","genre","email","upc","isrc","status"]).to_csv(DB_FILE, index=False)

st.title("🚀 SkyDistro")
st.caption("From Enugu to the World - Distribute to Spotify, Apple, Boomplay & 150+ stores")
st.divider()

menu = st.sidebar.selectbox("Menu", ["Upload Music", "Check Status", "Admin Panel"])

if menu == "Upload Music":
    st.subheader("Upload Your Release")
    st.info("Free distribution • You keep 80% • Paid via Opay/Bank")
    with st.form("upload"):
        artist = st.text_input("Artist Name *")
        email = st.text_input("Email / WhatsApp *")
        song = st.text_input("Song Title *")
        genre = st.selectbox("Genre", ["Afrobeats","Hip-Hop","Gospel","Highlife","R&B","Amapiano","Drill","Other"])
        audio = st.file_uploader("Audio File WAV/MP3 *", type=["mp3","wav","flac"])
        cover = st.file_uploader("Cover Art JPG 3000x3000 *", type=["jpg","jpeg","png"])
        agree = st.checkbox("I own this song 100%")
        submit = st.form_submit_button("🚀 SUBMIT TO SKYDISTRO")

        if submit:
            if not all([artist,email,song,audio,cover,agree]):
                st.error("Fill all fields")
            else:
                upc = str(uuid.uuid4().int)[:13]
                isrc = f"NG{datetime.now().year}SKY{str(uuid.uuid4().int)[:5]}"
                with open(f"{UPLOAD_FOLDER}/audio/{artist}_{song}_{audio.name}", "wb") as f:
                    f.write(audio.getbuffer())
                with open(f"{UPLOAD_FOLDER}/covers/{artist}_{song}_{cover.name}", "wb") as f:
                    f.write(cover.getbuffer())
                df = pd.read_csv(DB_FILE)
                df = pd.concat([df, pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d"), "artist": artist, "song": song, "genre": genre, "email": email, "upc": upc, "isrc": isrc, "status": "Pending"}])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success(f"Received! {song} by {artist}")
                st.write(f"UPC: {upc} | ISRC: {isrc}")
                st.write("Live in 2-3 days, we will notify you!")

elif menu == "Check Status":
    st.subheader("Check Status")
    q = st.text_input("Enter your email")
    if q:
        df = pd.read_csv(DB_FILE)
        st.dataframe(df[df['email'].str.contains(q, case=False, na=False)])

else:
    st.subheader("Admin - SkyLin Only")
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        df = pd.read_csv(DB_FILE)
        st.dataframe(df)
        edited = st.data_editor(df)
        if st.button("Save Changes"):
            edited.to_csv(DB_FILE, index=False)
            st.success("Saved! Commit on GitHub")
