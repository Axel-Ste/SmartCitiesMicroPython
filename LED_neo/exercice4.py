from machine import Pin, ADC, I2C, PWM
from ws2812 import WS2812
from utime import sleep, ticks_ms

led = WS2812(Pin(20), 1)

sound = ADC(1)

COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 255) # White
]

current_color_index = 0

current_BPM = 120

last_beat_time = 0

current_audio_sample = 0
audio_data = []

def calculer_bpm_basique(liste_audio, sr):
    # Calcul de l'énergie locale par blocs
    taille_bloc = 1024
    energies = []
    
    for i in range(0, len(liste_audio), taille_bloc):
        bloc = liste_audio[i:i+taille_bloc]
        energie = sum(sample ** 2 for sample in bloc)
        energies.append(energie)
    
    # Seuil basique pour détecter un "battement"
    seuil = sum(energies) / len(energies) * 1.5
    battements = sum(1 for e in energies if e > seuil)
    
    duree_secondes = len(liste_audio) / sr
    bpm = (battements / duree_secondes) * 60
    return bpm

while True:

    noise = sound.read_u16()
    
    # Récolte 100 échantillons
    audio_data.append(sound.read_u16())
    current_audio_sample += 1

    # Calcul du BPM toutes les 2 secondes
    if current_audio_sample >= 1000:  # Assuming 1000 samples for 2 seconds at 500 Hz
        current_BPM = calculer_bpm_basique(audio_data, 1000)  # Assuming 44.1 kHz sampling rate
        current_audio_sample = 0  # Reset the sample counter
        audio_data = []  # Clear the audio data list
        print("Current BPM:", current_BPM)
        sleep(0.1)  # Small delay to avoid overwhelming the output



    # Choix de la couleur aléatoire en fonction BPM

    if last_beat_time == 0 or (current_BPM > 0 and (ticks_ms() - last_beat_time) >= (60000 / current_BPM)):
        last_beat_time = ticks_ms()
        current_color_index = (current_color_index + 1) % len(COLORS)


    led.pixels_fill(COLORS[current_color_index])
    led.pixels_show()

    sleep(0.002) # Framerate of 500 Hz
