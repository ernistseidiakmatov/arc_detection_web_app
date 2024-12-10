from asyncio import Lock


class SharedState:
    def __init__(self):
        self.signal_length = 2048
        self.running = False
        self.lock = Lock()

    async def update(self, signal_length=None, running=None):
        async with self.lock:
            if signal_length is not None:
                self.signal_length = signal_length
            if running is not None:
                self.running = running

# state = SharedState()