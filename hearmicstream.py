import Queue
from array import array
import threading
import sys
import pyaudio
import io
from streamrw import StreamRW
import logging
 
# Import the Google Cloud client library
from google.cloud import speech

# first you have to authenticate for the default application: gcloud auth application-default login

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 2048
MAX_SOUNDBITE_SECS = 10
SILENCE_THRESHOLD = 500
PAUSE_LENGTH_SECS = 1
PAUSE_LENGTH_IN_SAMPLES = int((PAUSE_LENGTH_SECS * RATE / FRAMES_PER_BUFFER) + 0.5)
 
def processSound(audio_stream, transcript):
    speech_client = speech.Client()
    audio_sample = speech_client.sample(
        stream=audio_stream,
        source_uri=None,
        encoding=speech.encoding.Encoding.LINEAR16,
        sample_rate_hertz=RATE)

    while not audio_stream.closed:
        # Find transcriptions of the audio content
        try:
            alternatives = audio_sample.streaming_recognize('en-US',
                interim_results=True)
        except Exception, e:
            logging.error("Recognition raised {}".format(e))
            alternatives = None
        if not alternatives:
            logging.debug("no results")
        else:
            for alternative in alternatives:
                logging.debug('Transcript: {}'.format(alternative.transcript))
                logging.debug('Confidence: {}'.format(alternative.confidence))
                if alternative.is_final:
                    transcript.put(alternative.transcript)
    logging.debug("audio stream closed")

logging.getLogger().setLevel(logging.DEBUG)


print "initializing pyaudio"
audio = pyaudio.PyAudio()
 
print "opening audio"
# Start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=FRAMES_PER_BUFFER)

print "capturing"
audio_stream = StreamRW(io.BytesIO())
transcript = Queue.Queue()
soundprocessor = threading.Thread(target=processSound, args=(audio_stream,transcript,))
soundprocessor.start()
try:
    logging.debug("initial sample, waiting for sound")
    consecutive_silent_samples = 0
    volume = 0
    # Wait for sound
    while volume <= SILENCE_THRESHOLD:
        data = array('h', stream.read(FRAMES_PER_BUFFER))
        volume = max(data)
    logging.debug("sound heard")
    w = audio_stream.write(data)
    audio_stream.flush()
    while True:
        data = array('h', stream.read(FRAMES_PER_BUFFER))
        volume = max(data)
        if volume <= SILENCE_THRESHOLD:
            consecutive_silent_samples += 1
        else:
            consecutive_silent_samples = 0
        w = audio_stream.write(data)
        audio_stream.flush()
        if consecutive_silent_samples >= PAUSE_LENGTH_IN_SAMPLES:
            logging.debug("pause detected")
except KeyboardInterrupt:
    logging.info("ending")
    # Close the recognizer's stream
    audio_stream.close()
    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    logging.debug("Waiting for processor to exit")
    soundprocessor.join()
    print "Transcript %s" % ";".join(transcript.queue)
    sys.exit()
