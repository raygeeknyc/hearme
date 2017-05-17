import Queue
import threading
import sys
import pyaudio
import audioop
 
# Import the Google Cloud client library
from google.cloud import speech

# first you have to authenticate for the default application: gcloud auth application-default login

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 1024
MAX_SOUNDBITE_SECS = 10
SILENCE_THRESHOLD = 4
 
def processSoundBites(soundBites):
    while True:
        print "Sampling content"
        # Block until there's a soundbite in the queue
        content = b''.join(soundbites.get(True))
        # Append any additional soundbites in the queue
        while not soundbites.empty():
            content += b''.join(soundbites.get(false))
        audio_sample = speech_client.sample(
            content=content,
            source_uri=None,
            encoding=speech.encoding.Encoding.LINEAR16,
            sample_rate_hertz=RATE)

        # Find transcriptions of the audio content
        alternatives = audio_sample.recognize('en-US')

        if not alternatives:
            print "no results"
        else:
            print "Found %d transcripts:" % len(alternatives)
            for alternative in alternatives:
                print('Transcript: {}'.format(alternative.transcript))
                print('Confidence: {}'.format(alternative.confidence))

# Instantiates a speech service client
speech_client = speech.Client()

print "initializing pyaudio"
audio = pyaudio.PyAudio()
 
print "opening audio"
# Start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=FRAMES_PER_BUFFER)

print "capturing"
frames=Queue.Queue()
soundprocessor = threading.Thread(target=processSoundBites, args=(frames,))

try:
    while True:
        soundbite = []
        volume = 0
        while volume <= SILENCE_THRESHOLD:
            data = stream.read(FRAMES_PER_BUFFER)
            volume = max(data)
        soundbite.append(data)
        remaining_samples = int((MAX_SOUNDBITE_SECS * RATE / FRAMES_PER_BUFFER) + 0.5) - 1
        for i in range(0, remaining_samples):
            data = stream.read(FRAMES_PER_BUFFER)
            soundbite.append(data)
        print "finished recording %d frames" % len(soundbite)
        frames.append(soundbite)
except KeyboardInterrupt:
    print "ending"
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    sys.exit()

