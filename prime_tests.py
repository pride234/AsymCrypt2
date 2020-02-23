import math


class MillerRabinPrimeNumberTest:
    def __init__(self, prg, k=20):
        self._k = k
        self._prg = prg

    def is_prime(self, number):
        for i in range(self._k):
            if self._test_step(number) is False:  # may be None too
                return False
        return True

    def _test_step(self, p):
        x = self._prg.rand_in_range(2, p - 1)

        gcd = math.gcd(x, p)
        if gcd > 1:
            # p is complex.
            return False

        d, s = self._get_ds(p)
        x_d_mod_p = pow(x, d, p)
        if x_d_mod_p == 1 or x_d_mod_p == p - 1:
            return True

        for r in range(1, s):  # [1, s - 1]
            x_r = pow(x, d * (2 ** r), p)
            if x_r == p - 1:
                return True
            if x_r == 1:
                return False
        return False

    def _get_ds(self, number):
        remaining = number - 1
        d = s = 0
        while remaining % 2 == 0:
            s += 1
            remaining //= 2
        d = remaining
        return d, s