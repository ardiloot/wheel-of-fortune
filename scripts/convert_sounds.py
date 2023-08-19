import os
import io
import time
import pydub

if __name__ == "__main__":
    input_dir = "data/input_sounds/"
    output_dir = "data/sounds/"

    for fname in os.listdir(input_dir):
        input_file = os.path.join(input_dir, fname)
        output_file = os.path.join(output_dir, "%s.mp3" % (os.path.splitext(fname)[0]))
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
            audio.export(fout)
        print("Conversion done in %.1f s (%.3f MB)" % (time.time() - start, os.path.getsize(output_file) / 1024.0 ** 2))
