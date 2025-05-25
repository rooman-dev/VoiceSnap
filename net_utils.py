import struct
import pickle

def send_packet(sock, packet):
    data = pickle.dumps(packet)
    length = struct.pack('!I', len(data))  # 4 bytes, network order
    sock.sendall(length + data)

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Socket closed")
        data += packet
    return data

def recv_packet(sock):
    raw_length = recv_all(sock, 4)
    if not raw_length:
        return None
    data_length = struct.unpack('!I', raw_length)[0]
    data = recv_all(sock, data_length)
    return pickle.loads(data)