import time

class Timer:
    def __init__(self):
        self.start_time = None  
        self.is_running = False  

    def start(self):
        self.start_time = time.time()
        self.is_running = True

    def restart(self):
        self.start()

    def elapsed_time(self):
        if not self.is_running:
            return 0
        return int(time.time() - self.start_time)

    def has_elapsed(self, seconds):
        return self.elapsed_time() >= seconds

    def stop(self):
        self.is_running = False
