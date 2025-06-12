import os
import base64
from datetime import datetime
import tempfile
from collections import defaultdict
from os.path import join, splitext, split

import streamlit as st
from streamlit import session_state
from streamlit.components.v1 import html

import video_editing
from s3_utils import upload_file_to_bucket
from config import DEFAULT_BPM, DEFAULT_DURATION, NB_KEYS_PER_AUDIO_TRACK


def main():
    st.title("Video Clip Creator")

    # Set up the session
    if "tempdir" not in session_state:
        session_state.tempdir = tempfile.TemporaryDirectory()
        session_state.image_paths = []
        session_state.prev_picture = None
        session_state.session_key = 0
        # list of dicts containing "file", "bpm" and "duration" keys
        session_state.audio_tracks = [mk_track_dict()]
        # List of strings of the clips_paths paths 
        session_state.clips_paths = []

    # Audio tracks
    st.subheader("Audio tracks")
    # Add audio track
    if st.button(r"\+ audio track"):
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
        key=f"uploaded_images_{session_state.session_key}",
        label_visibility="visible",
    )
    if uploaded_images:
        for uploaded_img in uploaded_images:
            img_idx = len(session_state.image_paths)
            image_path = os.path.join(session_state.tempdir.name, f"uploaded_{img_idx}.jpg")
            with open(image_path, "wb") as f:
                f.write(uploaded_img.getbuffer())
            session_state.image_paths.append(image_path)
        session_state.session_key += 1
        st.rerun()

    # Display nb of pictures taken
    st.write(f"{len(session_state.image_paths)} photo(s) taken.")
    # Check that at least one picture has been taken
    if len(session_state.image_paths) == 0:
        st.warning("Please take at least one photo and upload an audio file.")
        return
    st.subheader("Images")
    display_image_carousel(session_state.image_paths)

    # Videos
    if st.button("Create new videos"):
        for clip_path in session_state.clips_paths:
            print("deleting", clip_path)
            os.remove(clip_path)
        session_state.clips_paths = []
        for track_idx, track in enumerate(session_state.audio_tracks):
            session_state.clips_paths.append(create_clip(track))

    for video_filename in session_state.clips_paths:
        display_video(video_filename)

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
    # Band aid fix: 
    # In case the clear photo button was not pressed the st.camera_input will return the last picture taken.
    # This would erroneously add the same picture to the image paths.
    if picture is not None and session_state.prev_picture != picture:
        session_state.prev_picture = picture 
        img_idx = len(session_state.image_paths)
        image_path = os.path.join(session_state.tempdir.name, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        session_state.image_paths.append(image_path)

def display_image_carousel(image_paths):
    # Read and encode all images to base64
    base64_images = []
    for path in image_paths:
        with open(path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode("utf-8")
            base64_images.append(f"data:image/jpeg;base64,{b64}")
    # Build the HTML carousel
    html_code = f"""
    <div style="display: flex; overflow-x: auto; gap: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 10px;">
        {''.join([f'<img src="{src}" style="height: 150px; border-radius: 8px;" />' for src in base64_images])}
    </div>
    """
    html(html_code, height=180)

def create_clip(track: defaultdict) -> str:
    """
    ### Description:
    Wrapper around video_editing.create_clip to prepare its inputs.
    ### Returns:
    Returns the path to the clip file. 
    """
    audio_path = join(session_state.tempdir.name, track["file"].name)
    audio_name, audio_ext = splitext(track["file"].name) 
    datetime_str = datetime.now().strftime("%d-%m-%Y:%H-%M-%S")
    # to str in case splitext returns None
    video_filename = f"{str(audio_name)}_bpm{int(track['bpm'])}_{datetime_str}.mp4"
    # For some reason, I couldn't access the file provided by the fileuploader.
    # So create a temp file as aid band fix (yet another one).
    with tempfile.NamedTemporaryFile(suffix=audio_ext) as audio_file:
        audio_file.write(track["file"].getbuffer())
        video_editing.create_clip(
            image_paths=session_state.image_paths,
            audio_path=audio_file.name,
            bpm=track["bpm"],
            duration=track["duration"],
            output_path=video_filename
        )
        return video_filename

def display_video(video_file_path: str):
    with open(video_file_path, "rb") as video_file:
        clip_filename = split(video_file_path)[1]
        st.subheader(clip_filename)
        st.video(video_file.read())
        st.download_button(
            "Download Video",
            video_file,
            file_name=clip_filename,
            key=video_file_path
        )


if __name__ == "__main__":
    main()