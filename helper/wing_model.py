import numpy as np

from helper.calculator import calculate_x_distance


class WingModel:
    def __init__(self, S,K,t,r,v,q,k1,k2,b):
        xp0 = -4
        xpc = -2
        xcc = 2
        xc0 = 4
        part1p = (2 * k1 * xpc + b) / (2 * (xpc - xp0))
        part2p = -(2 * k1 * xpc + b) / (xpc - xp0)
        part1c = (2 * k2 * xcc + b) / (2 * (xcc - xc0))
        part2c = -(2 * k2 * xcc + b) / (xcc - xc0)
        sigma_p = k1 * xpc * xpc + b * xpc + v - (part1p * xpc * xpc + part2p * xp0 * xpc)
        sigma_c = k2 * xcc * xcc + b * xcc + v - (part1c * xcc * xcc + part2c * xc0 * xcc)

        if isinstance(K, np.ndarray) or isinstance(K, list):
            self.vol = [0] * len(list(K))
            for i in range(len(K)):
                xx = calculate_x_distance(S, K[i], t, r, v, q)
                if xx < xp0:
                    self.vol[i] = part1p * xp0 * xp0 + part2p * xp0 * xp0 + sigma_p
                elif xx < xpc:
                    self.vol[i] = part1p * xx * xx + part2p * xp0 * xx + sigma_p
                elif xx < 0:
                    self.vol[i] = k1 * xx * xx + b * xx + v
                elif xx < xcc:
                    self.vol[i] = k2 * xx * xx + b * xx + v
                elif xx < xc0:
                    self.vol[i] = part1c * xx * xx + part2c * xc0 * xx + sigma_c
                else:
                    self.vol[i] = part1c * xc0 * xc0 + part2c * xc0 * xc0 + sigma_c
        else:
            xx = calculate_x_distance(S, K, t, r, v, q)
            if xx < xp0:
                self.vol = part1p * xp0 * xp0 + part2p * xp0 * xp0 + sigma_p
            elif xx < xpc:
                self.vol = part1p * xx * xx + part2p * xp0 * xx + sigma_p
            elif xx < 0:
                self.vol = k1 * xx * xx + b * xx + v
            elif xx < xcc:
                self.vol = k2 * xx * xx + b * xx + v
            elif xx < xc0:
                self.vol = part1c * xx * xx + part2c * xc0 * xx + sigma_c
            else:
                self.vol = part1c * xc0 * xc0 + part2c * xc0 * xc0 + sigma_c