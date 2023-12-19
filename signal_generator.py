import numpy as np

SAMPLE_RATE = 48000

def add_signal(signal, signal_to_add):
    return np.append(signal, signal_to_add)

def create_silence(duration):
    signal = np.zeros([1, int(SAMPLE_RATE*duration)])[0]
    return signal

def create_sinewave(frequency, duration):
    time = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    signal = np.sin(2 * np.pi * frequency * time)
    return signal

def create_sweep(frequency1, frequency2, duration, type='lin'):
    time = np.linspace(0, duration, int(SAMPLE_RATE*duration), endpoint=False)
    if type == 'lin':
        freq = np.linspace(frequency1, frequency2, int(SAMPLE_RATE*duration), endpoint=False)
    elif type == 'log':
        freq = np.logspace(np.log10(frequency1), np.log10(frequency2), int(SAMPLE_RATE*duration), endpoint=False)
    elif type == 'geo':
        freq = np.geomspace(frequency1, frequency2, int(SAMPLE_RATE*duration), endpoint=False)
    signal = np.sin(2 * np.pi * freq * time)
    return signal

def noise_psd(duration, psd = lambda f: 1):
        X_white = np.fft.rfft(np.random.randn(int(duration*SAMPLE_RATE)))
        S = psd(np.fft.rfftfreq(int(duration*SAMPLE_RATE)))
        # Normalize S
        S = S / np.sqrt(np.mean(S**2))
        X_shaped = X_white * S
        return np.fft.irfft(X_shaped)

def PSDGenerator(f):
    return lambda N: noise_psd(N, f)

@PSDGenerator
def white_noise(f):
    return 1

@PSDGenerator
def blue_noise(f):
    return np.sqrt(f)

@PSDGenerator
def violet_noise(f):
    return f

@PSDGenerator
def brownian_noise(f):
    return 1/np.where(f == 0, float('inf'), f)

@PSDGenerator
def pink_noise(f):
    return 1/np.where(f == 0, float('inf'), np.sqrt(f))

def create_burst(colour="pink", duration=1, fill=0.25):

    signal = pink_noise(duration*fill)
    add_signal(signal, create_silence(duration*(1-fill)))
    return signal