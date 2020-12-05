#!/opt/local/bin/python3
from scipy import signal
from scipy.io import wavfile
from scipy.fftpack import fft, ifft,fftfreq
import matplotlib.pyplot as plt
import wave 
import numpy as np
import sys
import struct

def get_audio(filename):
    frate,data = wavfile.read(filename)
    print(frate)
    b = signal.firwin(101, cutoff=900, fs= frate, pass_zero=False)
    data = signal.lfilter(b, [1.0], data)
    return frate, data

def get_fft(data):
    w = np.fft.fft(data)
    return w

def get_freq_peak(fft):
    freqs = np.fft.fftfreq(len(fft))
    #print(len(w)/frate)
    #print(w.min(), w.max())
    # (-0.5, 0.499975)

    # Find the peak in the coefficients
    idx = np.argmax(np.abs(fft))
    winner = np.argwhere(np.abs(fft) == np.amax(np.abs(fft)))

    freq = freqs[idx]
    return freq

def main(filename):
    frate, chunk = get_audio(filename)
    fft = get_fft(chunk)
    peak_frequency = get_freq_peak(fft)
    freq_in_hertz = abs(peak_frequency * frate)
    print("{} HZ".format(freq_in_hertz))

if len(sys.argv) == 2:
    main(sys.argv[1])
