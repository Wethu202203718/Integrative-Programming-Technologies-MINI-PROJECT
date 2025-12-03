import socket
import threading
import queue
import time
import json

class SharedBufferServer:
    def __init__(self, host='localhost', port=5555, buffer_size=15):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.buffer = queue.Queue(maxsize=buffer_size)
        self.lock = threading.Lock()
        self.producer_count = 0
        self.consumer_count = 0

    def start(self):
        """Start the buffer server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"[SERVER] Buffer Server started on {self.host}:{self.port}")
        print(f"[SERVER] Buffer size: {self.buffer_size}")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, addr)
            )
            client_thread.start()

    def handle_client(self, client_socket, addr):
        """Handle client connections (producers or consumers)"""
        try:
            # Receive client type
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                return

            request = json.loads(data)
            client_type = request.get('type')

            if client_type == 'producer':
                self.handle_producer(client_socket, addr, request)
            elif client_type == 'consumer':
                self.handle_consumer(client_socket, addr, request)
            else:
                response = {'status': 'error', 'message': 'Invalid client type'}
                client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"[SERVER] Error handling client {addr}: {e}")
        finally:
            client_socket.close()

    def handle_producer(self, client_socket, addr, request):
        """Handle producer requests to add items to buffer"""
        producer_id = request.get('id', 'unknown')
        item = request.get('item')

        print(f"[SERVER] Producer {producer_id}@{addr} wants to produce: {item}")

        with self.lock:
            if self.buffer.full():
                response = {
                    'status': 'error',
                    'message': 'Buffer is full. Try again later.'
                }
                print(f"[SERVER] Buffer FULL - Producer {producer_id} must wait")
            else:
                self.buffer.put(item)
                response = {
                    'status': 'success',
                    'message': f'Item "{item}" added to buffer',
                    'buffer_size': self.buffer.qsize()
                }
                print(f"[SERVER] Produced: {item} | Buffer size: {self.buffer.qsize()}/{self.buffer_size}")

        client_socket.send(json.dumps(response).encode('utf-8'))

    def handle_consumer(self, client_socket, addr, request):
        """Handle consumer requests to remove items from buffer"""
        consumer_id = request.get('id', 'unknown')

        print(f"[SERVER] Consumer {consumer_id}@{addr} wants to consume")

        with self.lock:
            if self.buffer.empty():
                response = {
                    'status': 'error',
                    'message': 'Buffer is empty. No items to consume.'
                }
                print(f"[SERVER] Buffer EMPTY - Consumer {consumer_id} must wait")
            else:
                item = self.buffer.get()
                response = {
                    'status': 'success',
                    'item': item,
                    'message': f'Item "{item}" consumed',
                    'buffer_size': self.buffer.qsize()
                }
                print(f"[SERVER] Consumed: {item} | Buffer size: {self.buffer.qsize()}/{self.buffer_size}")

        client_socket.send(json.dumps(response).encode('utf-8'))

    def get_buffer_status(self):
        """Get current buffer status"""
        with self.lock:
            return {
                'size': self.buffer.qsize(),
                'max_size': self.buffer_size,
                'is_full': self.buffer.full(),
                'is_empty': self.buffer.empty()
            }

if __name__ == "__main__":
    server = SharedBufferServer()
    server.start()
