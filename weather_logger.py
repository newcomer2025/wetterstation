#!/usr/bin/env python3
import time
import csv
import os
from datetime import datetime

import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

BASE_DIR = "/home/genie/wetterstation"
CSV_FILE = os.path.join(BASE_DIR, "wetterdaten.csv")
INTERVAL = 900  # 15 Minuten, 60 ist hier  1 Minute


def init_csv():
    os.makedirs(BASE_DIR, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["Datum", "Zeit", "Temperatur_C", "Feuchte_%", "Druck_hPa"])
            f.flush()
            os.fsync(f.fileno())


def init_sensor():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        try:
            return adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        except ValueError:
            return adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)
    except Exception as e:
        print(f"Sensor-Initialisierung fehlgeschlagen: {e}")
        exit(1)


def log_once(sensor):
    try:
        now = datetime.now()
        row = [
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            round(sensor.temperature, 2),
            round(sensor.humidity, 2),
            round(sensor.pressure, 2),
        ]
        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Logger-Fehler: {e}")


if __name__ == "__main__":
    sensor = init_sensor()
    init_csv()

    while True:
        log_once(sensor)
        time.sleep(INTERVAL)
