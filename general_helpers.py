import audioread
import wave
import contextlib
import sys


def convert_webm_to_wav(input_file, output_file):
    with audioread.audio_open(input_file) as f:
        print('Input file: %i channels at %i Hz; %.1f seconds.' %
                (f.channels, f.samplerate, f.duration),
                file=sys.stderr)
        print('Backend:', str(type(f).__module__).split('.')[1],
                file=sys.stderr)

        with contextlib.closing(wave.open(output_file, 'w')) as of:
            of.setnchannels(f.channels)
            of.setframerate(f.samplerate)
            of.setsampwidth(2)

            for buf in f:
                of.writeframes(buf)