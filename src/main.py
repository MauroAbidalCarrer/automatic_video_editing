import os
import tempfile
from collections import defaultdict

import streamlit as st
from streamlit import session_state

from video_editing import create_clip
from config import DEFAULT_BPM, DEFAULT_DURATION, NB_KEYS_PER_AUDIO_TRACK


def main():
    st.title("Video Clip Creator")

    # Create a temp dir for this session
    if "tempdir" not in session_state:
        session_state.tempdir = tempfile.TemporaryDirectory()
        session_state.image_paths = []
        session_state.prev_picture = None
        # list of dicts containing keys file, bpm and duration
        session_state.audio_tracks = []
        session_state.nb_tracks = 3

    # Pictures
    st.subheader("Step 1: Capture Photos")
    # Reset pictures
    if st.button("Reset Photos"):
        session_state.image_paths = []
    # Take pictures
    picture = st.camera_input("Take a photo")
    if picture is not None and session_state.prev_picture != picture:
        session_state.prev_picture = picture
        img_idx = len(session_state.image_paths)
        image_path = os.path.join(session_state.tempdir.name, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        session_state.image_paths.append(image_path)
        st.success(f"Captured photo #{img_idx + 1}")
        # Display nb of pictures taken
    st.write(f"{len(session_state.image_paths)} photo(s) taken.")
    # Check that at least one picture has been taken
    if len(session_state.image_paths) == 0:
        st.warning("Please take at least one photo and upload an audio file.")
        return

    # Audio tracks
    st.subheader("Audio tracks")
    # Add audio track
    if st.button("Add new audio track"):
        session_state.nb_tracks += 1
    # audio track inputs
    for track_idx in range(session_state.nb_tracks):
        create_audio_track_inputs(track_idx)
    track_has_file = lambda track: track["file"] is not None
    if not all(map(track_has_file, session_state.audio_tracks)):
        st.warning("Please provide an audio file for all the audio tracks.")
        return

    # Videos
    if st.button("Create Video"):
        for track_idx, track in enumerate(session_state.audio_tracks):
            create_and_display_video(track_idx, track)

def create_audio_track_inputs(track_idx: int):
    audio_tracks = session_state.audio_tracks
    if len(audio_tracks) <= track_idx:
        audio_track = defaultdict(
            file=None,
            bpm=DEFAULT_BPM,
            duration=DEFAULT_DURATION
        )
        audio_tracks.append(audio_track)
    else:
        audio_track = session_state.audio_tracks[track_idx]
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        audio_track["file"] = st.file_uploader(
            "Audio File",
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK,
        )
    with col2:
        audio_track["bpm"] = st.number_input(
            "BPM",
            min_value=1.0,
            value=DEFAULT_BPM,
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 1)
    with col3:
        audio_track["duration"] = st.number_input(
            "Duration (s)",
            min_value=1.0,
            value=DEFAULT_DURATION,
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 2
        )

def create_and_display_video(track_idx: int, track: defaultdict):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out_file:
        audio_path = os.path.join(session_state.tempdir.name, track["file"].name)
        with open(audio_path, "wb") as f:
            f.write(track["file"].getbuffer())
        create_clip(
            image_paths=session_state.image_paths,
            audio_path=audio_path,
            bpm=track["bpm"],
            duration=track["duration"],
            output_path=out_file.name
        )
        f = open(out_file.name, "rb")
        st.video(f.read())
        st.download_button(
            "Download Video",
            f,
            file_name="output.mp4",
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 3
        )
        f.close()

if __name__ == "__main__":
    main()