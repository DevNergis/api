import base64
import zlib


class Cipher:
    def __init__(self, data: str):
        self.data = data

    def encryption(self):
        return zlib.compress(base64.b85encode(
            base64.a85encode(base64.b16encode(
                base64.b32encode(base64.b64encode(
                    self.data.encode()))))), 9).hex()
