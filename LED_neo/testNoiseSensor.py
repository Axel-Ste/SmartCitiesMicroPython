from machine import Pin, ADC
from ws2812 import WS2812
from utime import sleep_ms, ticks_ms, ticks_diff

led = WS2812(Pin(20), 1)
sound = ADC(1)

COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 255)
]

# Calibration de l'offset
offset = 0
for i in range(500):
    offset += sound.read_u16()
    sleep_ms(1)

offset //= 500

print("Offset ADC =", offset)

# Paramètres
SEUIL = 3000          # à ajuster
BPM = 120

last_peak = 0
last_color_change = 0
current_color_index = 0

while True:

    # Lecture du micro
    sample = sound.read_u16()

    # Niveau sonore sans composante continue
    amplitude = abs(sample - offset)

    now = ticks_ms()

    # Détection d'un pic sonore
    if amplitude > SEUIL:

        # Ignore les pics trop rapprochés
        if ticks_diff(now, last_peak) > 300:

            interval = ticks_diff(now, last_peak)

            if last_peak != 0:

                bpm = 60000 / interval

                # filtre BPM aberrants
                if 50 <= bpm <= 220:
                    BPM = int(bpm)
                    print("BPM =", BPM)

            last_peak = now

    # Animation LED synchronisée BPM
    periode = 60000 / BPM

    if ticks_diff(now, last_color_change) >= periode:
        current_color_index = (current_color_index + 1) % len(COLORS)
        led.pixels_fill(COLORS[current_color_index])
        led.pixels_show()
        last_color_change = now

    sleep_ms(2)

    print(amplitude)