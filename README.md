# 🎤 VoiceSnap – Push-to-Talk Desktop Voice Communication

**VoiceSnap** is a real-time, push-to-talk (PTT) voice communication platform built with Python. Inspired by walkie-talkie-style simplicity, VoiceSnap allows users to send short voice messages to individuals or groups over a network, using a modern desktop interface.

---

## ✨ Features

- 🎙️ **Push-to-Talk**: Record and send voice clips to friends or groups with a single click.
- 👥 **Friend & Group System**: Send friend requests, accept them, and create voice chat groups.
- 🖥️ **Modern Multi-Pane GUI**: Built with Tkinter, organized into Users, Groups, Logs, and Settings.
- 🔊 **Real-Time Audio**: Uses `sounddevice` and `pygame` for low-latency voice playback and recording.
- 📡 **Socket-Based Client-Server Architecture**: Lightweight and efficient networking using Python sockets.
- 🧵 **Multi-threaded Design**: Responsive GUI and concurrent voice transmission.

---

## 🛠 Tech Stack

- **Language**: Python 3.11+
- **Libraries**: `Tkinter`, `socket`, `threading`, `sounddevice`, `pygame`, `scipy`, `simpleaudio`
- **Structure**:
  - `gui.py`: Main GUI with four windows and live updates
  - `client.py`: Client-side logic and socket communication
  - `server.py`: Central server handling users, groups, and messages
  - `audio_utils.py`: Handles voice recording and playback
  - `config.py`: Constants like IPs, ports, and cooldowns

---

