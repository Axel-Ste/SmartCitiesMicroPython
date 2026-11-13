
import machine
import time
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(False)

print("Début du test")

for i in range(3):
    print("Entrée en veille :", i + 1)

    start = time.ticks_ms()

    machine.lightsleep(5000)

    elapsed = time.ticks_diff(time.ticks_ms(), start)

    print("Réveil après :", elapsed, "ms")

print("Fin du test")
