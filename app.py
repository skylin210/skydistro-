import streamlit as st
import pandas as pd
import os, uuid, base64, requests
from datetime import datetime

st.set_page_config(page_title="SkyDistro - Permanent", page_icon="🚀", layout="centered")

ADMIN_PASSWORD = "skylin123"
DB_FILE = "releases.csv"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "skylin210/skydistro-")

def upload_to_github(file_bytes, github_path):
    if not GITHUB_TOKEN:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    payload = {
        "message": f"Upload {github_path}",
        "content": base64.b64encode(file_bytes).decode(),
    }
    if sha:
        payload["sha"] = sha
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code in [200,201]

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["date","artist","song","genre","email","upc","isrc","status","audio_path","cover_path"]).to_csv(DB_FILE, index=False)

st.title("🚀 SkyDistro")
st.caption("From Enugu to the World 🌍 | Permanent Storage: ACTIVE ✅")
st.divider()

menu = st.sidebar.selectbox("Menu", ["Upload Music", "Check Status", "Admin Panel"])

if menu == "Upload Music":
    st.subheader("Upload Your Release")
    st.success("✅ Permanent Storage Enabled - Songs will never delete again")
    with st.form("upload"):
        artist = st.text_input("Artist Name *")
        email = st.text_input("Email / WhatsApp *")
        song = st.text_input("Song Title *")
        genre = st.selectbox("Genre", ["Afrobeats","Hip-Hop","Gospel","Highlife","R&B","Amapiano","Drill","Other"])
        audio = st.file_uploader("Audio File WAV/MP3 *", type=["mp3","wav","flac"])
        cover = st.file_uploader("Cover Art JPG 3000x3000 *", type=["jpg","jpeg","png"])
        agree = st.checkbox("I own this song 100%")
        submit = st.form_submit_button("🚀 SUBMIT FOREVER")

        if submit:
            if not all([artist,email,song,audio,cover,agree]):
                st.error("Fill all fields")
            else:
                upc = str(uuid.uuid4().int)[:13]
                isrc = f"NG{datetime.now().year}SKY{str(uuid.uuid4().int)[:5]}"
                safe_name = f"{artist}_{song}".replace(" ", "_")
                audio_path = f"uploads/audio/{safe_name}_{audio.name}"
                cover_path = f"uploads/covers/{safe_name}_{cover.name}"

                with st.spinner("Saving to GitHub forever..."):
                    ok1 = upload_to_github(audio.getbuffer().tobytes(), audio_path)
                    ok2 = upload_to_github(cover.getbuffer().tobytes(), cover_path)
                    df = pd.read_csv(DB_FILE)
                    new = {"date": datetime.now().strftime("%Y-%m-%d"), "artist": artist, "song": song, "genre": genre, "email": email, "upc": upc, "isrc": isrc, "status": "Pending", "audio_path": audio_path, "cover_path": cover_path}
                    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    with open(DB_FILE, "rb") as f:
                        upload_to_github(f.read(), DB_FILE)

                st.success(f"🔥 {song} by {artist} SAVED FOREVER on GitHub!")
                st.info(f"UPC: {upc}\nISRC: {isrc}\nPath: {audio_path}")

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
        st.write(f"Total Releases: {len(df)}")
        if GITHUB_TOKEN:
            st.success("GitHub Storage Connected ✅")
        else:
            st.error("No GitHub Token Found")
