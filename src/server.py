import socket
import sys

buf_size = 512

def main(ip, port):
    # creating server socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # binding socket to provided port
    serversocket.bind((ip, int(port)))
    
    # listening for incoming connections
    serversocket.listen(5)
    
    (clientsocket, addresss) = serversocket.accept()
    
    while True:    
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
    
    serversocket.close()
    
if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Need ip and port to host server")