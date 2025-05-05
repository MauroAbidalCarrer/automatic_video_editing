from logging import getLogger
import argparse
import sys

from moviepy import ImageSequenceClip, AudioFileClip, clips_array
from moviepy.video.fx import Rotate

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create a video from a sequence of images at a given frame rate, "
            "looping to match a specified duration, and overlay it with an audio track."
        )
    )
    parser.add_argument(
        'images',
        nargs='+',
        help=(
            "List of image files (e.g. img1.png img2.jpg ...). "
            "These will be shown in the order given."
        )
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

    if len(args.images) < 1:
        print("Error: you must supply at least one image file.", file=sys.stderr)
        sys.exit(1)

    return args


def main():
    args = parse_args()

    try:
        audio = AudioFileClip(args.audio).with_duration(len(args.images) / args.fps)
    except Exception as e:
        logger = getLogger("main")
        logger.error(f"Could not load audio file '{args.audio}': {e}", exc_info=True)
        sys.exit(1)

    # Build video clip from image sequence
    clip:ImageSequenceClip = (
        ImageSequenceClip(args.images, fps=args.fps, durations=len(args.images))
    )

    clip = clips_array([
        [clip.with_effects([]), clip.with_effects([Rotate(90)])],
        [clip.with_effects([Rotate(270)]), clip.with_effects([Rotate(180)])],
    ])

    
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
