from machine import Pin, ADC, PWM
from utime import sleep

# Potentiomètre sur A0 (GPIO26)
pot = ADC(26)

# LED sur D16
led = PWM(Pin(16))
led.freq(500)  # fréquence PWM 1 kHz

while True:
    valeur = pot.read_u16()

    led.duty_u16(valeur)

    print("Potentiomètre :", valeur)

    sleep(0.01)