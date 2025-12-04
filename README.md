# Integrative-Programming-Technologies-MINI-PROJECT

This project demonstrates two implementations of the Producer-Consumer problem in Python:

1. **Thread-based Producer-Consumer Simulation** using threads and semaphores
2. **Socket-based Producer-Consumer System** using client-server architecture

## Prerequisites

- Python 3.x
- No external dependencies required (uses only standard library)

## Application 1: Thread-based Producer-Consumer Simulation

This application simulates the classic producer-consumer problem using Python threads and semaphores. It generates random student data, saves it to XML files, and manages a shared buffer between producer and consumer threads.

### Features

- Producer generates random student data and saves to XML
- Consumer reads and processes student data from XML
- Shared buffer with semaphore-based synchronization
- Configurable buffer size, delays, and student count
- Logging for monitoring operations

### How to Run

1. Navigate to the project root directory
2. Run the simulation:
   ```bash
   python "consumer producer.py"
   ```

The script will run a simulation with one producer and one consumer by default. You can modify the `main()` function or `run_multiple_producers_consumers()` for different configurations.

### Configuration

Key settings can be modified in the `CONFIG` dictionary at the top of the file:
- `BUFFER_SIZE`: Size of the shared buffer (default: 10)
- `MAX_STUDENTS`: Number of students to process (default: 10)
- Delay ranges for producer and consumer operations

## Application 2: Socket-based Producer-Consumer System

This application implements a distributed producer-consumer system using socket programming. It consists of a central buffer server that producers and consumers connect to via TCP sockets.

### Components

- **Buffer Server** (`Socket Programming/buffer_server.py`): Manages the shared buffer and handles client connections
- **Producer Client** (`Socket Programming/producer_client.py`): Connects to server to add items to buffer
- **Consumer Client** (`Socket Programming/consumer_client.py`): Connects to server to remove items from buffer
- **Launcher** (`Socket Programming/launcher.py`): Convenience script to start multiple clients and server

### How to Run

#### Option 1: Manual Startup

1. Start the buffer server:
   ```bash
   cd "Socket Programming"
   python buffer_server.py
   ```

2. In separate terminals, start producers:
   ```bash
   python producer_client.py 1
   python producer_client.py 2
   ```

3. In separate terminals, start consumers:
   ```bash
   python consumer_client.py 1
   python consumer_client.py 2
   ```

#### Option 2: Using Launcher (Recommended)

1. Navigate to the Socket Programming directory:
   ```bash
   cd "Socket Programming"
   ```

2. Run the launcher to start everything automatically:
   ```bash
   python launcher.py
   ```

This will start the server, 2 producers, and 2 consumers.

### Configuration

- Server runs on `localhost:5555` by default
- Buffer size is set to 15 in the server
- Clients will retry operations if buffer is full/empty
- Use Ctrl+C to stop the server or clients

## Output

Both applications provide detailed logging output showing:
- Producer/consumer operations
- Buffer status (size, full/empty state)
- Success/failure of operations
- Final statistics

## Notes

- The thread-based app runs entirely in-memory with XML file I/O
- The socket-based app requires running multiple processes and demonstrates distributed computing concepts
- Both implementations showcase synchronization techniques (semaphores vs. locks)
