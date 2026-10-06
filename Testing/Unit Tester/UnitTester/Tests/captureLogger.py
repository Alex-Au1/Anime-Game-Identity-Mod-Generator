from FixRaidenBoss2 import BaseLogger


class CaptureLogger(BaseLogger):
    """An AG Remap logger that keeps what it writes, as a server would forward it"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = []

    def write(self, message: str):
        self.lines.append(message)

    def read(self, desc: str) -> str:
        return ""
