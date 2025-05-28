# audio_utils.py
import simpleaudio as sa
import os
import numpy as np
import threading
import time
from scipy.io.wavfile import write

def record_audio(filename, stop_event, duration=30, on_finish=None):
    import sounddevice as sd
    fs = 44100
    frames = []
    start_time = time.time()
    def callback(indata, frames_count, time_info, status):
        frames.append(indata.copy())
        if stop_event.is_set() or (time.time() - start_time) > duration:
            raise sd.CallbackStop

    with sd.InputStream(samplerate=fs, channels=1, dtype='float32', callback=callback):
        while not stop_event.is_set() and (time.time() - start_time) < duration:
            sd.sleep(10)

    audio = np.concatenate(frames, axis=0)
    # Convert to int16 PCM
    audio_int16 = np.int16(audio * 32767)
    write(filename, fs, audio_int16)
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

def stop_recording(self, target, is_group):
    print("Stopping recording now")
    if hasattr(self, 'stop_event'):
        self.stop_event.set()
