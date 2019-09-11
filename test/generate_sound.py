from mido import Message, MidiFile, MidiTrack
import pygame

c_major = [60, 62, 64, 65, 67, 69, 71]
instrument_idx = 0
instrument_name = 'piano_note'

for pitch in c_major:
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=instrument_idx, time=0))
    track.append(Message('note_on', note=pitch, velocity=64, time=32))
    track.append(Message('note_off', note=pitch, velocity=64, time=1032))

    mid.save(instrument_name+'/'+str(pitch)+'.wav')
#    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
#    pygame.mixer.music.load('guitar_note/'+str(pitch)+'.wav')
#    pygame.mixer.music.play()
#    while pygame.mixer.music.get_busy():
#        i=1
