import socket
import sys

buf_size = 512

def main(ip, port):
    # creating socket
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connecting socket to server
    clientsocket.connect((ip, int(port)))
    
    # loop to send messages
    while True:
        msg = input("Enter message: ")
        if msg == "quit":
            print("closing connection")
            break
        
        clientsocket.send(msg.encode('utf-8'))
        
        msg = clientsocket.recv(buf_size)
        if msg == b'': # Zero bytes received
            print("socket connection broken")
            break
            
        print(msg.decode('utf-8'))
    
    clientsocket.close()
    
if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Need ip and port to connect to")