import pygame
import random

pygame.init()

sounds = {
    "winner":   [pygame.mixer.Sound("src/assets/sounds/freecow_winner.wav"),
                  pygame.mixer.Sound("src/assets/sounds/pvz_winner.mp3"),
                  pygame.mixer.Sound("src/assets/sounds/yeah_boy_winner.mp3"),
                  pygame.mixer.Sound("src/assets/sounds/you_winner.mp3")],
    "loser":    [pygame.mixer.Sound("src/assets/sounds/bruh_loser.mp3"),
                 pygame.mixer.Sound("src/assets/sounds/gta_loser.mp3"),
                 pygame.mixer.Sound("src/assets/sounds/haha_loser.mp3"),
                 pygame.mixer.Sound("src/assets/sounds/minecraft_loser.mp3")],
    "countdown":[pygame.mixer.Sound("src/assets/sounds/countdown.mp3")],
    "counter":  [pygame.mixer.Sound("src/assets/sounds/counter.mp3")]
}

def stop_all_sounds():
    for sound_list in sounds.values():
        for sound in sound_list:
            sound.stop()

def play_sound(sound_name):
    stop_all_sounds()
    sound_list = sounds.get(sound_name)
    if sound_list:
        random_sound = random.choice(sound_list)
        random_sound.play()
    else:
        print(f"No sound found for {sound_name}")