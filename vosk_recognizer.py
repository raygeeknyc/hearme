#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import simpleaudio
import json
import logging

MODEL_PATH="./vosk-model"

SetLogLevel(-1)

def play_audio_file(audio_filename):
    wave_obj = simpleaudio.WaveObject.from_wave_file(audio_filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing

if not os.path.exists(MODEL_PATH):
    logging.error("Please download the model from https://github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as '%s' in the current folder.", MODEL_PATH)
    sys.exit(1)

def main(audio_filename):
    wf = wave.open(audio_filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        logging.error("Audio file must be WAV format mono PCM.")
        sys.exit(1)
    
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print (res['text'])
    
    res = json.loads(rec.FinalResult())
    print (res['text'])
    play_audio_file(audio_filename)
    
if __name__=="__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
        sys.exit(0)
    else:
        logging.error('%s audio_file', sys.argv[0])
        sys.exit(255)
