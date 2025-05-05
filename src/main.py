import sys
import os
import argparse
from logging import getLogger

from moviepy import ImageSequenceClip, AudioFileClip, clips_array
from moviepy.video.fx import Rotate

logger = getLogger("main")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create a video from a sequence of images at a given frame rate, "
            "looping to match a specified duration, and overlay it with an audio track."
        )
    )
    parser.add_argument(
        '--images_folder',
        required=True,
        help=("Folder of the images that will be used for the clip.")
    )
    parser.add_argument(
        '--fps',
        required=True,
        type=float,
        help="Frame rate (frames per second) for the output video"
    )
    parser.add_argument(
        '--audio',
        required=True,
        help="Path to the audio file to include (e.g. soundtrack.mp3)"
    )
    parser.add_argument(
        '--duration',
        required=True,
        type=float,
        help="Total duration (in seconds) for the output video"
    )
    parser.add_argument(
        '--output',
        required=True,
        type=str,
        help="Destination video file path (e.g. out.mp4)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.images_folder):
        logger.error("images_folder path does not lead to a FOLDER!")
        sys.exit(1)

    return args


def main():
    args = parse_args()

    try:
        audio = AudioFileClip(args.audio).with_duration(args.duration)
    except Exception as e:
        logger.error(f"Could not load audio file '{args.audio}': {e}", exc_info=True)
        sys.exit(1)

    image_files = os.listdir(args.images_folder)
    image_files = list(filter(lambda filename: os.path.splitext(filename)[1] == ".jpg", image_files))
    nb_frames = int(args.fps * args.duration)
    image_file_idx_it = map(lambda i: i % len(image_files), range(nb_frames))
    image_files = [os.path.join(args.images_folder, image_files[i]) for i in image_file_idx_it]

    # Build video clip from image sequence
    clip:ImageSequenceClip = ImageSequenceClip(image_files, fps=args.fps, durations=args.duration)
    clip = (
        clips_array([
            [clip.with_effects([]), clip.with_effects([Rotate(270)])],
            [clip.with_effects([Rotate(90)]), clip.with_effects([Rotate(180)])],
        ])
        .with_audio(audio)
    )

    
    # Write the final video file
    try:
        clip.write_videofile(
            args.output,
            fps=args.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            write_logfile=True,
        )
    except Exception as e:
        logger = getLogger("write_videofile")
        logger.error(f"Error writing video file '{args.output}': {e}", stack_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
