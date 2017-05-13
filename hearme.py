# Import the packages we need for reading args and files
import io
import sys

# Import the Google Cloud client library
from google.cloud import speech

# first you have to authenticate for the default application: gcloud auth application-default login

# Instantiates a speech service client
speech_client = speech.Client()

# Load the sound into memory from the file named by the first parameter
with io.open(sys.argv[1], 'rb') as audio_file:
    content = audio_file.read()

audio_sample = speech_client.sample(
    content=content,
    source_uri=None,
    encoding='LINEAR16',
    sample_rate_hertz=16000)

# Find transcriptions of the audio file
alternatives = audio_sample.recognize('en-US')
print "Found %d alternative transcripts:" % len(alternatives)
for alternative in alternatives:
    print('Transcript: {}'.format(alternative.transcript))
