import struct
class ZPacket:
    # length of packet header
    HEADER_LEN = 8

    # Connection status flags
    SERV_CONN = 1
    CLIENT_WAIT = 2
    CLIENT_ACCEPT = 4
    CLIENT_DENY = 8
    CLIENT_CONN = 64
    CLIENT_DISCONN = 128

    # query flags
    CLIENT_REQ = 256
    
    def __init__(self, data: str = "", flags: int = 0):
        self.flags = flags
        self.data = data
    
    def build(self) -> bytes:
        # Building header with the length of the data and flags
        header = struct.pack('ll', len(self.data), self.flags)
        
        return header + self.data.encode('utf-8')
    
    @staticmethod
    def parse_bytes(bytes) -> struct:
        if len(bytes) < 16:
            return None
        return bytes[:16]
    
    @staticmethod
    def parse_flag(flags: int) -> str:
        if flags == SERV_CONN:
            return "Server connected"
        elif flags == CLIENT_WAIT:
            return "Waiting for client to connect"
        elif flags == CLIENT_CONN:
            return "Client connected"
        elif flags == CLIENT_DISCONN:
            return "Client disconnected"
        elif flags == CLIENT_REQ:
            return ""
        else:
            return f"Unsupported flag {flags}"
        