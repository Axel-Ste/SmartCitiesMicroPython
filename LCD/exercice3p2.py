from machine import I2C, Pin
from lcd1602 import LCD1602
from utime import sleep

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)

lcd = LCD1602(i2c, 2, 16, 0x3e)

lcd.display()
sleep(1)

lcd.clear()

# Affichage
lcd.setCursor(0, 0)
lcd.print("Hello")

lcd.setCursor(0, 1)
lcd.print("World !")

print("Affichage terminé")

while True:
    pass