import threading
import signal
import time
import sys

class Worker:
    def __init__(self, name):
        self.name = name
        self._running = True

    def run(self):
        while self._running:
            print(f"[{self.name}] Working...")
            time.sleep(1)
        print(f"[{self.name}] Stopped cleanly.")

    def stop(self):
        self._running = False


def main():
    workers = [Worker(f"Worker-{i}") for i in range(3)]
    threads = []

    # Create threads
    for w in workers:
        t = threading.Thread(target=w.run, daemon=True)
        threads.append(t)
        t.start()

    def handle_sigint(sig, frame):
        print("\nCtrl+C detected. Stopping all workers...")
        for w in workers:
            w.stop()
        # Wait for all threads to exit
        for t in threads:
            t.join()
        print("All workers stopped.")
        sys.exit(0)

    # Register signal handler
    signal.signal(signal.SIGINT, handle_sigint)

    # Keep main thread alive
    while True:
        time.sleep(0.5)


if __name__ == "__main__":
    main()
