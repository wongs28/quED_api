from bs4 import BeautifulSoup
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy.interpolate import CubicSpline
import time


# Fixed IP address of the device
DEVICE_IP = "http://128.95.31.28"


def build_url(action, param, value=None):
    if value is None:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}'
    else:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}&value={value}'


def set_zero(pm):
    return requests.post(build_url('set', pm, 0))


def get_param(param):
    return requests.get(build_url('get', param))


def set_param(param, value):
    return requests.post(build_url('set', param, value))


def check(response):
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code)


def find_string(response, search_string):
    soup = BeautifulSoup(response.text, 'html.parser')
    for br_tag in soup.find_all('br'):
        previous_sibling = br_tag.find_previous_sibling(string=True)
        if previous_sibling and search_string in previous_sibling:
            return previous_sibling.strip()


def polarization_correlation(pm1_angles, pm2_angles):
    cnt_rates = [[] for _ in range(len(pm1_angles))]
    i = 0
    try:
        set_zero('pm1')
        time.sleep(1.0)
        set_zero('pm2')
        time.sleep(1.0)
        for pm1 in pm1_angles:
            set_pm1 = set_param('pm1', pm1)
            time.sleep(1.0)
            check(set_pm1)

            for pm2 in pm2_angles:
                set_pm2 = set_param('pm2', pm2)
                check(set_pm2)
                time.sleep(1.0)
                cnt = get_param('cnt')
                check(cnt)
                cnt_rates[i].append(float(find_string(cnt, '01:')[4:]))
            i = i + 1
    except requests.exceptions.RequestException as e:
        print(e)

    return cnt_rates


def calculate_E(a, a_perp, b, b_perp):
    norm = a(b) + a(b_perp) + a_perp(b) + a_perp(b_perp)
    return (a(b) - a(b_perp) - a_perp(b) + a_perp(b_perp)) / norm


def calculate_S(h_counts, n_counts, v_counts, p_counts, b, bp, perp):
    E_ab = calculate_E(h_counts, v_counts, b, b+perp)
    E_abp = calculate_E(h_counts, v_counts, bp, bp+perp)
    E_apb = calculate_E(p_counts, n_counts, b, b+perp)
    E_apbp = calculate_E(p_counts, n_counts, bp, bp+perp)
    S1 = -E_ab + E_abp + E_apb + E_apbp
    S2 = E_ab - E_abp + E_apb + E_apbp
    S3 = E_ab + E_abp - E_apb + E_apbp
    S4 = E_ab + E_abp + E_apb - E_apbp
    return S1, S2, S3, S4


def plot_curves(ax, x_data, y_data):
    ax.plot(x_data, y_data)
    ax.set_title('Polarization Correlation Curve')
    ax.set_xlabel('Polarizer 2 Angle')
    ax.set_ylabel('Coincidence Count Rate [/1000ms]')
    ax.grid(True)
    ax.legend(['H', '-45', 'V', '+45'], title="Polarizer 1 Angle")


if __name__ == '__main__':
    splines = []
    pol1_angles = [0, -45, 90, 45]
    pol2_angles = np.linspace(0, 360, 17)
    all_counts = polarization_correlation(pol1_angles, pol2_angles)
    fig1, ax1 = plt.subplots(1, 1)
    fig2, ax2 = plt.subplots(1, 1)

    for data in all_counts:
        plot_curves(ax1, pol2_angles, data)
        x_new = np.arange(0, 360, 0.5)
        f_new = CubicSpline(pol2_angles, data)
        plot_curves(ax2, x_new, f_new(x_new))

    all_data = np.array(pol2_angles, all_counts)
    with open('coin_data.csv', mode='w', newline='') as file:
        coin_data = csv.writer(file)
        coin_data.writerows(all_data)

    plt.show()
