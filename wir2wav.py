import struct
import wave
import io
from enum import Enum
from fnmatch import fnmatch
import os


class Channels(Enum):
    MONO = 4
    STEREO = 8
    TRUE_STEREO = 16


class WIR:
    def __init__(self, path):
        """
        :param path: the path to the .wir file
        """
        with open(path, "rb") as f:
            self.path = path
            self.header = f.read(40)
            """
            Header format
            (based on http://freeverb3vst.osdn.jp/tips/tips.shtml)
            
            // 32bit LE
            typedef struct{
              0: char magic[4]; // "wvIR"
              4: int fileSizeLE; // filesize-8
              8: char version[8]; // version "ver1fmt "
              16: int headerSizeLE;
              20: short int i3; // 0x3
              22: short int channels;
              24: int fs; // sample/frame rate 
              28: int fs2;
              32: short int i4; // MONO 0x4 STEREO 0x8 4CH 0x10
              34: short int i5; // 0x17
              36: char data[4]; // "data"
            } WirHeader;
            40: // rest of the data is FLOAT_LE (32bit float)
            """
            self.data = f.read()
            self.numChannels = struct.unpack("H", self.header[22:24])[0]
            self.framerate = struct.unpack("I", self.header[24:28])[0]
            self.fs2 = struct.unpack("I", self.header[28:32])[0]
            self.channelsMask = struct.unpack("H", self.header[32:34])[0]

    def durationSecs(self):
        return len(self.data) / 4 / self.numChannels / self.framerate

    def __str__(self):
        chanStrings = []
        for chan in list(Channels):
            if self.channelsMask & chan.value:
                chanStrings.append(str(chan))
        return f"WIR[{self.path}, {self.numChannels} channels [{' + '.join(chanStrings)}], {self.framerate} Hz, {self.durationSecs():.3f} secs]"

    def dataWithChannelRemoved(self, channelIdx):
        buf = io.BytesIO()
        framesize = self.numChannels * 4
        offs = 0
        while offs < len(self.data):
            frame = self.data[offs:offs+framesize]
            if channelIdx > 0:
                buf.write(frame[:channelIdx*4])
            buf.write(frame[channelIdx*4+4:])
            offs += framesize
        return buf.getvalue()

    def writeWav(self, path, removeMonoChannel=True):
        """
        :param path: the path of the wave file to write to
        :param removeMonoChannel: whether to remove an additional mono channel (if further channels are available), e.g.
            to remove the mono channel for the case where an additional stereo channel is available
        """
        wav = wave.open(path, mode="wb")
        hasAdditionalMonoChannel = self.channelsMask & Channels.MONO.value > 0 and self.channelsMask != Channels.MONO.value
        if hasAdditionalMonoChannel and removeMonoChannel:
            data = self.dataWithChannelRemoved(0)
            numChannels = self.numChannels-1
        else:
            data = self.data
            numChannels = self.numChannels
        print(f"Writing wave file {path} with {numChannels} for {wir} ...")
        wav.setsampwidth(4)
        wav.setnchannels(numChannels)
        wav.setframerate(self.framerate)
        wav.writeframes(data)
        wav.close()


if __name__ == '__main__':
    for fn in os.listdir("."):
        if fnmatch(fn, "*.wir"):
            wir = WIR(fn)
            wavfn = os.path.splitext(fn)[0] + ".wav"
            wir.writeWav(wavfn)
