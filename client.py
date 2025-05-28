# client.py
import socket
import threading
import time
import io
import wave
import simpleaudio as sa
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from audio_utils import play_audio
from net_utils import send_packet, recv_packet

class VoiceClient:
    def __init__(self, username, on_friend_request=None, on_group_invite=None):
        self.username = username
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_HOST, SERVER_PORT))
        self.sock.send(username.encode())
        self.friends = []
        self.groups = []
        self.on_friend_request = on_friend_request
        self.on_group_invite = on_group_invite
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                packet = recv_packet(self.sock)
                if not packet:
                    break
                try:
                    self.handle_packet(packet)
                except Exception as e:
                    print(f"Packet error: {e}")
            except Exception as e:
                print(f"Listen error: {e}")
                break

    def handle_packet(self, packet):
        # print("Received packet:", packet)  # Uncomment for debugging
        if packet['type'] == 'voice':
            # Play audio from bytes in memory
            with io.BytesIO(packet['data']) as buf:
                with wave.open(buf, 'rb') as wf:
                    wave_obj = sa.WaveObject.from_wave_read(wf)
                    play_obj = wave_obj.play()
                    play_obj.wait_done()
        elif packet['type'] == 'friend_request':
            if self.on_friend_request:
                self.on_friend_request(packet['from'])
        elif packet['type'] == 'group_invite':
            if self.on_group_invite:
                self.on_group_invite(packet['group'])
        elif packet['type'] == 'friends_list':
            self.friends = packet['friends']
        elif packet['type'] == 'groups_list':
            self.groups = packet['groups']

    def send_voice(self, target, is_group, audio_bytes):
        packet = {
            'type': 'voice',
            'from': self.username,
            'to': target,
            'is_group': is_group,
            'data': audio_bytes
        }
        send_packet(self.sock, packet)

    def send_friend_request(self, target):
        send_packet(self.sock, {
            'type': 'friend_request',
            'from': self.username,
            'to': target
        })

    def respond_friend_request(self, from_user, accept):
        send_packet(self.sock, {
            'type': 'friend_response',
            'from': self.username,
            'to': from_user,
            'accept': accept
        })

    def create_group(self, group_name, members):
        send_packet(self.sock, {
            'type': 'group_create',
            'from': self.username,
            'group': group_name,
            'members': members
        })

    def respond_group_invite(self, group_name, accept):
        send_packet(self.sock, {
            'type': 'group_response',
            'from': self.username,
            'group': group_name,
            'accept': accept
        })

    def get_friends(self):
        send_packet(self.sock, {
            'type': 'get_friends',
            'from': self.username
        })
        # Wait for the friends list to be updated by handle_packet
        for _ in range(10):
            if self.friends:
                return list(self.friends)
            threading.Event().wait(0.1)
        return list(self.friends)

    def get_groups(self):
        send_packet(self.sock, {
            'type': 'get_groups',
            'from': self.username
        })
        # Wait for the server to send the updated group list and update self.groups
        for _ in range(10):
            if self.groups:
                return list(self.groups)
            threading.Event().wait(0.1)
        return list(self.groups)

    def close(self):
        # Optionally notify server before closing, if server handles it
        # send_packet(self.sock, {'type': 'close_connection', 'from': self.username})
        self.sock.close()
