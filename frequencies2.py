#!/opt/local/bin/python3
import sys
import scipy.io.wavfile as wavfile
import numpy as np
import pylab as pl

def power_and_peak_frequency(audio_data, sampling_rate):
  p = 20*np.log10(np.abs(np.fft.rfft(audio_data)))
  f = np.linspace(0, sampling_rate/2.0, len(p))
  return (p, f)

def main(filename):
  rate, data = wavfile.read(filename)
  print(len(data))
  t = np.arange(len(data))*1.0/rate
  pl.plot(t, data)
  pl.show()

  freq, power = power_and_peak_frequency(data, rate)
  pl.xlabel("Frequency(Hz)")
  pl.ylabel("Power(dB)")
  pl.plot(freq, power)

  print("{} Hz".format(int(max(freq))))
  pl.show()

main(sys.argv[1])
