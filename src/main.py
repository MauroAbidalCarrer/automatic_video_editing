# app.py
import os
import tempfile
import streamlit as st
from logging import getLogger
from moviepy import ImageSequenceClip, AudioFileClip, clips_array
from moviepy.video.fx import Rotate

logger = getLogger("streamlit_app")

def create_clip_from_files(
    image_paths: list[str],
    audio_path: str,
    fps: float,
    duration: float,
    output_path: str
):
    # Load audio
    audio = AudioFileClip(audio_path).with_duration(duration)

    # Loop or trim image sequence to match duration
    nb_frames = int(fps * duration)
    paths = [image_paths[i % len(image_paths)] for i in range(nb_frames)]

    # Build the video
    clip = ImageSequenceClip(paths, fps=fps)
    clip = (
        clips_array([
            [clip, clip.with_effects([Rotate(270)])],
            [clip.with_effects([Rotate(90)]), clip.with_effects([Rotate(180)])],
        ])
        .with_audio(audio)
    )

    # Write file
    clip.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        write_logfile=False,
    )
    return output_path

st.title("Automatic Video Clip Creator")

# 1. Image files
images = st.file_uploader(
    "Upload your image sequence",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 2. Audio file
audio = st.file_uploader(
    "Upload an audio track",
    type=["mp3", "wav", "aac"],
    accept_multiple_files=False
)

# 3. Parameters
fps = st.number_input("Frame rate (fps)", min_value=1.0, value=24.0)
duration = st.number_input("Total duration (s)", min_value=1.0, value=5.0)

# 4. Output filename
output_name = st.text_input("Output video filename", value="out.mp4")

# 5. Process button
if st.button("Create Video"):

    if not images:
        st.error("Please upload at least one image.")
    elif audio is None:
        st.error("Please upload an audio file.")
    else:
        # Save uploads to temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            img_paths = []
            for idx, img in enumerate(images):
                path = os.path.join(tmpdir, f"img_{idx}{os.path.splitext(img.name)[1]}")
                with open(path, "wb") as f:
                    f.write(img.getbuffer())
                img_paths.append(path)

            audio_path = os.path.join(tmpdir, audio.name)
            with open(audio_path, "wb") as f:
                f.write(audio.getbuffer())

            output_path = os.path.join(tmpdir, output_name)

            try:
                st.info("Processing video, please wait...")
                create_clip_from_files(
                    image_paths=img_paths,
                    audio_path=audio_path,
                    fps=fps,
                    duration=duration,
                    output_path=output_path
                )
                st.success("Video created successfully!")
                
                # Offer for download
                with open(output_path, "rb") as vf:
                    st.download_button(
                        "Download your video",
                        data=vf,
                        file_name=output_name,
                        mime="video/mp4"
                    )
            except Exception as e:
                logger.error("Failed to create clip", exc_info=True)
                st.error(f"Error: {e}")
