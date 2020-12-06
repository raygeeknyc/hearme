#!/opt/local/bin/python3
#####
# Raymond Blum <raygeeknyc@gmail.com>
# Licensed under GNU-GPL-3.0-or-later
#####
import sys
import logging
import simpleaudio
import numpy as np
import matplotlib.pyplot as plt
import librosa
import soundfile
import audioop
import librosa.display

logging.getLogger('').setLevel(logging.INFO)

def play_audio_file(audio_filename):
    logging.info('playing %s', audio_filename)   

    wave_obj = simpleaudio.WaveObject.from_wave_file(audio_filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing
    logging.info('EOF %s', audio_filename)   

def main(audio_filename):
    source_audio, sr = librosa.load(audio_filename)
    # compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(source_audio))
    
    S_filter = librosa.decompose.nn_filter(S_full,
                                           aggregate=np.median,
                                           metric='cosine',
                                           width=int(librosa.time_to_frames(2, sr=sr)))
    S_filter = np.minimum(S_full, S_filter)

    power = 2
    margin_i, margin_v = 2, 10
    mask_i = librosa.util.softmask(S_filter,
                                   margin_i * (S_full - S_filter),
                                   power=power)
    mask_v = librosa.util.softmask(S_full - S_filter,
                                   margin_v * S_filter,
                                   power=power)
    S_foreground = mask_v * S_full
    S_background = mask_i * S_full
    
    plt.figure(figsize=(12, 8))
    plt.subplot(3, 1, 1)
    full = librosa.amplitude_to_db(S_full, ref=np.max)
    librosa.display.specshow(full, y_axis='log', sr=sr)
    plt.title('Full spectrum')
    plt.colorbar()
    
    plt.subplot(3, 1, 2)
    background = librosa.amplitude_to_db(S_background, ref=np.max)
    librosa.display.specshow(background, y_axis='log', sr=sr)
    plt.title('Background')
    plt.colorbar()
    
    plt.subplot(3, 1, 3)
    foreground = librosa.amplitude_to_db(S_foreground, ref=np.max)
    librosa.display.specshow(foreground, y_axis='log', x_axis='time', sr=sr)
    plt.title('Foreground')
    plt.colorbar()
    
    plt.tight_layout()
    plt.ion()
    plt.show()
    plt.draw()
    plt.pause(.001)
    
    full_audio = librosa.istft(S_full)
    
    foreground_audio = librosa.istft(S_foreground)
    background_audio = librosa.istft(S_background)
    
    logging.debug("sr: {}".format(sr))
    logging.debug("orig({}) max {} power {}: {}".format(len(source_audio), audioop.max(source_audio,2), audioop.rms(source_audio,2), source_audio))
    logging.debug("full({}) max {} power {}: {}".format(len(full_audio), audioop.max(background_audio,2), audioop.rms(full_audio,2), full_audio))
    logging.debug("foreground({}) max {} power {}: {}".format(len(foreground_audio), audioop.max(background_audio,2), audioop.rms(foreground_audio,2), foreground_audio))
    logging.debug("background({}) max {} power {}: {}".format(len(background_audio), audioop.max(background_audio,2), audioop.rms(background_audio,2), background_audio))
    
    soundfile.write('full.WAV', full_audio, sr)
    play_audio_file('full.WAV')
    soundfile.write('fg.WAV', foreground_audio, sr)
    play_audio_file('fg.WAV')
    soundfile.write('bg.WAV', background_audio, sr)
    play_audio_file('bg.WAV')

if __name__=="__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
        sys.exit(0)
    else:
        logging.error('%s audio_file', sys.argv[0])
        sys.exit(255)
