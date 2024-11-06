from flask import Flask, jsonify, request
import numpy as np
import requests
import time

# app = Flask(__name__)

# Fixed IP address of the device
DEVICE_IP = "http://128.95.31.28"  # Change this to your device's IP

vari = {
    'action': ['get', 'set'],
    'param': {'ild': None, 'pm1': None, 'pm2': None, 'int': None, 'cnt': None, 'mref': None}
}


def build_url(action, param, value=None):
    if value is None:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}'
    else:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}&value={value}'


if __name__ == '__main__':
    try:
        for angle in [22.5, 67.5, 112.5, 157.5]:
            response = requests.post(build_url('set', 'pm1', angle))
            time.sleep(3)
            if response.status_code == 200:
                print(response.text)
            else:
                print(response.status_code)
    except requests.exceptions.RequestException as e:
        print(e)
