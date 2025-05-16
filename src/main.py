# app.py
import os
import tempfile
from logging import getLogger

import streamlit as st
from moviepy.video.fx import Rotate
from moviepy import ImageSequenceClip, AudioFileClip, clips_array


logger = getLogger("streamlit_app")


def create_clip(
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

def main():
    st.title("Video Clip Creator")

    # User input fields
    fps = st.number_input("Frame Rate (fps)", min_value=1.0, value=24.0)
    duration = st.number_input("Video Duration (seconds)", min_value=1.0, value=10.0)

    audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "aac"])
    picture = st.camera_input("Take a picture")

    if picture is None:
        st.warning("Please take a picture with your camera.")
        return
    if audio_file is None:
        st.warning("Please upload an audio file.")
        return

    # Button to trigger video creation
    if st.button("Create Video"):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save captured image
            image_path = os.path.join(tmpdir, picture.name)
            with open(image_path, "wb") as f:
                f.write(picture.getbuffer())

            # Save uploaded audio
            audio_path = os.path.join(tmpdir, audio_file.name)
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())

            output_path = os.path.join(tmpdir, "output.mp4")

            try:
                create_clip(
                    images_dir=os.path.dirname(image_path),
                    duration=duration,
                    fps=fps,
                    audio_path=audio_path,
                    output_path=output_path,
                )
                with open(output_path, "rb") as f:
                    st.success("Video created successfully!")
                    st.video(f.read())
                    st.download_button("Download Video", f, file_name="output.mp4")
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()