import socket
import json
import time
import random
import threading
import sys

class Consumer:
    def __init__(self, consumer_id, server_host='localhost', server_port=5555):
        self.consumer_id = consumer_id
        self.server_host = server_host
        self.server_port = server_port

    def consume(self):
        """Consume item from buffer server"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))

            # Send consumer request
            request = {
                'type': 'consumer',
                'id': self.consumer_id
            }

            client_socket.send(json.dumps(request).encode('utf-8'))

            # Receive response
            response = client_socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            client_socket.close()

            if response_data['status'] == 'success':
                item = response_data['item']
                print(f"[CONSUMER {self.consumer_id}] Successfully consumed: {item}")
                return item
            else:
                print(f"[CONSUMER {self.consumer_id}] Failed to consume: {response_data['message']}")
                return None

        except Exception as e:
            print(f"[CONSUMER {self.consumer_id}] Error: {e}")
            return None

    def continuous_consumption(self, max_items=10, interval=1, max_retries=5):
        """Continuously consume items"""
        items_consumed = 0

        while items_consumed < max_items:
            retries = 0
            item = None
            while item is None and retries < max_retries:
                item = self.consume()
                if item is None:
                    retries += 1
                    if retries < max_retries:
                        print(f"[CONSUMER {self.consumer_id}] Retrying... ({retries}/{max_retries})")
                        time.sleep(random.uniform(1, 3))  # Wait before retry
                    else:
                        print(f"[CONSUMER {self.consumer_id}] Max retries reached, stopping consumption.")
                        return
            if item is not None:
                items_consumed += 1
                print(f"[CONSUMER {self.consumer_id}] Total consumed: {items_consumed}")
                time.sleep(interval)  # Process the item
            else:
                print(f"[CONSUMER {self.consumer_id}] Buffer empty, waiting...")
                time.sleep(random.uniform(1, 3))  # Wait before retry

def run_consumer(consumer_id, max_items=10):
    """Run a consumer instance"""
    consumer = Consumer(consumer_id)

    print(f"[CONSUMER {consumer_id}] Starting to consume up to {max_items} items")
    consumer.continuous_consumption(max_items, interval=random.uniform(0.5, 2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        consumer_id = sys.argv[1]
    else:
        consumer_id = "1"

    run_consumer(consumer_id, max_items=15)
