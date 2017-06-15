import Queue
import time
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
FRAMES_PER_BUFFER = 4096
SILENCE_THRESHOLD = 500
PAUSE_LENGTH_SECS = 0.7
PAUSE_LENGTH_IN_SAMPLES = int((PAUSE_LENGTH_SECS * RATE / FRAMES_PER_BUFFER) + 0.5)
 
def processSound(audio_stream, transcript):
    global stop
    while not stop:
        try:
            recognize_stream = None
            # Google RPC Call for StreamingRecognize
            with cloud_speech.beta_create_Speech_stub(make_channel('speech.googleapis.com', 443)) as service:
                request = self.request_stream()
                recognize_stream = service.StreamingRecognize(request, DEADLINE_SECS)
                self.listen_print_loop(recognize_stream)

        except AbortionError as e:
            self.logger.info("AbortionError: " + str(e))
        except CancellationError as e:
            self.logger.info("CancellationError: " + str(e))
        finally:
            if self.last_not_final:
                self.send_event(json.dumps(self.last_not_final))

    self.logger.info("RPC Thread stopped")
    self.send_event(json.dumps({"status": "stop"}))

logging.getLogger().setLevel(logging.DEBUG)

logging.debug("initializing pyaudio")
audio = pyaudio.PyAudio()
 
logging.debug("opening audio")
# Start Recording
logging.info("capturing from mic")
stream = audio.open(format=FORMAT, channels=CHANNELS,
             rate=RATE, input=True,
             frames_per_buffer=FRAMES_PER_BUFFER)

audio_stream = StreamRW(io.BytesIO())
transcript = Queue.Queue()
soundprocessor = threading.Thread(target=processSound, args=(audio_stream,transcript,))
global stop
stop = False
soundprocessor.start()
try:
    logging.debug("initial sample, waiting for sound")
    consecutive_silent_samples = 0
    volume = 0
    # Wait for sound
    while volume <= SILENCE_THRESHOLD:
        data = stream.read(FRAMES_PER_BUFFER)
        if not data:
            break
        data = array('h', data)
        volume = max(data)
    logging.debug("sound heard")
    w = audio_stream.write(data)
    audio_stream.flush()
    samples = 0
    while True:
        samples += 1 
        data = stream.read(FRAMES_PER_BUFFER)
        if not data:
            logging.debug("no audio data")
            break
        data = array('h', data)
        volume = max(data)
        if volume <= SILENCE_THRESHOLD:
            consecutive_silent_samples += 1
        else:
            if consecutive_silent_samples >= PAUSE_LENGTH_IN_SAMPLES:
                logging.debug("pause ended {}".format(samples))
            consecutive_silent_samples = 0
        w = audio_stream.write(data)
        audio_stream.flush()
        if consecutive_silent_samples == PAUSE_LENGTH_IN_SAMPLES:
            logging.debug("pause detected {}".format(samples))
except KeyboardInterrupt:
    logging.info("interrupted")
finally:
    logging.info("ending")
    stop = True
    logging.debug("Waiting for processor to exit")
    soundprocessor.join()
    # Close the recognizer's stream
    audio_stream.close()
    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print "Transcript %s" % ";".join(transcript.queue)
    sys.exit()
