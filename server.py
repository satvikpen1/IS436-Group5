import random
import socket
import sys
import threading
from datetime import datetime

COLORS = [
    "\033[91m", "\033[92m", "\033[93m", "\033[94m", 
    "\033[95m", "\033[96m", "\033[31m", "\033[32m", 
    "\033[33m", "\033[34m", "\033[35m", "\033[36m"
]
RESET = "\033[0m"

#For handling multiple clients list needed
clients = []

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def sendall(msg, sender_connection=None):
   for client in clients:
        if client != sender_connection:
            try:
                client.send(msg.encode())
            except:
                # If sending fails, the client likely connection is broken, so we remove it from the list
                rem_client(client)   
   
def rem_client(connection):
    if connection in clients:
        clients.remove(connection)
        connection.close()

def single_client(connection, addr, color):
    #Add unique identfier based on chat port 
    chat_id = f"User-{addr[1]}"
    while True:
        try:
            #chars are received in bytes, so we decode them to string before printing
            msg = connection.recv(1024)
            if not msg:
                break
            
            decoded_msg = msg.decode()
            ts = get_timestamp()
            
            # Format:[Time] [Color][ID][Reset]: msg
            formatted_msg = f"[{ts}] {color}[{chat_id}]{RESET}: {decoded_msg}"
            
            print(f"\n{formatted_msg}")
            print("Server broadcast: ", end="", flush=True)
            
            sendall(formatted_msg, connection)
            
        except:
            break
    print(f"\n[{get_timestamp()}] [System] {chat_id} disconnected.")
    rem_client(connection)
def server():
       # If u run the client without a port number, it will say what to run, otherwise it will create 
    # connection at port
    if len(sys.argv) != 2:
        print("Are you running: python server.py <port>")
        return

    try:
        port = int(sys.argv[1])
        if not (1025 <= port <= 65535):
            raise ValueError
    except ValueError:
        print("Port must be between 1025 and 65535.")
        return

    # Connection on specified port and listen for clients, then send welcome message to client and start thread to listen for client messages while also allowing server to send messages back to client until 'exit' is typed by either party
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', port))
        server_socket.listen(5)
        print(f"Server listening on port {port}...")
# Thread for broadcasting messages from the server admin to all clients, also allows the admin to shut down the server by typing 'exit'
        def server_admin_chat():
            while True:
                msg = input("Server broadcast: ")
                #Exit msg here
                if msg.lower() == 'exit':
                    print("Shutting down server...")
                    sendall("Server is shutting down.")
                    # Force exit the process
                    sys.exit()
                admin_msg = f"[{get_timestamp()}] \033[1m[SERVER]\033[0m: {msg}"
                sendall(admin_msg)

        threading.Thread(target=server_admin_chat, daemon=True).start()

        while True:
            connection, addr = server_socket.accept()
            clients.append(connection)
            client_color = random.choice(COLORS)
            print(f"\n[System] New connection from {addr[1]} with color {client_color}")

            # Send welcome message
            connection.send("\n--- Welcome to the Server! ---\nType 'exit' to leave.".encode())

            # Start a dedicated thread for this client
            client_thread = threading.Thread(target=single_client, args=(connection, addr,client_color), daemon=True)
            client_thread.start()

    except Exception as e:
        print(f"Error from Server: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()