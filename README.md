# wir2wav

wir2wav is a simple tool for the conversion of .wir impulse response files into standard PCM .wav files.

## Usage

Simply run `wir2wav.py` with Python 3 (no additional packages required).

The script will recursively search for .wir files in the current working directory and convert them to .wav files, storing the .wav files next to the original .wir file.

### Exported Channels

.wir files may contain more than a (true) stereo stream. If an additional mono channel is present, it will be dropped in the exported .wav file.

