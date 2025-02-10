import socket
import struct
import sys

from zPacket import ZPacket

buf_size = 512

class Client():
    def __init__(self, ip: str, port: str):
        # creating socket
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # connecting socket to server
        self.clientsocket.connect((ip, int(port)))

    def connect_to_client(self):
        recv_packet = self.recv()
        if recv_packet is None:
            return

        # If this client has already been requested
        if recv_packet.flags == ZPacket.SERV_CONN | ZPacket.CLIENT_REQ:
            if self.accept_client_req(recv_packet):
                self.message_client()

        if recv_packet.flags & ZPacket.SERV_CONN == ZPacket.SERV_CONN:
            req_client = input("Enter recipient ip: ")
            self.send(req_client, ZPacket.CLIENT_REQ)
            if not self.wait_for_client():
                return
            self.message_client()

    # Wait for updates on client req from server
    def wait_for_client(self) -> bool:
        while True:
            recv_packet = self.recv()
            if recv_packet is None:
                return False

            if recv_packet.flags == ZPacket.CLIENT_REQ:
                self.accept_client_req(recv_packet)
            elif recv_packet.flags == ZPacket.CLIENT_CONN:
                print(f"Connected to client with ip {recv_packet.data}")
                return True
            elif recv_packet.flags == ZPacket.CLIENT_WAIT:
                print("Waiting for client to accept....")

    def accept_client_req(self, recv_packet) -> bool:
        resp = input(f"connect to {recv_packet.data}? [y/n]")
        if resp == "y":
            self.send(recv_packet.data, ZPacket.CLIENT_ACCEPT)
            return True
        self.send(flags=ZPacket.CLIENT_DENY)
        return False

    def message_client(self):
        # loop to send messages
        while True:
            msg = input("Enter message: ")
            if msg == "quit":
                print("closing connection")
                break

            self.send(msg)
            
            recv_packet = self.recv()
            if recv_packet is None or recv_packet.flags == ZPacket.CLIENT_DISCONN:
                break
            print(recv_packet.data)

    def recv(self) -> ZPacket:
        header_bytes = self.clientsocket.recv(ZPacket.HEADER_LEN)
        if header_bytes == b'': # Zero bytes received
            print("socket connection broken")
            return
        header_struct = struct.unpack('ll', header_bytes)

        data = self.clientsocket.recv(header_struct[0]).decode('utf-8')

        return ZPacket(data, header_struct[1])
    
    def send(self, data = "", flags = 0):
        packet = ZPacket(data, flags)
        self.clientsocket.send(packet.build())
    
    def shutdown(self):
        #TODO send disconnect msg to server
        self.clientsocket.close()

def main(ip, port):
    client = Client(ip, port)
    client.connect_to_client()
    client.shutdown()
    
if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Need ip and port to connect to")