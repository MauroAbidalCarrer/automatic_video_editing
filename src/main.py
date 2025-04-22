from logging import getLogger
import argparse
import sys

from moviepy import ImageSequenceClip, AudioFileClip

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Create a video from a sequence of images at a given frame rate "
            "and overlay it with an audio track."
        )
    )
    # images will consume all but the last three positional arguments
    parser.add_argument(
        'images',
        nargs='+',
        help=(
            "List of image files (e.g. img1.png img2.jpg ...). "
            "These will be shown in the order given."
        )
    )
    parser.add_argument(
        'audio',
        help="Path to the audio file to include (e.g. soundtrack.mp3)"
    )
    parser.add_argument(
        'fps',
        type=float,
        help="Frame rate (frames per second) for the output video"
    )
    parser.add_argument(
        'output',
        help="Destination video file path (e.g. out.mp4)"
    )
    args = parser.parse_args()
    # Make sure there are at least one image
    if len(args.images) < 1:
        print("Error: you must supply at least one image file.", file=sys.stderr)
        sys.exit(1)

    return args

def main():
    args = parse_args()

    try:
        audio = AudioFileClip(args.audio).with_duration(4)
    except Exception as e:
        print(f"Error loading audio file '{args.audio}': {e}", file=sys.stderr)
        sys.exit(1)

    # Build video clip from image sequence
    clip:ImageSequenceClip = ImageSequenceClip(args.images, fps=args.fps, durations=len(args.images))
    clip = clip.with_audio(audio)
    # Write the final video file
    try:
        clip.write_videofile(
            args.output,
            fps=args.fps,
            codec='libx264',      # H.264 video codec
            audio_codec='aac',     # AAC audio codec
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
