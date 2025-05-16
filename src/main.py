import os
import tempfile
from logging import getLogger

import streamlit as st
from moviepy.video.fx import Rotate, Crop
from moviepy import Clip, ImageSequenceClip, AudioFileClip, clips_array


logger = getLogger("streamlit_app")


def main():
    st.title("Video Clip Creator")

    # Create a temp dir for this session
    if "tempdir" not in st.session_state:
        st.session_state.tempdir = tempfile.TemporaryDirectory()
        st.session_state.image_paths = []

    tempdir = st.session_state.tempdir.name
    image_paths = st.session_state.image_paths

    st.subheader("Step 1: Capture Photos")

    picture = st.camera_input("Take a photo")
    if picture is not None:
        img_idx = len(image_paths)
        image_path = os.path.join(tempdir, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        image_paths.append(image_path)
        st.success(f"Captured photo #{img_idx + 1}")

    if len(image_paths) > 0:
        st.write(f"{len(image_paths)} photo(s) taken.")
        if st.button("Reset Photos"):
            st.session_state.image_paths = []
            st.experimental_rerun()

    st.subheader("Step 2: Upload Audio")
    audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "aac"])

    st.subheader("Step 3: Set Parameters")
    fps = st.number_input("Frame Rate (fps)", min_value=1.0, value=24.0)
    duration = st.number_input("Video Duration (seconds)", min_value=1.0, value=10.0)

    if len(image_paths) == 0 or audio_file is None:
        st.warning("Please take at least one photo and upload an audio file.")
        return

    if st.button("Create Video"):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as out_file:
            audio_path = os.path.join(tempdir, audio_file.name)
            with open(audio_path, "wb") as f:
                f.write(audio_file.getbuffer())

            try:
                st.info("Processing video, please wait...")
                create_clip(
                    image_paths=image_paths,
                    audio_path=audio_path,
                    fps=fps,
                    duration=duration,
                    output_path=out_file.name
                )
                st.success("Video created successfully!")
                with open(out_file.name, "rb") as f:
                    st.video(f.read())
                    st.download_button("Download Video", f, file_name="output.mp4")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
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
    clip = crop_clip_to_square(clip)
    print("shape after cropping:", clip.get_frame(0).shape[:2])
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

def crop_clip_to_square(clip: Clip) -> Clip:
    """Crop the clip to the largest square possible."""
    width, height = clip.size
    side_len = min(width, height)
    return  (
        Crop(
            x1 = (width - side_len) // 2,
            x2 = width - (width - side_len) // 2,
            y1 = (height - side_len) // 2,
            y2 = height -  (height - side_len) // 2,
        )
        .apply(clip)
    )

if __name__ == "__main__":
    main()