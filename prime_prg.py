import math


class IntInRangePRG:
    def __init__(self, base_prg):
        self.__base_prg = base_prg

    def rand_in_range(self, low_bound, high_bound, iter_treshold=10000):
        max_bytes = math.ceil(len(hex(high_bound)[2:]) / 2)
        for _ in range(iter_treshold):
            random_bytes = self.__base_prg.bytes(max_bytes)
            number = int.from_bytes(random_bytes, 'big')
            if number < low_bound or number > high_bound:
                continue
            return number
        raise Exception('Number in [{}, {}] was not found within {} iterations'.format(
            low_bound, high_bound, iter_treshold
        ))


class PrimePRG(IntInRangePRG):
    def __init__(self, base_prg, prime_test):
        super().__init__(base_prg)
        self.__test = prime_test

    def prime_in_range(self, low_bound, high_bound, iter_treshold=1000):
        print('Trying to find prime in [{}, {}]'.format(hex(low_bound), hex(high_bound)))
        for i in range(iter_treshold):
            prime_candidate = self.rand_in_range(low_bound, high_bound)
            if self.__test.is_prime(prime_candidate):
                print('Found in iter {}: {} ({})'.format(i, hex(prime_candidate), prime_candidate))
                return prime_candidate
        raise Exception('Prime was not found within {} iterations'.format(low_bound, high_bound, iter_treshold))
