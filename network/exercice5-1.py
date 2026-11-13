
import network
import ntptime
import time
from machine import Pin, ADC, I2C, PWM

# Configuration Wi-Fi
SSID = "electroProjectWifi"
PASSWORD = "B1MesureEnv"

UTC = 1  # Décalage horaire pour la Belgique (UTC+1 en hiver, UTC+2 en été)

next_servo_move_time = 0  # Variable globale pour stocker le temps du prochain mouvement du servo

wlan = network.WLAN(network.STA_IF)

def connect_wifi(ssid, password):
    global wlan
    wlan.active(True)

    print("Connexion au Wi-Fi...")

    wlan.connect(SSID, PASSWORD)

    # Attente de connexion
    timeout = 20
    start = time.time()

    while not wlan.isconnected():
        if time.time() - start > timeout:
            print("Erreur : connexion Wi-Fi impossible")
            raise RuntimeError("Wi-Fi timeout")

        time.sleep(0.5)
        print(".", end="")

    print("\nConnecté au Wi-Fi !")
    print("Adresse IP :", wlan.ifconfig()[0])

def synchronize_time():
    print("Synchronisation de l'heure via NTP...")
    try:
        ntptime.settime()
        print("Heure synchronisée !")
    except Exception as e:
        print("Erreur NTP :", e)
        raise

def servo_control(pin_number, angle):
    pwm = PWM(Pin(pin_number))
    pwm.freq(50)  # Fréquence pour les servos
    duty = int((angle / 180) * 1023)  # Conversion de l'angle en rapport cyclique
    pwm.duty_u16(duty)
    time.sleep(0.5)  # Temps pour que le servo atteigne la position
    pwm.deinit()  # Désactivation du PWM après le mouvement

def hour_on_servo():
    # Le servo n'a que 180 pas donc on divise par 12 
    # Récupération de l'heure locale
    t = time.localtime()

    # Conversion de l'heure en minutes pour le servo (0-180 degrés)
    minutes = (t[3] + UTC) * 60 + t[4]  # Total minutes in the day

    # Calcul du nombre du nombre de minutes par pas pour le servo (0-180 degrés) sur 12 heures
    minutes_par_pas = (12 * 60) / 180  # 720 minutes / 180 pas = 4 minutes par pas

    # Conversion des minutes en angle pour le servo (0-180 degrés) sur 12 heures
    angle = angle = int(minutes * 180 / (12 * 60))  # Mapping from 0-720 minutes to 0-180 degrees

    
    # Planifier le prochain mouvement du servo après une période définie
    global next_servo_move_time
    next_servo_move_time = time.time() + minutes_par_pas * 60  # Convertir minutes en secondes

    # Contrôle du servo sur le pin 18
    servo_control(18, angle)

    print("Servo mis à l'heure")



# Affichage de l'heure
while True:
    # Vérification de la connexion Wi-Fi et synchronisation de l'heure
    if not wlan.isconnected():
        connect_wifi(SSID, PASSWORD)
        synchronize_time()
    
    # Récupération de l'heure UTC
    t = time.localtime()

    print("{:02d}:{:02d}:{:02d}".format(
        t[3] + UTC, # Correction de l'heure en fonction du décalage UTC
        t[4],
        t[5]
    ))

    # Si il est temps de bouger le servo, on appelle la fonction hour_on_servo
    if time.time() >= next_servo_move_time:
        hour_on_servo()

    # Attentre la seconde suivante
    actual_time = time.time()
    while time.time() - actual_time < 1:
        pass
