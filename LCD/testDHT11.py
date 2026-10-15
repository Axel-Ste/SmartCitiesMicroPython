import dht
from machine import Pin
from time import sleep

for gpio in [16, 18, 20, 21, 22]:
    print("\nTest GPIO", gpio)

    try:
        capteur = dht.DHT11(Pin(gpio))
        capteur.measure()

        print("T =", capteur.temperature())
        print("H =", capteur.humidity())

    except Exception as e:
        print(e)

    sleep(2)