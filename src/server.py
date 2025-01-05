from socket import socket, AF_INET, SOCK_STREAM
import sys
import struct
import threading
import time

from zPacket import ZPacket

class Connection:
    NOT_RECVEIVED = 1
    ACCEPTED = 2
    DENIED = 3

    def __init__(self, socket: socket):
        self.socket = socket
        self.status = Connection.NOT_RECVEIVED
        self.lock = threading.Lock()
    
    def update_status(self, status: int):
        self.lock.acquire()
        self.status = status
        self.lock.release()

class Server:
    def __init__(self, port: str):
        # dictionary of client ips and sockets
        self.clients: dict[str, socket] = {}

        # diction ary of requested ips and sockets making the request
        self.client_requests: dict[str, Connection] = {}

        # creating server socket
        self.socket = socket(AF_INET, SOCK_STREAM)

        # binding socket to provided port
        self.socket.bind(('', int(port)))

        # listening for incoming connections
        self.socket.listen(5)

        self.clients_lock = threading.Lock()

    def process_connections(self):
        while True:
            # block until next client connects
            (clientsocket, address) = self.socket.accept()

            # TODO validate client 

            self.clients_lock.acquire()
            self.clients[address[0]] = clientsocket
            self.clients_lock.release()

            print(address[0])

            client_handler = threading.Thread(target=self.handle_client, args=(clientsocket,))
            client_handler.start()
            #client_handler.join()
    
    def handle_client(self, clientsocket: socket):
        if clientsocket == None:
            print("handle_client: requires client_socket")
            return
        
        # Sending serv_connected, and client_req if this client has been requested
        flags = ZPacket.SERV_CONN
        data = ""
        self.clients_lock.acquire()
        if clientsocket.getsockname()[0] in self.client_requests.keys(): 
            flags = flags | ZPacket.CLIENT_REQ
            data = self.client_requests[clientsocket.getsockname()[0]].socket.getsockname()[0]
        self.clients_lock.release()

        # sending status to client
        self.send(clientsocket, data, flags)

        recv_packet = self.recv(clientsocket)
        if recv_packet is None:
            print(f"Disconnected from client {clientsocket.getsockname()[0]}")
            return
        
        if recv_packet.flags == ZPacket.CLIENT_ACCEPT:
            self.clients_lock.acquire()
            connection = self.client_requests[clientsocket.getsockname()[0]]
            self.clients_lock.release()
            connection.update_status(Connection.ACCEPTED)
            self.send(connection.socket, flags=ZPacket.CLIENT_CONN)
            self.send_recv_loop(clientsocket, connection.socket)
        elif recv_packet.flags == ZPacket.CLIENT_DENY:
            self.clients_lock.acquire()
            self.client_requests[clientsocket.getsockname()[0]].update_status(Connection.DENIED)
            self.clients_lock.release()
            # TODO how can client req another client? 
        elif recv_packet.flags == ZPacket.CLIENT_REQ:
            print(f"client req ip: {recv_packet.data}")
            connection = Connection(clientsocket)
            self.clients_lock.acquire()
            self.client_requests[recv_packet.data] = connection
            self.clients_lock.release()
            self.await_client(connection)
            self.clients_lock.acquire()
            send_socket = self.clients[recv_packet.data]
            self.clients_lock.release()
            self.send_recv_loop(connection.socket, send_socket)
    
    def await_client(self, connection: Connection):
        # TODO really need to poll on these packets so client2socket thread (can asyncio solve this?)
        # Check if req_client is already connected, if not wait until it is
        # if req_ip in self.clients.keys():
        #     
        #     client2socket = self.clients[req_ip]
        #     self.send(client2socket, cliensocket.getsockname(), ZPacket.CLIENT_REQ)

        #     recv_packet = self.recv(client2socket)
        #     packet = ZPacket(data=cliensocket.getsockname(), flags=ZPacket.CLIENT_REQ)

        #     # Who checks that client2socket wants to connect (this thread or client2 thread)

        #     client2socket.send(packet.build())

        while True:
            connection.lock.acquire()
            if connection.status == Connection.ACCEPTED:
                connection.lock.release()
                return
            connection.lock.release()
            self.send(connection.socket, flags=ZPacket.CLIENT_WAIT)
            time.sleep(5)
                

    # Cleans up server
    def close(self):
        self.socket.close()

    def send_recv_loop(self, recv_socket: socket, send_socket: socket):
        packet = self.recv(recv_socket)
        if packet is None: # Recv socket disconnected
            self.send(send_socket, flags=ZPacket.CLIENT_DISCONN)
            return

        send_socket.send(packet)

    def send(self, clientsocket: socket, data = "", flags = 0):
        if clientsocket == None:
            print("handle_client: requires client_socket")
            return
        
        packet = ZPacket(data, flags)

        # sending connected status to client
        clientsocket.send(packet.build())
    
    def recv(self, clientsocket: socket) -> ZPacket:
        if clientsocket == None:
            print("handle_client: requires client_socket")
            return
        
        header_bytes = clientsocket.recv(ZPacket.HEADER_LEN)
        if header_bytes == b'': # Zero bytes received
            print("socket connection broken")
            return
        header_struct = struct.unpack('ll', header_bytes)

        data = clientsocket.recv(header_struct[0]).decode('utf-8')

        return ZPacket(data, header_struct[1])

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