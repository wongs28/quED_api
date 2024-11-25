from main import plot_curves

import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline


def calculate_E(a, a_perp, b, b_perp):
    """
    This function calculates the expectation value for angles a and b. perp = perpendicular.
    a(b) is the coincident count rate at polarizer 1 = a and polarizer 2 = b.

    :param a: cubic spline corresponding to angle a
    :param a_perp: cubic spline corresponding to angle a_perp
    :param b: angle b
    :param b_perp: angle b_perp
    :return: expectation value
    """
    norm = a(b) + a(b_perp) + a_perp(b) + a_perp(b_perp)
    return (a(b) - a(b_perp) - a_perp(b) + a_perp(b_perp)) / norm


def calculate_S(a, ap, a_perp, ap_perp, b, bp, perp):
    """
    This function calculates the S value from expectation values of a, ap, b, and bp.
    p = prime.
    perp = perpendicular.

    :param a: cubic spline corresponding to polarizer 1 = a
    :param ap: cubic spline corresponding to polarizer 1 = ap
    :param a_perp: cubic spline corresponding to polarizer 1 = a_perp
    :param ap_perp: cubic spline corresponding to polarizer 1 = ap_perp
    :param b: polarizer 2 = angle b
    :param bp: polarizer 2  = angle bp
    :param perp: perpendicular angle to add to b and bp
    :return: list of expectation values and S values
    """
    E_ab = calculate_E(a, a_perp, b, b+perp)
    E_abp = calculate_E(a, a_perp, bp, bp+perp)
    E_apb = calculate_E(ap, ap_perp, b, b+perp)
    E_apbp = calculate_E(ap, ap_perp, bp, bp+perp)
    E = [E_ab, E_abp, E_apb, E_apbp]

    S1 = -E_ab + E_abp + E_apb + E_apbp
    S2 = E_ab - E_abp + E_apb + E_apbp
    S3 = E_ab + E_abp - E_apb + E_apbp
    S4 = E_ab + E_abp + E_apb - E_apbp
    S = [S1, S2, S3, S4]

    return E, S


if __name__ == '__main__':
    # open coin_data.csv and copy it to a list
    with open('coin_data.csv', 'r') as file:
        reader = csv.reader(file)
        all_data = [row for row in reader]

    fig3, ax3 = plt.subplots(1, 1)
    # create cubic splines to interpolate data for calculation
    counts = []
    for data in all_data[1:]:
        x_new = np.arange(0, 180, 0.5)
        f_new = CubicSpline(all_data[0], data)
        counts.append(f_new)
        plot_curves(ax3, x_new, f_new(x_new), [0, 45, 90, 135])

    # calculate using interpolated data
    S = calculate_S(counts[0], counts[1], counts[2], counts[3], 22.5, 67.5, 90)
    print(S)

    # calculate manually using measured data
    test_cnt = [[] for _ in range(4)]
    i = 0
    for count in counts:
        for angle in [22.5, 67.5, 112.5, 157.5]:
            test_cnt[i].append(count(angle))
        i = i + 1
    print(test_cnt)
    test_e = []
    for i in range(2):
        test_e.append((test_cnt[i][0] - test_cnt[i][2] - test_cnt[i+2][0] + test_cnt[i+2][2]) / (
                test_cnt[i][0] + test_cnt[i][2] + test_cnt[i+2][0] + test_cnt[i+2][2]))
        test_e.append((test_cnt[i][1] - test_cnt[i][3] - test_cnt[i+2][1] + test_cnt[i+2][3]) / (
                    test_cnt[i][1] + test_cnt[i][3] + test_cnt[i + 2][1] + test_cnt[i + 2][3]))
    print(test_e)
    plt.show()
