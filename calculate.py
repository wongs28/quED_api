from main import calculate_S

import csv
import numpy as np
from scipy.interpolate import CubicSpline

if __name__ == '__main__':
    with open('count_rates.csv', 'r') as file:
        all_data = csv.reader(file)
    
    counts = []
    for data in all_data[1:]:
        counts.append(CubicSpline(all_data[0], data))

    S1 = calculate_S(counts[0], counts[1], counts[2], counts[3], 22.5, 67.5, 90)
    S2 = calculate_S(counts[0], counts[1], counts[2], counts[3], 22.5, 67.5, 270)
    print(S1, S2)
