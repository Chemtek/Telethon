from io import BytesIO, BufferedWriter
from struct import pack


class BinaryWriter:
    """
    Small utility class to write binary data.
    Also creates a "Memory Stream" if necessary
    """

    def __init__(self, stream=None):
        if not stream:
            stream = BytesIO()

        self.stream = stream
        self.writer = BufferedWriter(self.stream)

    # region Writing

    def write_byte(self, value):
        self.writer.write(pack('B', value))

    def write_int(self, value, signed=True):
        if signed:
            self.writer.write(pack('i', value))
        else:
            value &= 0xFFFFFFFF  # Ensure it's unsigned (see http://stackoverflow.com/a/30092291/4759433)
            self.writer.write(pack('I', value))

    def write_long(self, value, signed=True):
        if signed:
            self.writer.write(pack('q', value))
        else:
            value &= 0xFFFFFFFFFFFFFFFF
            self.writer.write(pack('Q', value))

    def write_float(self, value):
        self.writer.write(pack('f', value))

    def write_double(self, value):
        self.writer.write(pack('d', value))

    def write_large_int(self, value, bits):
        self.writer.write(pack('{}B'.format(bits // 8), value))

    def write(self, data):
        self.writer.write(data)

    # endregion

    # region Telegram custom writing

    def tgwrite_bytes(self, data):

        if len(data) < 254:
            padding = (len(data) + 1) % 4
            if padding != 0:
                padding = 4 - padding

            self.write(bytes([len(data)]))
            self.write(data)

        else:
            padding = len(data) % 4
            if padding != 0:
                padding = 4 - padding

            # TODO ensure that _this_ is right (it appears to be)
            self.write(bytes([254]))
            self.write(bytes([len(data) % 256]))
            self.write(bytes([(len(data) >> 8) % 256]))
            self.write(bytes([(len(data) >> 16) % 256]))
            self.write(data)

            """ Original:
                    binaryWriter.Write((byte)254);
                    binaryWriter.Write((byte)(bytes.Length));
                    binaryWriter.Write((byte)(bytes.Length >> 8));
                    binaryWriter.Write((byte)(bytes.Length >> 16));
            """

        self.write(bytes(padding))

    def tgwrite_string(self, string):
        return self.tgwrite_bytes(string.encode('utf-8'))

    def tgwrite_bool(self, bool):
        #                     boolTrue                boolFalse
        return self.write_int(0x997275b5 if bool else 0xbc799737, signed=False)

    # endregion

    def flush(self):
        self.writer.flush()

    def close(self):
        self.writer.close()
        # TODO Do I need to close the underlying stream?

    def get_bytes(self, flush=True):
        if flush:
            self.writer.flush()
        self.stream.getbuffer()

    # with block
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
