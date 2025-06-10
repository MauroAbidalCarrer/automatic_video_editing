import os
import tempfile
from collections import defaultdict

import streamlit as st
from streamlit import session_state

from video_editing import create_clip
from config import DEFAULT_BPM, DEFAULT_DURATION, NB_KEYS_PER_AUDIO_TRACK


def main():
    st.title("Video Clip Creator")

    # Set up the session
    if "tempdir" not in session_state:
        session_state.tempdir = tempfile.TemporaryDirectory()
        session_state.image_paths = []
        session_state.prev_picture = None
        session_state.prev_uploaded_pictures = None
        # list of dicts containing keys file, bpm and duration
        session_state.audio_tracks = [mk_track_dict()]

    # Audio tracks
    st.subheader("Audio tracks")
    # Add audio track
    if st.button("Add new audio track"):
        session_state.audio_tracks.append(mk_track_dict())
    # audio track inputs
    for track_idx, track in enumerate(session_state.audio_tracks):
        create_audio_track_inputs(track_idx, track)
    track_has_file = lambda track: track["file"] is not None
    if not all(map(track_has_file, session_state.audio_tracks)):
        st.warning("Please provide an audio file for all the audio tracks.")
        return

    # Pictures
    st.subheader("Pictures")
    # Reset pictures
    if st.button("Reset Photos"):
        session_state.image_paths = []
    # Take pictures
    picture_from_camera()
    # Add image uploader to upload multiple images
    uploaded_images = st.file_uploader(
        "Upload image(s)",
        accept_multiple_files=True,
        key="uploaded_images",
    )
    if uploaded_images and session_state.prev_uploaded_pictures != uploaded_images:
        session_state.prev_uploaded_pictures = uploaded_images
        for uploaded_img in uploaded_images:
            img_idx = len(session_state.image_paths)
            image_path = os.path.join(session_state.tempdir.name, f"uploaded_{img_idx}.jpg")
            with open(image_path, "wb") as f:
                f.write(uploaded_img.getbuffer())
            session_state.image_paths.append(image_path)

    # Display nb of pictures taken
    st.write(f"{len(session_state.image_paths)} photo(s) taken.")
    # Check that at least one picture has been taken
    if len(session_state.image_paths) == 0:
        st.warning("Please take at least one photo and upload an audio file.")
        return

    # Videos
    if st.button("Create Video"):
        for track_idx, track in enumerate(session_state.audio_tracks):
            create_and_display_video(track_idx, track)

def mk_track_dict() -> defaultdict:
    return defaultdict(
            file=None,
            bpm=DEFAULT_BPM,
            duration=DEFAULT_DURATION
        )

def create_audio_track_inputs(track_idx: int, track: defaultdict):
    spec = [3, 1, 1, 1] if track_idx else [3, 1, 1]
    cols = st.columns(spec)
    with cols[0]:
        track["file"] = st.file_uploader(
            "Audio File",
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK,
        )
    with cols[1]:
        track["bpm"] = st.number_input(
            "BPM",
            min_value=1.0,
            value=DEFAULT_BPM,
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 1)
    with cols[2]:
        track["duration"] = st.number_input(
            "Duration (s)",
            min_value=1.0,
            value=DEFAULT_DURATION,
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 2
        )
    if track_idx:
        with cols[3]:
            if st.button("Remove track", key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 3):
                del session_state.audio_tracks[track_idx]
                st.rerun()

def picture_from_camera():
    picture = st.camera_input("Take a photo")
    # Rubber band aid fix: 
    # In case the clear photo button was not pressed the st.camera_input will return the last picture taken.
    # This would erroneously add the same picture to the image paths.
    if picture is not None and session_state.prev_picture != picture:
        session_state.prev_picture = picture 
        img_idx = len(session_state.image_paths)
        image_path = os.path.join(session_state.tempdir.name, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        session_state.image_paths.append(image_path)

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
            key=track_idx * NB_KEYS_PER_AUDIO_TRACK + 4
        )
        f.close()

if __name__ == "__main__":
    main()