from machine import Pin
from utime import sleep

led = Pin(16, Pin.OUT)
button = Pin(18, Pin.IN)
counter = 0
blink_enable = False
blink_speed = 0.5

def run_transition_effect(self):
    global blink_enable
    global blink_speed

    print("Transition effect...")

    old_blink_enable = blink_enable
    old_blink_speed = blink_speed

    blink_enable = True
    blink_speed = 0.1
    sleep(2)
    blink_enable = old_blink_enable
    blink_speed = old_blink_speed

    print("Transition effect finished.")


def handle_button_press(self):
    global counter
    global blink_enable
    global blink_speed

    # Gestion du compteur pour changer l'état de clignotement
    counter += 1
    if counter > 2:
        counter = 0
    print("Blink state : ", counter)

    # Gestion des différents états de clignotement en fonction du compteur
    if counter == 0:
        blink_enable = False
    elif counter == 1:
        blink_enable = True
        blink_speed = 0.5
    elif counter == 2:
        blink_enable = True
        blink_speed = 0.1
    else:
        print("Error: Invalid state")

    run_transition_effect(self)  # Anti-rebond pour éviter les multiples déclenchements

# Enregistrement de l'interruption sur le bouton pour détecter les appuis
button.irq(trigger=Pin.IRQ_RISING, handler=handle_button_press)

led.value(0) # Led éteinte au démarrage

# Boucle principale pour gérer le clignotement de la LED
while True:
    if (blink_enable):
        led.toggle()
        sleep(blink_speed)
    else:
        led.value(0)





