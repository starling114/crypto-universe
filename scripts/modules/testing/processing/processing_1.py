import multiprocessing as mp
import time
import sys

class Processor:
    def __init__(self):
        self.stop_event = mp.Event()

    def run(self):
        while True:
            # Your processing code goes here
            print(f"Processing in process: {mp.current_process().name}")
            time.sleep(1)  # Simulate some work; replace with actual processing

            if self.stop_event.is_set():
                print(f"Stopping process: {mp.current_process().name}")
                # Add any cleanup code here if needed
                break

    def stop(self):
        self.stop_event.set()

def main():
    num_instances = 3  # Adjust the number of instances as needed
    instances = [Processor() for _ in range(num_instances)]
    processes = []

    for inst in instances:
        p = mp.Process(target=inst.run)
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Ctrl+C pressed, stopping all instances...")
        for inst in instances:
            inst.stop()
        for p in processes:
            p.join()
        sys.exit(0)

if __name__ == '__main__':
    main()
