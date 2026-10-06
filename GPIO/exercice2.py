from machine import Pin, PWM, ADC
from utime import sleep

# Buzzer
buzzer = PWM(Pin(27))

# Potentiomètre
pot = ADC(26)

# Liste des notes avec leurs fréquences correspondantes
notes = {
    "DO": 1046,
    "RE": 1175,
    "MI": 1318,
    "FA": 1397,
    "SOL": 1568,
    "SI": 1967
}

# Mélodie à jouer et leurs durées respectives (en secondes)
melody = [
    ("SOL", 0.5),
    ("SOL", 0.5),
    ("SOL", 0.5),
    ("RE", 0.35),
    ("SI", 0.15),
    ("SOL", 0.5),
    ("RE", 0.35),
    ("SI", 0.15),
    ("SOL", 1.0),
    ("RE", 0.5),
    ("RE", 0.5),
    ("RE", 0.5),
    ("MI", 0.35),
    ("SI", 0.15),
    ("FA", 0.5),
    ("RE", 0.35),
    ("SI", 0.15),
    ("SOL", 1.0),
]

def get_volume(): # Gestion du volume en fonction de la position du potentiomètre + Correction pour la perception humaine du son
    value = pot.read_u16()

    x = value / 65535
    # Correction gamma
    gamma = 2.2
    x = x ** gamma

    return int(x * 30000)

def play_note(freq, duration): # Jouer une note avec une fréquence et une durée données + prise en compte du volume
    buzzer.freq(freq)

    step = 0.01
    loops = int(duration / step)

    for _ in range(loops):
        buzzer.duty_u16(get_volume()) # Vérification du volume à chaque pas
        sleep(step)

    buzzer.duty_u16(0)
    sleep(0.05)


# Boucle principale pour jouer la mélodie en continu
while True:
    for note, duration in melody:
        play_note(notes[note], duration)

    sleep(1)