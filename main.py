import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy.interpolate import CubicSpline
import time


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


def set_zero(pm):
    return requests.post(build_url('set', pm, 0))


def check(response):
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code)


def polarization_correlation():
    cnt_rates = [[] for _ in range(4)]
    i = 0
    try:
        set_zero('pm1')
        set_zero('pm2')
        for pm1 in [0, -45, 90, 45]:
            set_pm1 = requests.post(build_url('set', 'pm1', pm1))
            time.sleep(0.1)
            check(set_pm1)

            for pm2 in np.arange(0, 360, 10):
                set_pm2 = requests.post(build_url('set', 'pm2', pm2))
                time.sleep(0.1)
                check(set_pm2)
                cnt = requests.get(build_url('get', 'cnt'))
                time.sleep(0.1)
                check(cnt)
                # append count rate to list
            i = i + 1
    except requests.exceptions.RequestException as e:
        print(e)

    return cnt_rates


def calculate_E(a, a_perp, b, b_perp):
    norm = a(b) + a(b_perp) + a_perp(b) + a_perp(b_perp)
    return (a(b) - a(b_perp) - a_perp(b) + a_perp(b_perp)) / norm


def calculate_S(h_counts, n_counts, v_counts, p_counts):
    E_ab = calculate_E(h_counts, v_counts, 22.5, -67.5)
    E_abp = calculate_E(h_counts, v_counts, 67.5, -22.5)
    E_apb = calculate_E(p_counts, n_counts, 22.5, -67.5)
    E_apbp = calculate_E(p_counts, n_counts, 67.5, -22.5)
    return E_ab + E_abp - E_apb + E_apbp


def plot_curves(x_data, y_data):
    fig, ax = plt.subplots(1, 1)
    ax.plot(x_data, y_data)
    ax.set_title('Polarization Correlation Curve')
    ax.set_xlabel('Polarizer 2 Angle')
    ax.set_ylabel('Coincidence Count Rate [/1000ms]')
    ax.grid(True)
    ax.legend(['H', '-45', 'V', '+45'], title="Polarizer 1 Angle")


if __name__ == '__main__':
    all_counts = polarization_correlation()
    interp = []
    for data in all_counts:
        x = np.arange(0, 360, 10)
        plot_curves(x, data)
        interp.append(CubicSpline(x, data))
        plot_curves(x, CubicSpline(x, data))

    S = calculate_S(interp[0], interp[1], interp[2], interp[3])
    print(S)
    plt.show()

