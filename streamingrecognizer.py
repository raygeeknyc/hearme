#!/opt/local/bin/python3
#####
# Raymond Blum <raygeeknyc@gmail.com>
# Licensed under GNU-GPL-3.0-or-later
#####


import logging
import simpleaudio
import sys


def transcribe_streaming(stream_file):
    """Streams transcription of the given audio file."""
    import io
    from google.cloud import speech

    client = speech.SpeechClient()

    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    for response in responses:
        for result in response.results:
          if result.is_final:
            for alternative in result.alternatives:
              print("Speech: {}".format(alternative.transcript))


def main(audio_filename):
    transcribe_streaming(audio_filename)
    wave_obj = simpleaudio.WaveObject.from_wave_file(audio_filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing


logging.getLogger().setLevel(logging.INFO)
if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.fatal("%s audio_filename", sys.argv[0])
        sys.exit(-1)
    main(sys.argv[1])
