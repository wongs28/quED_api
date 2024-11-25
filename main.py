from bs4 import BeautifulSoup
import csv
import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy.interpolate import CubicSpline
import time


# Fixed IP address of the device
DEVICE_IP = "http://128.95.31.28"


def build_url(action, param, value=None):
    """
    This function builds the specific url to send in an http request.

    :param action: str
    :param param: str
    :param value: int or float
    :return: str
    """
    if value is None:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}'
    else:
        return f'{DEVICE_IP}:8080/?action={action}&param={param}&value={value}'


def set_zero(pm):
    """
    This function sends a POST request to set a polarizer position to zero.

    :param pm: str
    :return: http request
    """
    return requests.post(build_url('set', pm, 0))


def get_param(param):
    """
    This function sends a GET request.

    :param param: str
    :return: http request
    """
    return requests.get(build_url('get', param))


def set_param(param, value):
    """
    This function sends a POST request.

    :param param:
    :param value:
    :return: http request
    """
    return requests.post(build_url('set', param, value))


def check(response):
    """
    This function checks if an http request was successful.

    :param response: http request
    :return: raw html
    """
    if response.status_code == 200:
        print(response.text)
    else:
        print(response.status_code)


def find_string(response, search_string):
    """
    This function searches for a specific string in html data by looping through line breaks.

    :param response: http request
    :param search_string: str
    :return: str
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    for br_tag in soup.find_all('br'):
        previous_sibling = br_tag.find_previous_sibling(string=True)
        if previous_sibling and search_string in previous_sibling:
            return previous_sibling.strip()


def polarization_correlation(pm1_angles, pm2_angles):
    """
    This function moves polarizers and measures coincident count rates to collect data for a polarization correation curve.

    :param pm1_angles: list of polarizer 1 angles
    :param pm2_angles: list of polarizer 2 angles
    :return: 2D list coincidence count rates
    """
    cnt_rates = [[] for _ in range(len(pm1_angles))]
    i = 0
    try:
        # set both polarizers to zero
        set_zero('pm1')
        time.sleep(1.0)
        set_zero('pm2')
        time.sleep(1.0)
        for pm1 in pm1_angles:
            # set polarizer 1
            set_pm1 = set_param('pm1', pm1)
            time.sleep(1.0)
            check(set_pm1)

            for pm2 in pm2_angles:
                # set polarizer 2
                set_pm2 = set_param('pm2', pm2)
                check(set_pm2)
                time.sleep(1.0)
                # get count rates
                cnt = get_param('cnt')
                check(cnt)
                # find coincidence count in html data
                cnt_rates[i].append(float(find_string(cnt, '01:')[4:]))
            i = i + 1
    except requests.exceptions.RequestException as e:
        print(e)

    return cnt_rates


def plot_curves(ax, x_data, y_data, labels):
    """
    This function plots a polarization correlation curve
    :param ax: ax.subplot()
    :param x_data: polarizer 2 angles
    :param y_data: coincident count rates
    :param labels: polarizer 1 angles
    :return: None
    """
    ax.plot(x_data, y_data)
    ax.set_title('Polarization Correlation Curve')
    ax.set_xlabel('Polarizer 2 Angle')
    ax.set_ylabel('Coincidence Count Rate [/1000ms]')
    ax.grid(True)
    ax.legend(labels, title="Polarizer 1 Angle")


if __name__ == '__main__':
    # set polarizer angles
    pol1_angles = [0, 45, 90, 135]
    pol2_angles = np.linspace(0, 180, 9)
    # take polarization correlation measurements
    all_counts = polarization_correlation(pol1_angles, pol2_angles)
    # create plot for measured data and interpolated data
    fig1, ax1 = plt.subplots(1, 1)
    fig2, ax2 = plt.subplots(1, 1)

    for data in all_counts:
        # plot measured data
        plot_curves(ax1, pol2_angles, data, pol1_angles)
        x_new = np.arange(0, 180, 0.5)
        f_new = CubicSpline(pol2_angles, data)
        # plot interpolated data
        plot_curves(ax2, x_new, f_new(x_new), pol1_angles)

    # save data to coin_data.csv (first row is pol2_angles, subsequent rows are coincident count rates)
    all_data = np.vstack([pol2_angles, all_counts])
    with open('coin_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

    plt.show()
