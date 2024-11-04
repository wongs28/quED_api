from flask import Flask, jsonify, request
import numpy as np
import requests

app = Flask(__name__)

# Fixed IP address of the device
DEVICE_IP = "http://128.95.31.28"  # Change this to your device's IP

vari = {
    'action': ['get', 'set'],
    'param': {'ild': None, 'pm1': None, 'pm2': None, 'int': None, 'cnt': None, 'mref': None}
}

if __name__ == '__main__':
    vari['param']['pm1'] = np.arange(0, 360, 0.5)
    print(vari['param']['pm1'])
    # url = f":8080/?action={action}&param={param}&value={value}"

