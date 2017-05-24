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
    audio_stream = io.BytesIO()
    buf = io.BufferedRandom(audio_stream)
    from google.cloud import speech
    speech_client = speech.Client()

    audio_sample = speech_client.sample(
        stream=audio_stream,
        encoding=speech.encoding.Encoding.LINEAR16,
        sample_rate_hertz=16000)
    alternatives = audio_sample.streaming_recognize('en-US')

    while not input.stream.EOF:
        data = input.stream.read()
        audio.stream.write(data)
        for alternative in alternatives:
            print('Finished: {}'.format(alternative.is_final))
            print('Stability: {}'.format(alternative.stability))
            print('Confidence: {}'.format(alternative.confidence))
            print('Transcript: {}'.format(alternative.transcript))

if __name__ == '__main__':
    transcribe_streaming(sys.stdin)
