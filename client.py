import socket
import sys
import threading
from datetime import datetime
def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")
def receive_messages(socket):

    while True:
        try:
            #chars are received in bytes, so we decode them to string before printing
            msg = socket.recv(1024)
            if not msg:
                print("\n..................Server has closed connection..............")
                break
            print(f"\r{msg.decode()}")
            print(f"[{get_timestamp()}] You: ", end="", flush=True)
        except:
            break
    sys.exit()

def client():
    # If u run the client without a port number, it will say what to run, otherwise it will create 
    # connection at port
    if len(sys.argv) != 2:
        print("Are you running: python client.py <port>")
        return
    #Making sure the port number is valid
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Port must be a valid integer.")
        return

    # 2. Connect to Server and display the welcome message
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', port))
        
        # Recieve further messages
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # Main loop for sending messages to the server as well ending the connection when 'exit' is typed
        print("--- Connected to Server ---")
        print("Type your message and press Enter. Type 'exit' to quit.")

        while True:
            msg = input(f"[{get_timestamp()}] Client (Current Terminal): ")
            if msg.lower() == 'exit':
                break
            if msg.strip(): # Check if the message is not empty or just whitespace
                client_socket.send(msg.encode())
    #Error handling for error that are inbuilt as well as the most common error of connection refused when the server is not running or the port is incorrect
    except ConnectionRefusedError:
        print("Error: Could not connect to server.Incorrect Port/Server Down")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        print("Closing connection...")
        client_socket.close()

if __name__ == "__main__":
    client()