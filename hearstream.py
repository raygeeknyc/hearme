# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import sys
from streamrw import StreamRW
import threading
import time

class SpeechProcessor:
    def __init__(self):
        self._stop = False

    def stop(self):
        self._stop = True

    def transcribe_streaming(self, audio_stream):
        """Streams transcription of the given audio file."""
        from google.cloud import speech
        print "Setting up recognition"
        speech_client = speech.Client()

        audio_sample = speech_client.sample(
            stream=audio_stream,
            encoding=speech.encoding.Encoding.LINEAR16,
            sample_rate_hertz=16000)
        while True:
            print "recognizing"
            alternatives = audio_sample.streaming_recognize('en-US',
                interim_results=True)

            for alternative in alternatives:
                print('Finished: {}'.format(alternative.is_final))
                print('Stability: {}'.format(alternative.stability))
                print('Confidence: {}'.format(alternative.confidence))
                if alternative.is_final: print('Transcript: {}'.format(alternative.transcript))
            if self._stop:
                break
        print "done with results"

if __name__ == '__main__':
    audio_file = io.open(sys.argv[1],'rb')
    audio_stream = StreamRW(io.BytesIO())
    speechProcessor = SpeechProcessor()
    soundthread = threading.Thread(target=speechProcessor.transcribe_streaming, args=(audio_stream,))
    soundthread.start()
    time.sleep(5)
    chunks = 0
    data = audio_file.read(256)
    while data:
        audio_stream.write(data)
        chunks += 1
        if not chunks % 10:
            audio_stream.flush()
        data=audio_file.read(256)
    audio_file.close()
    time.sleep(5)
    print "stopping"
    speechProcessor.stop()
    soundthread.join()
    audio_stream.close()
