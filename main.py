
import numpy as np
import scipy.signal as ss
from matplotlib import pyplot as plt
import wave
from time import sleep

import pyaudio

import signal_generator as sg

BUFFER_SIZE = 1024
SAMPLE_RATE = 48000
EMPTY_SIGNAL = np.array([])

def read_wave(filename):
    return True

def write_wave_mono(file_path, signal):
    """
    Write a WAV file with PCM encoding (format 1).

    Parameters:
    - file_path: The path to the output WAV file.
    - sample_rate: The sample rate of the audio.
    - data: NumPy array containing the audio data.

    Note: The data should be a NumPy array with values in the range [-1, 1].
    """
    with wave.open(file_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono audio
        wav_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.setcomptype("NONE", "not compressed")

        # Convert float data to PCM format (16-bit integers)
        pcm_data = (signal * np.iinfo(np.int16).max).astype(np.int16)

        wav_file.writeframes(pcm_data.tobytes())

        print(f"written wavefile: {file_path}")

def convert_float_to_int16(ar):
    return (ar * np.iinfo(np.int16).max).astype(np.int16)

def write_wave_12ch(file_path, signal_12):
    """
    Write a WAV file with PCM encoding (format 1).

    Parameters:
    - file_path: The path to the output WAV file.
    - sample_rate: The sample rate of the audio.
    - data: NumPy array containing the audio data.

    Note: The data should be a NumPy array with values in the range [-1, 1].
    """
    with wave.open(file_path, "w") as wav_file:
        wav_file.setnchannels(12)  # Mono audio
        wav_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.setcomptype("NONE", "not compressed")

        wav_file.writeframes(signal_12.tobytes())

        print(f"written wavefile: {file_path}")

def plot_signals(signals_to_plot, orientation="v"):
    if orientation == "v":
        plot_figure = plt.figure(figsize=(8.0, 8.0))
    elif orientation =="h":
        plot_figure = plt.figure(figsize=(8.0, 4.0))

    file_enum, file_enum_max = 0, len(signals_to_plot)

    for signal in signals_to_plot:
        file_enum+=1
        if orientation == "v":
            data_plot = plot_figure.add_subplot(file_enum_max, 1, file_enum)
        elif orientation == "h":
            data_plot = plot_figure.add_subplot(1, file_enum_max, file_enum)
        data_plot.set_ylabel("ok")
        data_plot.plot(signal)

    plot_figure.tight_layout()
    plt.show()

def make_test_signal_12channel(type="sweep", duration=1):
    silence = sg.create_silence(duration)
    arr = []
    for i in range(1, 13):
        signal = EMPTY_SIGNAL
        for j in range(1, 13):
            if i == j:
                if type == "sweep":
                    signal = sg.add_signal(signal, sg.create_sweep(80, 5000, duration, "log"))
                elif type == "pink":
                    signal = sg.add_signal(signal, sg.pink_noise(duration))
                elif type == "burst":
                    signal = sg.add_signal(signal, sg.create_burst("pink", 1, 0.01))
            elif j == 13 or i != j:
                signal = sg.add_signal(signal, silence)
        print(f"channel_{i}")
        arr.append(convert_float_to_int16(signal))
        # write_wave_mono(f"{type}_channel_{i}.wav", signal)
    return np.array(arr).T

def record_audio(file_path, duration=1):
    """
    Record audio from the microphone and save it to a WAV file.

    Parameters:
    - file_path: The path to the output WAV file.
    - duration: The duration of the recording in seconds.
    - sample_rate: The sample rate of the audio.
    - chunk_size: The number of frames per buffer.

    Note: The default values are set for a common configuration (44.1 kHz sample rate, 16-bit PCM).
    """
    p_in = pyaudio.PyAudio()

    stream = p_in.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=BUFFER_SIZE)

    print("Recording...")
    frames = []

    for i in range(0, int(SAMPLE_RATE / BUFFER_SIZE * duration)):
        data = stream.read(BUFFER_SIZE)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    p_in.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))

def play_audio(file_path):
    p_out = pyaudio.PyAudio()
    with wave.open(file_path, "rb") as wf:
        stream = p_out.open(format=p_out.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
        # Play samples from the wave file (3)
        while len(data := wf.readframes(BUFFER_SIZE)):
            stream.write(data)
        print("streaming")
        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        p_out.terminate()

def play_and_record(file_path, output_file, duration=1):
    p = pyaudio.PyAudio()

    # Open a stream for recording
    record_stream = p.open(format=pyaudio.paInt16,
                           channels=1,
                           rate=SAMPLE_RATE,
                           input=True,
                           frames_per_buffer=BUFFER_SIZE)

    # Open the WAV file for playback
    wf = wave.open(file_path, "rb")
    playback_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                             channels=wf.getnchannels(),
                             rate=wf.getframerate(),
                             output=True)

    frames = []

    for i in range(int(SAMPLE_RATE / BUFFER_SIZE * duration)):
        # Read audio from the playback stream
        playback_data = wf.readframes(BUFFER_SIZE)

        # Play audio
        playback_stream.write(playback_data)

        # Record audio from the microphone
        record_data = record_stream.read(BUFFER_SIZE)
        frames.append(record_data)

    print("Playback and recording complete.")

    # Stop and close the streams
    playback_stream.stop_stream()
    playback_stream.close()
    record_stream.stop_stream()
    record_stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(output_file, "wb") as wf_out:
        wf_out.setnchannels(1)
        wf_out.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf_out.setframerate(SAMPLE_RATE)
        wf_out.writeframes(b"".join(frames))

if __name__ == "__main__":
    ts = make_test_signal_12channel("burst", 1)
    # play_and_record("sweep_channel_2.wav", "input.wav", duration=5)
    write_wave_12ch("12ch.wav", ts)
    
