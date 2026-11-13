
import network
import ntptime
import time
import machine
from machine import Pin, PWM

# ==============================
# CONFIGURATION
# ==============================

SSID = "electroProjectWifi"
PASSWORD = "B1MesureEnv"

UTC = 1  # Belgique : 1 hiver, 2 été

BUZZER_PIN = 16
SERVO_PIN = 18

STATE_DURATION = 15  # secondes

next_servo_move_time = 0

# ==============================
# INITIALISATION
# ==============================

wlan = network.WLAN(network.STA_IF)

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.freq(2000)
buzzer.duty_u16(0)

# ==============================
# BUZZER
# ==============================

def beep(duration=150, frequency=2000):
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)
    time.sleep_ms(duration)
    buzzer.duty_u16(0)


# ==============================
# WIFI
# ==============================

def connect_wifi():
    wlan.active(True)

    print("Connexion au Wi-Fi...")
    wlan.connect(SSID, PASSWORD)

    timeout = 20
    start = time.time()

    while not wlan.isconnected():
        if time.time() - start > timeout:
            wlan.active(False)
            raise RuntimeError("Wi-Fi timeout")

        time.sleep_ms(500)
        print(".", end="")

    print("\nWi-Fi connecté !")
    print("IP :", wlan.ifconfig()[0])


def disconnect_wifi():
    print("Déconnexion du Wi-Fi...")
    wlan.disconnect()
    wlan.active(False)


# ==============================
# SYNCHRONISATION NTP
# ==============================

def synchronize_time():
    try:
        ntptime.settime()
        print("Heure synchronisée !")
        return True

    except Exception as e:
        print("Erreur NTP :", e)
        return False


def get_local_time():
    return time.localtime(time.time() + UTC * 3600)


def print_time():
    t = get_local_time()

    print("{:02d}:{:02d}:{:02d}".format(
        t[3], t[4], t[5]
    ))


# ==============================
# SERVO
# ==============================

def servo_control(angle):
    angle = max(0, min(180, angle))

    pwm = PWM(Pin(SERVO_PIN))
    pwm.freq(50)

    # Impulsion entre 500 et 2500 µs
    pulse_us = 500 + (angle / 180) * 2000

    duty = int(pulse_us * 65535 / 20000)
    pwm.duty_u16(duty)

    time.sleep_ms(500)
    pwm.deinit()


def hour_on_servo():
    global next_servo_move_time

    t = get_local_time()

    # Heure convertie en minutes sur 12 heures
    minutes = (t[3] % 12) * 60 + t[4]

    # Conversion en angle
    angle = int(minutes * 180 / 720)

    servo_control(angle)

    # Prochain mouvement dans 4 minutes
    next_servo_move_time = time.time() + 240

    print("Servo positionné :", angle, "degrés")


# ==============================
# ETAT 1 : WIFI ACTIF
# ==============================

def state_wifi():
    print("\n===== ETAT 1 : WIFI ACTIF =====")

    try:
        connect_wifi()
    except Exception as e:
        print("Erreur Wi-Fi :", e)

    if wlan.isconnected():
        synchronize_time()

    start = time.time()
    last_sync = time.time()

    while time.time() - start < STATE_DURATION:

        # Synchronisation NTP toutes les 10 secondes
        if wlan.isconnected() and time.time() - last_sync >= 10:
            synchronize_time()
            last_sync = time.time()

        print_time()

        if time.time() >= next_servo_move_time:
            hour_on_servo()

        time.sleep_ms(1000)

    disconnect_wifi()
    beep()


# ==============================
# ETAT 2 : MODE AUTONOME
# ==============================

def state_autonomous():
    print("\n===== ETAT 2 : MODE AUTONOME =====")

    wlan.disconnect()
    wlan.active(False)
    wlan.deinit()


    start = time.time()

    while time.time() - start < STATE_DURATION:

        print_time()

        if time.time() >= next_servo_move_time:
            hour_on_servo()

        time.sleep_ms(1000)

    beep()


# ==============================
# ETAT 3 : LIGHT SLEEP
# ==============================

def state_light_sleep():
    print("\n===== ETAT 3 : LIGHT SLEEP =====")

    wlan.active(False)
    buzzer.duty_u16(0)

    # Veille légère de 30 secondes
    machine.lightsleep(STATE_DURATION * 1000)

    print("Réveil du Light Sleep")
    beep()


# ==============================
# ETAT 4 : DEEP SLEEP
# ==============================

def state_deep_sleep():
    print("\n===== ETAT 4 : DEEP SLEEP =====")

    wlan.active(False)
    buzzer.duty_u16(0)

    # Signal sonore avant la veille
    beep()

    print("Entrée en Deep Sleep pour 15 secondes...")

    # Sur RP2040, cette fonction provoque
    # une veille suivie d'un redémarrage.
    machine.deepsleep(STATE_DURATION * 1000)


# ==============================
# PROGRAMME PRINCIPAL
# ==============================

print("\nDémarrage du système")

# Au réveil du Deep Sleep, le programme redémarre.
# WDT_RESET permet de détecter ce redémarrage.
if machine.reset_cause() == machine.WDT_RESET:
    print("Réveil après Deep Sleep")
    beep()

while True:

    # ETAT 1
    state_wifi()

    # ETAT 2
    state_autonomous()

    # ETAT 3
    state_light_sleep()

    # ETAT 4
    state_deep_sleep()

    # Le programme reprend au démarrage
    # après le Deep Sleep.
