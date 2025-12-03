import socket
import json
import time
import random
import threading
import sys

class Producer:
    def __init__(self, producer_id, server_host='localhost', server_port=5555):
        self.producer_id = producer_id
        self.server_host = server_host
        self.server_port = server_port

    def produce(self, item):
        """Send item to buffer server"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))

            # Send producer request
            request = {
                'type': 'producer',
                'id': self.producer_id,
                'item': item
            }

            client_socket.send(json.dumps(request).encode('utf-8'))

            # Receive response
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            client_socket.close()

            if response_data['status'] == 'success':
                print(f"[PRODUCER {self.producer_id}] Successfully produced: {item}")
                return True
            else:
                print(f"[PRODUCER {self.producer_id}] Failed to produce: {response_data['message']}")
                return False

        except Exception as e:
            print(f"[PRODUCER {self.producer_id}] Error: {e}")
            return False

    def continuous_production(self, items=None, interval=1, max_retries=5):
        """Continuously produce items"""
        if items is None:
            items = [f"Item-{i}" for i in range(1, 101)]

        for item in items:
            retries = 0
            success = False
            while not success and retries < max_retries:
                success = self.produce(item)
                if not success:
                    retries += 1
                    if retries < max_retries:
                        print(f"[PRODUCER {self.producer_id}] Retrying... ({retries}/{max_retries})")
                        time.sleep(random.uniform(1, 3))  # Wait before retry
                    else:
                        print(f"[PRODUCER {self.producer_id}] Max retries reached for item {item}, skipping.")
            if success:
                time.sleep(interval)  # Wait before next production

def run_producer(producer_id, num_items=10):
    """Run a producer instance"""
    producer = Producer(producer_id)

    # Generate some items to produce
    items = [f"P{producer_id}-Item-{i}" for i in range(1, num_items + 1)]

    print(f"[PRODUCER {producer_id}] Starting to produce {num_items} items")
    producer.continuous_production(items, interval=random.uniform(0.5, 2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        producer_id = sys.argv[1]
    else:
        producer_id = "1"

    run_producer(producer_id, num_items=15)
