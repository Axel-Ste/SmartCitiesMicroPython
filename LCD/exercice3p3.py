from machine import Pin, ADC, I2C, PWM
from lcd1602 import LCD1602
import dht
from utime import sleep_ms, ticks_ms
import math


pot = ADC(26)

led = PWM(Pin(20))
led.freq(5000)

dht = dht.DHT11(Pin(18))

buzzer = PWM(Pin(16))
buzzer.freq(1000)

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)
lcd = LCD1602(i2c, 2, 16, 0x3e)

# =========================
# Paramètres
# =========================

NORMAL = 0
HOT = 1
ALARM = 2

etat = NORMAL

last_temp_read = 0
temperature = 0

alarm_visible = True
last_alarm_toggle = 0

# =========================
# Fonctions
# =========================

def lire_consigne():
    """
    Convertit ADC 0..65535
    vers 15..35°C
    """
    raw = pot.read_u16()

    temp_set = 15 + (raw / 65535) * 20

    return round(temp_set, 1)


def lire_temperature():
    global temperature
    global dht

    try:
        dht.measure()
        temperature = dht.temperature()
        print("Température lue : {:.1f}C".format(temperature))
    except:
        pass

    return temperature


def effet_battement(freq_hz):
    """
    PWM type respiration
    """

    t = ticks_ms() / 1000

    niveau = (math.sin(2 * math.pi * freq_hz * t) + 1) / 2

    led.duty_u16(int(niveau * 65535))


def afficher(consigne, temp, etat):
    global alarm_visible

    lcd.clear()

    lcd.setCursor(0, 0)
    lcd.print("Set:{:.1f}C".format(consigne))

    if etat == ALARM:

        lcd.setCursor(0, 1)

        if alarm_visible:
            lcd.print("ALARM {:.1f}C".format(temp))
        else:
            lcd.print("Ambient:{:.1f}".format(temp))

    else:

        lcd.setCursor(0, 1)
        lcd.print("Ambient:{:.1f}".format(temp))


# =========================
# Boucle principale
# =========================

while True:

    consigne = lire_consigne()

    # Lecture température chaque seconde
    if ticks_ms() - last_temp_read > 1000:
        lire_temperature()
        last_temp_read = ticks_ms()

    # Machine à états

    if temperature >= consigne + 3:
        etat = ALARM

    elif temperature > consigne:
        etat = HOT

    else:
        etat = NORMAL

    # Actions par état

    if etat == NORMAL:

        led.duty_u16(0)
        buzzer.duty_u16(0)

    elif etat == HOT:

        buzzer.duty_u16(1000)

        # battement lent 0.5 Hz
        effet_battement(0.5)

    elif etat == ALARM:

        buzzer.duty_u16(32768)  # 50% duty cycle

        # battement rapide
        effet_battement(2)

        # clignotement du texte ALARM
        if ticks_ms() - last_alarm_toggle > 500:
            alarm_visible = not alarm_visible
            last_alarm_toggle = ticks_ms()

    afficher(consigne, temperature, etat)

    sleep_ms(50)