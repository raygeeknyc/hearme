#
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

def transcribe_streaming(input_stream):
    """Streams transcription of the given audio file."""
    from google.cloud import speech
    buf = StreamRW()
    speech_client = speech.Client()

    audio_sample = speech_client.sample(
        stream=buf,
        encoding=speech.encoding.Encoding.LINEAR16,
        sample_rate_hertz=16000)
    alternatives = audio_sample.streaming_recognize('en-US',
        interim_results=True)

    while True:
        print "reading chunk"
        data=input_stream.read(512)
        if not data: break
        print "writing data %d" % len(data)
        buf.write(data)
 
    print "done reading"
    buf.flush()
    for alternative in alternatives:
        print('Finished: {}'.format(alternative.is_final))
        print('Stability: {}'.format(alternative.stability))
        print('Confidence: {}'.format(alternative.confidence))
        print('Transcript: {}'.format(alternative.transcript))
    print "done with results"

if __name__ == '__main__':
    transcribe_streaming(sys.stdin)
