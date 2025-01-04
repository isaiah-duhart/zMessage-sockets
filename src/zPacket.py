SERV_CONN = 1
CLIENT_WAIT = 2
CLIENT_CONN = 4
CLIENT_DISCONN = 8

class ZPacket:
    def __init__(self, flags: int = 0, data: str):
        self.flags = flags
        self.data = data
    
    def build(self) -> bytes:
        # Building packet with the length of the data and flags
        packet = struct.pack('lh', len(self.data), flags)
        
        return packet + self.data.encode('utf-8')
    
    def parse_flag(self) -> str:
        if self.flags == SERV_CONN:
            return "Server connected"
        elif self.flags == CLIENT_WAIT:
            return "Waiting for client to connect"
        elif self.flags == CLIENT_CONN:
            return "Client connected"
        elif self.flags == CLIENT_DISCONN:
            return "Client disconnected"
        else:
            return f"Unsupported flag {self.flags}"
        