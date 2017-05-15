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
RECORD_SECONDS = 10
 
def processSoundBites(soundBites):
    while True:
        bite_count = 0
        # Block until there's a soundbite in the queue
        content = b''.join(soundBites.get(True))
        bite_count += 1
        # Append any additional soundbites in the queue
        while not soundBites.empty():
            content += b''.join(soundBites.get(false))
            bite_count += 1
        print "Sampling content from %d soundbites" % bite_count
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
soundprocessor.start()
try:
    while True:
        soundbite = []
        for i in range(0, int((RECORD_SECONDS * RATE / FRAMES_PER_BUFFER) + 0.5)):
            data = stream.read(FRAMES_PER_BUFFER)
            soundbite.append(data)
        print "finished recording %d frames" % len(soundbite)
        frames.put(soundbite)

except KeyboardInterrupt:
    print "ending"
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    sys.exit()

