import subprocess
import time
import threading
import sys

def start_server():
    print("[LAUNCHER] Starting buffer server...")
    try:
        return subprocess.Popen([sys.executable, "buffer_server.py"])
    except Exception as e:
        print(f"[LAUNCHER] Failed to start server: {e}")
        return None

def start_producer(producer_id):
    print(f"[LAUNCHER] Starting producer {producer_id}...")
    try:
        return subprocess.Popen([sys.executable, "producer_client.py", str(producer_id)])
    except Exception as e:
        print(f"[LAUNCHER] Failed to start producer {producer_id}: {e}")
        return None

def start_consumer(consumer_id):
    print(f"[LAUNCHER] Starting consumer {consumer_id}...")
    try:
        return subprocess.Popen([sys.executable, "consumer_client.py", str(consumer_id)])
    except Exception as e:
        print(f"[LAUNCHER] Failed to start consumer {consumer_id}: {e}")
        return None

def main():
    # Start the buffer server
    server_process = start_server()
    if server_process is None:
        print("[LAUNCHER] Cannot proceed without server.")
        return
    time.sleep(2)  # Give server time to start

    # Start producers and consumers
    processes = []

    # Start 2 producers
    for i in range(1, 3):
        proc = start_producer(i)
        if proc:
            processes.append(proc)
        time.sleep(1)

    # Start 2 consumers
    for i in range(1, 3):
        proc = start_consumer(i)
        if proc:
            processes.append(proc)
        time.sleep(1)

    # Wait for all processes
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\n[LAUNCHER] Shutting down...")
        if server_process:
            server_process.terminate()
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    main()
