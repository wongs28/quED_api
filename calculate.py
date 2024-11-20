import csv
import numpy as np
from scipy.interpolate import CubicSpline


def calculate_E(a, a_perp, b, b_perp):
    norm = a(b) + a(b_perp) + a_perp(b) + a_perp(b_perp)
    return (a(b) - a(b_perp) - a_perp(b) + a_perp(b_perp)) / norm


def calculate_S(a, ap, a_perp, ap_perp, b, bp, perp):
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
    with open('coin_data.csv', 'r') as file:
        reader = csv.reader(file)
        all_data = [row for row in reader]

    counts = []
    for data in all_data[1:]:
        counts.append(CubicSpline(all_data[0], data))

    S1 = calculate_S(counts[0], counts[1], counts[2], counts[3], 22.5, 67.5, -90)
    S2 = calculate_S(counts[0], counts[1], counts[2], counts[3], 22.5, 67.5, 270)
    print(S1, S2, sep='\n')
    # for count in counts:
    #     for angle in [22.5, 67.5, 112.5, 157.5]:
    #         print(count(angle))
