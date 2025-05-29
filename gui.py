# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading

from client import VoiceClient
import ttkbootstrap as tb
from ttkbootstrap.constants import *

MAX_VOICE_DURATION = 30  # seconds

class VoiceSnapGUI:
    def __init__(self, username):
        self.username = username
        self.root = tb.Window(themename="pulse")
        self.root.title("VoiceSnap")
        self.root.geometry("650x700")
        self.root.resizable(False, False)
        self.setup_theme()

        username_label = tb.Label(
            self.root,
            text=f"Logged in as: {self.username}",
            bootstyle="inverse-light",
            font=("Segoe UI Rounded", 18, "bold"),
            anchor="center",
            padding=(10, 10)
        )
        username_label.pack(pady=(10, 0), fill="x")

        self.recording_indicator = tb.Label(
            self.root,
            text="● Recording...",
            font=("Segoe UI", 13, "bold"),
            foreground="#e63946",
            bootstyle="danger"
        )
        self.recording_indicator.pack(pady=(0, 5))
        self.recording_indicator.pack_forget()

        self.client = VoiceClient(
            self.username,
            on_friend_request=self.on_friend_request,
            on_group_invite=self.on_group_invite
        )

        self.tabs = tb.Notebook(self.root, bootstyle="primary")
        self.user_tab = tb.Frame(self.tabs)
        self.group_tab = tb.Frame(self.tabs)
        self.tabs.add(self.user_tab, text="Users")
        self.tabs.add(self.group_tab, text="Groups")
        self.tabs.pack(expand=1, fill="both", padx=10, pady=10)

        self.init_user_tab()
        self.init_group_tab()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def setup_theme(self):
        style = tb.Style()
        style.configure('TButton', font=('Segoe UI', 12), padding=8)
        style.configure('TLabel', font=('Segoe UI Rounded', 13))
        style.configure('TNotebook.Tab', font=('Segoe UI Rounded', 12, 'bold'))

    def init_user_tab(self):
        frame = tb.Frame(self.user_tab, padding=10, bootstyle="light")
        frame.pack(fill=tk.BOTH, expand=True)
        self.user_list_frame = tb.Frame(frame, bootstyle="light")
        self.user_list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        btn_frame = tb.Frame(frame, bootstyle="light")
        btn_frame.pack(fill="x", pady=(10, 0))
        refresh_btn = tb.Button(btn_frame, text="🔄 Refresh", command=self.update_user_list, bootstyle="info-outline")
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        add_btn = tb.Button(btn_frame, text="➕ Add User", command=self.add_user, bootstyle="success-outline")
        add_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.update_user_list()

    def update_user_list(self):
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()
        friends = self.client.get_friends() if self.client else []
        for friend in friends:
            frame = tb.Frame(self.user_list_frame, bootstyle="light")
            user_label = tb.Label(
                frame,
                text=friend,
                width=18,
                anchor="w",
                bootstyle="light",
                font=("Segoe UI Rounded", 18, "bold"),
                foreground="#222",
                borderwidth=0,
                relief="flat",
                background="#f4f6fb",
                padding=(24, 14)
            )
            user_label.pack(side=tk.LEFT, padx=(16, 12), pady=12, fill="x")
            hold_btn = tb.Button(
                frame,
                text="🎤",
                bootstyle="success-outline round-toolbutton",
                width=3
            )
            hold_btn.pack(side=tk.LEFT, padx=12, pady=12)
            hold_btn.bind('<ButtonPress-1>', lambda e, f=friend: self.start_recording(f, False))
            hold_btn.bind('<ButtonRelease-1>', lambda e, f=friend: self.stop_recording(f))
            def on_enter(e, btn=hold_btn):
                btn.configure(bootstyle="success dark round-toolbutton")
            def on_leave(e, btn=hold_btn):
                btn.configure(bootstyle="success-outline round-toolbutton")
            hold_btn.bind("<Enter>", on_enter)
            hold_btn.bind("<Leave>", on_leave)
            frame.pack(fill="x", pady=16, padx=16)

    def add_user(self):
        target = simpledialog.askstring("Add User", "Enter username:")
        if target and self.client:
            self.client.send_friend_request(target)
            messagebox.showinfo("Info", f"Friend request sent to {target}")
            self.update_user_list()

    def start_recording(self, target, is_group):
        self.recording_indicator.pack()
        self.stop_event = threading.Event()
        def after_record(audio_bytes):
            self.recording_indicator.pack_forget()
            self.client.send_voice(target, is_group, audio_bytes)
        def record_and_send():
            from audio_utils import record_audio_to_bytes
            audio_bytes = record_audio_to_bytes(self.stop_event, MAX_VOICE_DURATION)
            after_record(audio_bytes)
        self.recording_thread = threading.Thread(target=record_and_send)
        self.recording_thread.start()

    def stop_recording(self, target):
        if hasattr(self, 'stop_event'):
            self.stop_event.set()

    def init_group_tab(self):
        frame = tb.Frame(self.group_tab, padding=10, bootstyle="light")
        frame.pack(fill=tk.BOTH, expand=True)
        self.group_list_frame = tb.Frame(frame, bootstyle="light")
        self.group_list_frame.pack(fill=tk.BOTH, expand=True)
        refresh_btn = tb.Button(frame, text="🔄", command=self.update_group_list, bootstyle="info-outline")
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        create_btn = tb.Button(frame, text="➕ Create Group", command=self.create_group, bootstyle="success-outline")
        create_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.group_buttons = {}
        self.update_group_list()

    def update_group_list(self):
        for widget in self.group_list_frame.winfo_children():
            widget.destroy()
        groups = self.client.get_groups() if self.client else []
        if groups is None:
            groups = []
        for group in groups:
            frame = tb.Frame(self.group_list_frame, bootstyle="light")
            tb.Label(frame, text=group, width=20, anchor="w", bootstyle="light").pack(side=tk.LEFT, padx=5)
            hold_btn = tb.Button(
                frame,
                text="🎤 Hold to Talk",
                bootstyle="success-outline",
            )
            hold_btn.pack(side=tk.LEFT, padx=5)
            hold_btn.bind('<ButtonPress-1>', lambda e, g=group: self.start_recording(g, True))
            hold_btn.bind('<ButtonRelease-1>', lambda e, g=group: self.stop_recording(g, True))
            frame.pack(fill="x", pady=6)
            self.group_buttons[group] = frame

    def create_group(self):
        group_name = simpledialog.askstring("Create Group", "Enter group name:")
        members = []
        while True:
            member = simpledialog.askstring("Add Member", "Enter member username (cancel to stop):")
            if not member:
                break
            members.append(member)
        if group_name and members and self.client:
            self.client.create_group(group_name, members)
            messagebox.showinfo("Info", f"Group '{group_name}' created.")
            self.update_group_list()

    def on_friend_request(self, from_user):
        def respond(accept):
            self.client.respond_friend_request(from_user, accept)
            self.update_user_list()
        if messagebox.askyesno("Friend Request", f"Accept friend request from {from_user}?"):
            respond(True)
        else:
            respond(False)

    def on_group_invite(self, group_name):
        def respond(accept):
            self.client.respond_group_invite(group_name, accept)
            self.update_group_list()
        if messagebox.askyesno("Group Invite", f"Accept invite to group '{group_name}'?"):
            respond(True)
        else:
            respond(False)

    def on_close(self):
        self.client.close()
        self.root.destroy()

if __name__ == "__main__":
    username = input("Enter your username: ")
    VoiceSnapGUI(username)
