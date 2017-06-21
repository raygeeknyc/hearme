import Queue
import time
from array import array
import threading
import sys
import pyaudio
import io
import logging
from fedstream import FedStream
 
# Import the Google Cloud client library
from google.cloud import speech

# first you have to authenticate for the default application: gcloud auth application-default login

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 4096
SILENCE_THRESHOLD = 500
PAUSE_LENGTH_SECS = 1.0
AUDIO_BUFFER_SECS = 2.0
PAUSE_LENGTH_IN_SAMPLES = int((PAUSE_LENGTH_SECS * RATE / FRAMES_PER_BUFFER) + 0.5)
AUDIO_STREAM_BUFFER_SIZE = int(FRAMES_PER_BUFFER * 2 * (RATE / FRAMES_PER_BUFFER) * (PAUSE_LENGTH_SECS + AUDIO_BUFFER_SECS))
AUDIO_STREAM_BUFFER_SIZE = 32768
 
def processSound(audio_stream, transcript):
    global stop
    speech_client = speech.Client()
    logging.debug("created client")

    while not stop:
        try:
            logging.debug("sampling")
            audio_sample = speech_client.sample(
                stream=audio_stream,
                encoding=speech.encoding.Encoding.LINEAR16,
                sample_rate_hertz=RATE)

            alternatives = audio_sample.streaming_recognize('en-US',
                interim_results=True)
            # Find transcriptions of the audio content
            for alternative in alternatives:
                logging.debug('Transcript: {}'.format(alternative.transcript))
                if alternative.is_final:
                    logging.debug('Final: {}'.format(alternative.is_final))
                    logging.debug('Confidence: {}'.format(alternative.confidence))
                    transcript.put(alternative.transcript)
        except ValueError, e:
            logging.warning("processor: end of audio {}".format(str(e)))
            stop = True
        except Exception, e:
            logging.error("Recognition raised {}".format(e))
    logging.debug("processor ending")


logging.getLogger().setLevel(logging.DEBUG)

logging.debug("initializing pyaudio")
audio = pyaudio.PyAudio()
 
logging.debug("opening audio")
# Start Recording
logging.info("capturing from mic")
mic_stream = audio.open(format=FORMAT, channels=CHANNELS,
             rate=RATE, input=True,
             frames_per_buffer=FRAMES_PER_BUFFER)

audio_buffer = Queue.Queue()
audio_stream = FedStream(audio_buffer)
transcript = Queue.Queue()
soundprocessor = threading.Thread(target=processSound, args=(audio_stream, transcript,))
global stop
stop = False
try:
    logging.debug("initial sample")
    data = mic_stream.read(FRAMES_PER_BUFFER)
    logging.debug("staring speech processor thread")
    soundprocessor.start()
    samples = 0
    frames_buffered = 1
    while True:
        samples += 1 
        frames_buffered += 1
        data = mic_stream.read(FRAMES_PER_BUFFER)
        logging.debug("mic read {} bytes".format(len(data)))
        audio_buffer.put(data)
    logging.warning("end of data from mic stream")
except KeyboardInterrupt:
    logging.info("interrupted")
except Exception, e:
    logging.exception("Error: {}".format(str(e)))
finally:
    logging.info("ending")
    stop = True
    # Stop Recording
    mic_stream.stop_stream()
    mic_stream.close()
    audio.terminate()
    # Close the recognizer's stream
    audio_stream.close()
    logging.debug("Waiting for processor to exit")
    soundprocessor.join()
    print "Transcript %s" % ";".join(transcript.queue)
    sys.exit()
