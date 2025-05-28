# VoiceSnap

**VoiceSnap** is a modern, real-time voice messaging application for local networks or the internet. It features a beautiful GUI, instant push-to-talk voice messaging, friend and group management, and automatic playback of received messages.

---

## Features

- 🎤 Push-to-talk voice messaging (walkie-talkie style)
- 👥 Friend and group management
- 🖥️ Modern, responsive GUI (ttkbootstrap)
- 🔔 Instant playback of received messages
- 🔄 Live refresh for users and groups
- ⏱️ Message cooldown to prevent spam

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/voicesnap.git
   cd voicesnap
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

---

## Usage

1. **Start the server:**
   ```sh
   python server.py
   ```

2. **Start the client GUI (on the same or another PC):**
   ```sh
   python gui.py
   ```
   Enter a unique username when prompted.

3. **Add friends or create groups using the GUI.**
4. **Hold the 🎤 button to record and send a voice message.**

---

## Configuration

Edit `config.py` to set:
- `SERVER_HOST` and `SERVER_PORT` for your network setup.
- `MAX_VOICE_DURATION` for maximum message length.

---

## Requirements

- Python 3.8+
- See `requirements.txt` for Python package dependencies.

---

## License

MIT License

---

**VoiceSnap** – The fastest way to talk with your friends, hands-free!
