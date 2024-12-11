from asyncio import Lock


class SharedState:
    def __init__(self):
        self.signal_length = 2048
        self.save_arc_data = 0
        self.save_dir = "/home/netvision/Desktop/arc_data"
        self.detection_period = 0.5
        self.running = False
        self.lock = Lock()

    async def update(self, signal_length=None, save_arc_data=None, save_dir=None, detection_period=None, running=None):
        async with self.lock:
            if signal_length is not None:
                self.signal_length = signal_length
            if save_arc_data is not None:
                self.save_arc_data = save_arc_data
            if save_dir is not None:
                self.save_dir = save_dir
            if detection_period is not None:
                self.detection_period = detection_period
            if running is not None:
                self.running = running


# state = SharedState()