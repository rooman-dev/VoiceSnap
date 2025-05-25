# client.py
import socket
import threading
import pickle
import time
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from audio_utils import play_audio

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
        self.received_messages = {}  # {user/group: [filename, ...]}
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    break
                try:
                    packet = pickle.loads(data)
                    self.handle_packet(packet)
                except Exception as e:
                    print(f"Packet error: {e}")
            except Exception as e:
                print(f"Listen error: {e}")
                break

    def handle_packet(self, packet):
        if packet['type'] == 'voice':
            filename = f"recv_{packet['from']}_{int(time.time())}.wav"
            with open(filename, 'wb') as f:
                f.write(packet['data'])
            # Store for playback
            self.received_messages.setdefault(packet['from'], []).append(filename)
            play_audio(filename)  # <-- This auto-plays the message!
        elif packet['type'] == 'friend_request':
            print(f"Friend request from {packet['from']}")
            if self.on_friend_request:
                self.on_friend_request(packet['from'])
        elif packet['type'] == 'group_invite':
            print(f"Group invite to {packet['group']}")
            if self.on_group_invite:
                self.on_group_invite(packet['group'])
        elif packet['type'] == 'friends_list':
            self.friends = packet['friends']
        elif packet['type'] == 'groups_list':
            self.groups = packet['groups']

    def send_voice(self, target, is_group, filename):
        with open(filename, 'rb') as f:
            data = f.read()
        packet = {
            'type': 'voice',
            'from': self.username,
            'to': target,
            'is_group': is_group,
            'data': data
        }
        self.sock.send(pickle.dumps(packet))

    def send_friend_request(self, target):
        self.sock.send(pickle.dumps({
            'type': 'friend_request',
            'from': self.username,
            'to': target
        }))

    def respond_friend_request(self, from_user, accept):
        self.sock.send(pickle.dumps({
            'type': 'friend_response',
            'from': self.username,
            'to': from_user,
            'accept': accept
        }))

    def create_group(self, group_name, members):
        self.sock.send(pickle.dumps({
            'type': 'group_create',
            'from': self.username,
            'group': group_name,
            'members': members
        }))

    def respond_group_invite(self, group_name, accept):
        self.sock.send(pickle.dumps({
            'type': 'group_response',
            'from': self.username,
            'group': group_name,
            'accept': accept
        }))

    def get_friends(self):
        self.sock.send(pickle.dumps({
            'type': 'get_friends',
            'from': self.username
        }))
        # Wait for the friends list to be updated by handle_packet
        for _ in range(10):
            if self.friends:
                return list(self.friends)
            threading.Event().wait(0.1)
        return list(self.friends)

    def get_groups(self):
        self.sock.send(pickle.dumps({
            'type': 'get_groups',
            'from': self.username
        }))
        # Wait for the groups list to be updated by handle_packet
        for _ in range(10):
            if self.groups:
                return list(self.groups)
            threading.Event().wait(0.1)
        return list(self.groups)

    def close(self):
        self.sock.close()
