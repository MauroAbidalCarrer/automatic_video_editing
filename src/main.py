import os
import tempfile
from collections import defaultdict

import streamlit as st
from streamlit import session_state

from video_editing import create_clip
from config import DEFAULT_BPM, DEFAULT_DURATION


def main():
    st.title("Video Clip Creator")

    # Create a temp dir for this session
    if "tempdir" not in session_state:
        session_state.tempdir = tempfile.TemporaryDirectory()
        session_state.image_paths = []
        session_state.prev_picture = None
        # list of dicts containing keys file, bpm and duration
        session_state.audio_tracks = []

    tempdir = session_state.tempdir.name
    image_paths = session_state.image_paths

    # Pictures
    st.subheader("Step 1: Capture Photos")
    # Reset pictures
    if st.button("Reset Photos"):
        session_state.image_paths = []
    # Take pictures
    picture = st.camera_input("Take a photo")
    if picture is not None and session_state.prev_picture != picture:
        session_state.prev_picture = picture
        img_idx = len(image_paths)
        image_path = os.path.join(tempdir, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        image_paths.append(image_path)
        st.success(f"Captured photo #{img_idx + 1}")
        # Display nb of pictures taken
    st.write(f"{len(image_paths)} photo(s) taken.")
    # Check that at least one picture has been taken
    if len(image_paths) == 0:
        st.warning("Please take at least one photo and upload an audio file.")
        return
    # Audio
    st.subheader("Audio tracks")
    for i in range(3):
        create_audio_track_inputs(i)
    track_has_file = lambda track: track["file"] is not None
    if not all(map(track_has_file, session_state.audio_tracks)):
        st.warning("Please provide an audio file for all the audio tracks.")
        return

    audio_file = session_state.audio_tracks[0]["file"]
    bpm = session_state.audio_tracks[0]["bpm"]
    duration = session_state.audio_tracks[0]["duration"]
    if st.button("Create Video"):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out_file:
            audio_path = os.path.join(tempdir, audio_file.name)
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())
            create_clip(
                image_paths=image_paths,
                audio_path=audio_path,
                bpm=bpm,
                duration=duration,
                output_path=out_file.name
            )
            f = open(out_file.name, "rb")
            st.video(f.read())
            st.download_button("Download Video", f, file_name="output.mp4")
            f.close()

def create_audio_track_inputs(line_index: int):
    audio_tracks = session_state.audio_tracks
    print("len(audio_tracks):", len(audio_tracks), len(audio_tracks) <= line_index)
    if len(audio_tracks) <= line_index:
        print("Adding new audio track")
        audio_track = defaultdict(
            file=None,
            bpm=DEFAULT_BPM,
            duration=DEFAULT_DURATION
        )
        audio_tracks.append(audio_track)
    else:
        audio_track = session_state.audio_tracks[line_index]
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        audio_track["file"] = st.file_uploader(
            "Audio File",
            key=line_index * 3,
        )
    with col2:
        audio_track["bpm"] = st.number_input(
            "BPM",
            min_value=1.0,
            value=DEFAULT_BPM,
            key=line_index * 3 + 1)
    with col3:
        audio_track["duration"] = st.number_input(
            "Duration (s)",
            min_value=1.0,
            value=DEFAULT_DURATION,
            key=line_index * 3 + 2
        )

if __name__ == "__main__":
    main()