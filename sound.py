import pyaudio


class Pcm2Wave:
    """pcm流包装成wave数据的类"""
    def __init__(self, rate, width, channels):
        """
        :param rate: 采样频率
        :param width: 每个样本所占的字节数
        :param channels: 通道数
        """
        self.rate = rate
        self.width = width
        self.channels = channels

    def pack(self, data):
        """
        将数据包装成wave格式
        :param data: 数据
        :return: wave格式的数据
        """
        headers = [
            b'RIFF',  # ChunkID
            self.uint2bytes(44-8+len(data), 4),  # ChunkSize
            b'WAVE',  # Format
            b'fmt ',  # Subchunk1ID
            self.uint2bytes(16, 4),  # Subchunk1Size
            self.uint2bytes(1, 2),  # AudioFormat
            self.uint2bytes(self.channels, 2),  # NumChannels
            self.uint2bytes(self.rate, 4),  # SampleRate
            self.uint2bytes(self.width*self.rate, 4),  # ByteRate
            self.uint2bytes(self.width, 2),  # BlockAlign
            self.uint2bytes(self.width*8, 2),  # BitsPerSample
            b'data',  # Subchunk2ID
            self.uint2bytes(len(data), 4),  # Subchunk2Size
            data  # Data
        ]

        return b''.join(headers)

    @staticmethod
    def uint2bytes(uint, width):
        """
        把无符号整数转换成小端存储的字节串
        :param uint: 要转换的无符号整数
        :param width: 字节串的字节数
        :return: 字节串
        """
        return uint.to_bytes(width, 'little', signed=False)


class Recorder:
    RATE = 44100
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    CHUNK = 1024

    def __init__(self):
        self.pa = pa = pyaudio.PyAudio()
        self.stream = pa.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                       input=True, frames_per_buffer=self.CHUNK)
        self.packer = Pcm2Wave(self.RATE, pyaudio.get_sample_size(self.FORMAT), self.CHANNELS)

    def start(self, send):
        """
        循环读取音频通过websocket发往前端
        :param send: 发送数据的接口
        """
        self.stream.start_stream()
        while self.stream.is_active():
            data = self.stream.read(self.CHUNK)
            send(data)
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def pack(self, data):
        """
        打包pcm数据成wave数据
        :param data: 源pcm数据
        :return: 打包后的wave数据
        """
        return self.packer.pack(data)


