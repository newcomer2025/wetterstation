#!/usr/bin/env python3

import board
import busio
import adafruit_bme280.basic as adafruit_bme280

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    try:
       bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    except ValueError:
       bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)


    print(f"Temperatur: {bme280.temperature:.2f} °C")
    print(f"Feuchte:     {bme280.humidity:.2f} %")
    print(f"Druck:       {bme280.pressure:.2f} hPa")

if __name__ == "__main__":
    main()
