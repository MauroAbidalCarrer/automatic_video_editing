import os
import tempfile

import streamlit as st

from video_editing import create_clip


def main():
    st.title("Video Clip Creator")

    # Create a temp dir for this session
    if "tempdir" not in st.session_state:
        st.session_state.tempdir = tempfile.TemporaryDirectory()
        st.session_state.image_paths = []
        st.session_state.prev_picture = None

    tempdir = st.session_state.tempdir.name
    image_paths = st.session_state.image_paths

    st.subheader("Step 1: Capture Photos")

    if len(image_paths) > 0:
        st.write(f"{len(image_paths)} photo(s) taken.")
        if st.button("Reset Photos"):
            st.session_state.image_paths = []

    picture = st.camera_input("Take a photo")
    if picture is not None and st.session_state.prev_picture != picture:
        st.session_state.prev_picture = picture
        img_idx = len(image_paths)
        image_path = os.path.join(tempdir, f"photo_{img_idx}.jpg")
        with open(image_path, "wb") as f:
            f.write(picture.getbuffer())
        image_paths.append(image_path)
        st.success(f"Captured photo #{img_idx + 1}")


    st.subheader("Step 2: Upload Audio")
    audio_file = st.file_uploader(label="Upload Audio File")
    
    st.subheader("Step 3: Set Parameters")
    bpm = st.number_input("Beat per Minute", min_value=1.0, value=24.0)
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
                    bpm=bpm,
                    duration=duration,
                    output_path=out_file.name
                )
                st.success("Video created successfully!")
                with open(out_file.name, "rb") as f:
                    st.video(f.read())
                    st.download_button("Download Video", f, file_name="output.mp4")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
if __name__ == "__main__":
    main()