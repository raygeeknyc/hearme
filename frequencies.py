import statistics
import pyaudio
import audioop
import numpy as np
import matplotlib.pyplot as plt
import sys
import logging
logging.getLogger('').setLevel(logging.INFO)

np.set_printoptions(suppress=True) # don't use scientific notation

CHUNK_SIZE = 4096 # number of data points to read at a time
RATE = 44100 # Sampling rate of the input microphone
POWER_SAMPLE_SECS=2
_POWER_WINDOW=-1*int(RATE / CHUNK_SIZE * POWER_SAMPLE_SECS)

_AUDIO_DATA_WIDTH = 2  # 16 bit audio data

def get_rms(audio_chunk):
    return audioop.rms(audio_chunk, _AUDIO_DATA_WIDTH)

def plot_fft_powers_peaks(plots, fft, powers, average_powers, peaks):
    plot1, plot2, plot3 = plots

    plot1.cla()
    plot1.title.set_text('fft')
    plot1.plot(fft)

    plot2.cla()
    plot2.title.set_text('power vs {} sec average'.format(POWER_SAMPLE_SECS))
    intervals = range(-1*len(powers) + 1, 1)
    y_pos = np.arange(len(intervals))
    plot2.bar(y_pos, powers, align='center', alpha=0.5)
    plot2.plot(y_pos, average_powers)
    plot2.set_ylim(min(powers)-1, max(powers))

    plot3.cla()
    plot3.title.set_text('peak frequencies')
    intervals = range(-1*len(peaks) + 1, 1)
    y_pos = np.arange(len(intervals))
    plot3.plot(y_pos, peaks)

    plt.tight_layout()
    plt.show()
    plt.pause(0.00001)
    
def main(capture_secs):
    p=pyaudio.PyAudio() # start the PyAudio class
    mic_stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  frames_per_buffer=CHUNK_SIZE)
    
    plt.ion()
    fig, subplots = plt.subplots(3)

    peaks = []
    powers = []
    average_powers = []
    for i in range(0, int(RATE / CHUNK_SIZE * capture_secs)):
        data = np.frombuffer(mic_stream.read(CHUNK_SIZE,exception_on_overflow=False),dtype=np.int16)
        data = data * np.hanning(len(data))
        fft = abs(np.fft.fft(data).real)
        fft = fft[:int(len(fft)/2)] # keep only first half
        frequency = np.fft.fftfreq(CHUNK_SIZE,1.0/RATE)
        frequency = frequency[:int(len(frequency)/2)] # keep only first half
        freqPeak = frequency[np.where(fft==np.max(fft))[0][0]]+1
        print("peak frequency: %d Hz"%freqPeak)
        peaks.append(freqPeak)
        power = get_rms(data)
        powers.append(power)
        average_power = statistics.mean(powers[_POWER_WINDOW:])
        average_powers.append(average_power)
        plot_fft_powers_peaks(subplots, fft, powers, average_powers, peaks)
    
    # close the stream gracefully
    mic_stream.stop_stream()
    mic_stream.close()
    p.terminate()
    plt.close()

if __name__=="__main__":
    if len(sys.argv) == 2:
        secs = int(sys.argv[1])
        main(secs)
        sys.exit(0)
    else:
        logging.error('%s seconds', sys.argv[0])
        sys.exit(255)
