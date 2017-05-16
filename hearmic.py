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
FRAMES_PER_BUFFER = 2048
RECORD_SECONDS = 5
END_MESSAGE = "Abort!Abort!Abort!"
 
def processSoundBites(soundBites,transcript):
    shutdown = False
    while not shutdown:
        bite_count = 0
        # Block until there's a soundbite in the queue
        utterance = soundBites.get(True)
        print "Processing sound"
        if utterance == END_MESSAGE:
            print "stopping sound processor"
            shutdown = True
            content = ''
        else:
            content = b''.join(utterance.queue)
            bite_count += 1
        # Append any additional soundbites in the queue
        while not soundBites.empty():
            utterance = soundBites.get(False)
            if utterance == END_MESSAGE:
                print "stopping sound processor"
                shutdown = True
            else:
                content += b''.join(utterance.queue)
                bite_count += 1
        if bite_count:
            print "Sampling content from %d soundbites" % bite_count
            audio_sample = speech_client.sample(
                content=content,
                source_uri=None,
                encoding=speech.encoding.Encoding.LINEAR16,
                sample_rate_hertz=RATE)

            # Find transcriptions of the audio content
            try:
                alternatives = audio_sample.recognize('en-US')
            except ValueError:
                alternatives = None
            if not alternatives:
                print "no results"
            else:
                print "Found %d transcripts:" % len(alternatives)
                for alternative in alternatives:
                    print('Transcript: {}'.format(alternative.transcript))
                    print('Confidence: {}'.format(alternative.confidence))
                    transcript.put(alternative.transcript)

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
transcript = Queue.Queue()
soundprocessor = threading.Thread(target=processSoundBites, args=(frames,transcript,))
soundprocessor.start()
try:
    while True:
        soundbite = Queue.Queue()
        for i in range(0, int((RECORD_SECONDS * RATE / FRAMES_PER_BUFFER) + 0.5)):
            data = stream.read(FRAMES_PER_BUFFER)
            soundbite.put(data)
        print "finished recording %d frames" % len(soundbite.queue)
        frames.put(soundbite)

except KeyboardInterrupt:
    print "ending"
    if soundbite:
        frames.put(soundbite)
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    frames.put(END_MESSAGE)
    print "Waiting for processor to exit"
    soundprocessor.join()
    print "Transcript %s" % " ".join(transcript.queue)
    sys.exit()
