import os
import time
import pydub
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Sound converter",
        description="Converts sound files from input directory to output directory (44.1 kHz 128 kbit/s WAV)",
    )
    parser.add_argument(
        "--input-dir", type=str, default="~/data/wheel-of-fortune/input_sounds/"
    )
    parser.add_argument(
        "--output-dir", type=str, default="~/data/wheel-of-fortune/sounds/"
    )
    parser.add_argument("--max-duration-secs", type=float, default=90.0)
    parser.add_argument("--format", type=str, default="wav")
    args = parser.parse_args()

    input_dir = os.path.expanduser(args.input_dir)
    output_dir = os.path.expanduser(args.output_dir)
    print("Input dir:", input_dir)
    print("Output dir:", output_dir)

    for fname in os.listdir(input_dir):
        input_file = os.path.join(input_dir, fname)
        output_file = os.path.join(
            output_dir, "%s.%s" % (os.path.splitext(fname)[0], args.format)
        )
        print("Input: %s" % (input_file))
        print("Output: %s" % (output_file))

        if os.path.isfile(output_file):
            print("Output file already exists, skip")
            continue

        print("Load...")
        start = time.time()
        audio = pydub.AudioSegment.from_file(input_file)
        print("Load done in %.1f s" % (time.time() - start))

        print("Convert...")
        start = time.time()
        with open(output_file, "wb") as fout:
            audio = audio.set_frame_rate(44100)
            audio[: int(1000 * args.max_duration_secs)].export(
                fout, format=args.format, bitrate="128k"
            )
        print(
            "Conversion done in %.1f s (%.3f MB)"
            % (time.time() - start, os.path.getsize(output_file) / 1024.0**2)
        )
