from moviepy.video.fx import Rotate, Crop
from moviepy import Clip, ImageSequenceClip, AudioFileClip, clips_array


def create_clip(
    image_paths: list[str],
    audio_path: str,
    bpm: float,
    duration: float,
    output_path: str
):
    # Load audio
    audio = AudioFileClip(audio_path).with_duration(duration)
    fps = bpm / 60
    # Loop or trim image sequence to match duration
    nb_frames = max(int(fps * duration), 1)
    paths = [image_paths[i % len(image_paths)] for i in range(nb_frames)]
    # Build the video
    clip = ImageSequenceClip(paths, fps=fps)
    clip = crop_clip_to_square(clip)
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

