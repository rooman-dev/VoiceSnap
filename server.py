# server.py
import socket
import threading
import time
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, COOLDOWN_SECONDS
from client import send_packet, recv_packet

clients = {}         # username -> socket
user_friends = {}    # username -> set of accepted friends
pending_friends = {} # username -> set of pending requests
groups = {}          # group_name -> set of usernames
pending_groups = {}  # username -> set of pending group invites
cooldowns = {}       # username -> last sent timestamp
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        username = conn.recv(BUFFER_SIZE).decode()
        with lock:
            clients[username] = conn
            user_friends.setdefault(username, set())
            pending_friends.setdefault(username, set())
            pending_groups.setdefault(username, set())
        print(f"{username} connected.")

        while True:
            packet = recv_packet(conn)
            if not packet:
                break

            if packet['type'] == 'voice':
                sender = packet['from']
                target = packet['to']
                is_group = packet['is_group']
                now = time.time()
                voice_data = packet['data']

                if len(voice_data) > 2 * 44100 * 30:  # crude check: 2 bytes/sample * 44100 Hz * 30s
                    send_packet(conn, {'type': 'error', 'message': 'Message too long.'})
                    continue

                with lock:
                    if cooldowns.get(sender, 0) + COOLDOWN_SECONDS > now:
                        send_packet(conn, {'type': 'error', 'message': 'Cooldown active.'})
                        continue
                    cooldowns[sender] = now

                if is_group:
                    with lock:
                        members = groups.get(target, set())
                    for member in members:
                        if member == sender:
                            continue
                        with lock:
                            if member in clients:
                                # Accept/decline logic
                                if sender not in user_friends.get(member, set()):
                                    send_packet(clients[member], {
                                        'type': 'group_invite',
                                        'group': target,
                                        'from': sender
                                    })
                                    continue
                                send_packet(clients[member], packet)
                else:
                    with lock:
                        if target in clients:
                            # Accept/decline logic
                            if sender not in user_friends.get(target, set()):
                                send_packet(clients[target], {
                                    'type': 'friend_request',
                                    'from': sender
                                })
                                continue
                            send_packet(clients[target], packet)

            elif packet['type'] == 'friend_request':
                target = packet['to']
                sender = packet['from']
                with lock:
                    pending_friends.setdefault(target, set()).add(sender)
                with lock:
                    if target in clients:
                        send_packet(clients[target], {
                            'type': 'friend_request',
                            'from': sender
                        })

            elif packet['type'] == 'friend_response':
                from_user = packet['from']
                to_user = packet['to']
                accept = packet['accept']
                with lock:
                    if accept:
                        user_friends.setdefault(from_user, set()).add(to_user)
                        user_friends.setdefault(to_user, set()).add(from_user)
                    pending_friends[to_user].discard(from_user)
                    if to_user in clients:
                        send_packet(clients[to_user], {
                            'type': 'friend_response',
                            'from': from_user,
                            'accept': accept
                        })

            elif packet['type'] == 'group_create':
                creator = packet['from']
                group = packet['group']
                members = set(packet['members'])
                with lock:
                    groups[group] = members | {creator}
                    for member in members:
                        pending_groups.setdefault(member, set()).add(group)
                        if member in clients:
                            send_packet(clients[member], {
                                'type': 'group_invite',
                                'group': group,
                                'from': creator
                            })

            elif packet['type'] == 'group_response':
                user = packet['from']
                group = packet['group']
                accept = packet['accept']
                with lock:
                    if accept:
                        groups.setdefault(group, set()).add(user)
                    pending_groups[user].discard(group)

            elif packet['type'] == 'get_friends':
                with lock:
                    friends = list(user_friends.get(packet['from'], set()))
                send_packet(conn, {'type': 'friends_list', 'friends': friends})

            elif packet['type'] == 'get_groups':
                with lock:
                    user_groups = [g for g, members in groups.items() if packet['from'] in members]
                send_packet(conn, {'type': 'groups_list', 'groups': user_groups})

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        with lock:
            for k, v in list(clients.items()):
                if v == conn:
                    clients.pop(k, None)
        print(f"{username} disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
