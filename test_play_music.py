# [ref] https://stackoverflow.com/questions/20021457/playing-mp3-song-on-python

# pip install pygame

import time
from pygame import mixer  # Load the popular external library

music_file = "Mark Knopfler - A love idea.mp3"

mixer.init()
mixer.music.load(music_file)
mixer.music.play()
while mixer.music.get_busy():  # wait for music to finish playing
    time.sleep(1)