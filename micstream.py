import pyaudio
import wave
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
 
print "initializing pyaudio"
audio = pyaudio.PyAudio()
 
print "opening audio"
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

print "opening recording file"
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
print "recording..."
frames = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
    waveFile.writeframes(data)
print "finished recording"
 
 
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile.close()
