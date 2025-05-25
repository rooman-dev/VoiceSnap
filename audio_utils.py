# audio_utils.py
import sounddevice as sd
from scipy.io.wavfile import write
import simpleaudio as sa
import os
import numpy as np
import threading

def record_audio(filename, stop_event, duration=30, on_finish=None):
    fs = 44100
    frames = []

    def callback(indata, frames_count, time_info, status):
        if stop_event.is_set():
            raise sd.CallbackStop()
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=callback):
        try:
            sd.sleep(int(duration * 1000))  # Max duration
        except sd.CallbackStop:
            pass

    audio = np.concatenate(frames, axis=0)
    write(filename, fs, audio)
    print(f"Recording saved to {filename}")
    if on_finish:
        on_finish()

def play_audio(filename):
    if os.path.exists(filename):
        try:
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            print(f"Error during playback: {e}")
    else:
        print(f"File {filename} does not exist.")
