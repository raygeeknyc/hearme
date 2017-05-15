import pyaudio
import audioop
 
# Import the Google Cloud client library
from google.cloud import speech

# first you have to authenticate for the default application: gcloud auth application-default login

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 1024
RECORD_SECONDS = 10
 
# Instantiates a speech service client
speech_client = speech.Client()

print "initializing pyaudio"
audio = pyaudio.PyAudio()
 
print "opening audio"
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=FRAMES_PER_BUFFER)

print "capturing"
frames = []
for i in range(0, int((RECORD_SECONDS * RATE / FRAMES_PER_BUFFER) + 0.5)):
    data = stream.read(FRAMES_PER_BUFFER)
    frames.append(data)
print "finished recording %d frames" % len(frames)

print "Sampling content"
audio_sample = speech_client.sample(
    content=b''.join(frames),
    source_uri=None,
    encoding=speech.encoding.Encoding.LINEAR16,
    sample_rate_hertz=RATE)

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# Find transcriptions of the audio content
alternatives = audio_sample.recognize('en-US')

#print "Found %d alternative transcripts:" % len(alternatives)
if not alternatives:
    print "no results"
else:
    for alternative in alternatives:
        print('Transcript: {}'.format(alternative.transcript))
        print('Confidence: {}'.format(alternative.confidence))
