import socket
import sys

buf_size = 512

class Server:
    def __init__(self, port):
        # dictionary of client ids and sockets
        self.clients = {}

        # creating server socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # binding socket to provided port
        self.socket.bind(('', int(port)))

        print(self.socket.getsockname())

        # listening for incoming connections
        self.socket.listen(5)

    def process_connections(self):
        while True:
            # block until next client connects
            self.add_client()

            # TODO validate client 

            msg = clientsocket.recv(buf_size)
            if msg == b'': # Zero bytes received
                print("socket connection broken")
                break

            print(msg.decode('utf-8')) 

            msg = input("Enter message: ")
            if msg == "quit":
                print("closing connection")
                break  

            clientsocket.send(msg.encode('utf-8'))

    def add_client(self):
        (clientsocket, _) = self.socket.accept()

        ip = clientsocket.getaddrinfo(host, _)[0]
        print(f"client ip is {ip}")

        #TODO check if client already exists
        self.clients[ip] = clientsocket

    # Cleans up server
    def close(self):
        self.socket.close()

def main(port):
    # create server socket
    server = Server(port)
    
    # handle clients
    server.process_connections()
    
    # close server
    server.close()


    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Need ip and port to host server")