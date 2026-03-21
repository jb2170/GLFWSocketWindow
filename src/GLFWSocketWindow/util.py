class ChunkedNonBlockReader:
    def __init__(self, sock, chunk_size: int):
        self.sock = sock
        self.chunk_size = chunk_size
        self.buffer = b""
        self.chunks = []

    def read(self):
        while len(self.buffer) < self.chunk_size:
            try:
                part = self.sock.recv(self.chunk_size)
            except BlockingIOError:
                raise
            if not part:
                raise EOFError
            self.buffer += part

        ret = self.buffer[:self.chunk_size]
        self.buffer = self.buffer[self.chunk_size:]

        return ret
