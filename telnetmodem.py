import socket
import pty
import os
import threading

# Configurations
TELNET_PORT = 2323  # Port for Telnet

# Create a lock to synchronize modem access
modem_lock = threading.Lock()

# Function to handle Telnet client
def handle_client(client_socket, master_fd):
    try:
        client_socket.send(b"Connected to virtual modem interface\n")

        while True:
            # Receive data from Telnet client
            telnet_data = client_socket.recv(1024)
            if not telnet_data:
                break

            # Write data to virtual modem
            with modem_lock:
                os.write(master_fd, telnet_data)

            # Read response from virtual modem
            with modem_lock:
                modem_response = os.read(master_fd, 1024)

            # Send response back to Telnet client
            if modem_response:
                client_socket.send(modem_response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Main server function
def main():
    # Set up virtual modem connection
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)
    print(f"Virtual modem device created: {slave_name}")
    print(f"You can use minicom or another terminal emulator to connect: {slave_name}")

    # Set up Telnet server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", TELNET_PORT))
    server.listen(5)
    print(f"Telnet server listening on port {TELNET_PORT}")

    try:
        while True:
            # Accept incoming Telnet client connection
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")

            # Handle client in a new thread
            client_handler = threading.Thread(
                target=handle_client, args=(client_socket, master_fd)
            )
            client_handler.start()

    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        os.close(master_fd)
        os.close(slave_fd)
        server.close()

if __name__ == "__main__":
    main()
