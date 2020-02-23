import math
import time

import scipy.stats


class CriteriaBase:
    def __init__(self, byte_source, alphas, test_length):
        self._byte_source = byte_source
        self._alphas = alphas
        self._test_length = test_length
        self._start_time = None
        self._finish_time = None

    def __repr__(self):
        return '{}(source={}, n_bytes={}, n_bits={})'.format(
            self.__class__.__name__, self._byte_source, self._test_length, self._test_length * 8
        )

    def __str__(self):
        return self.__repr__()

    def run(self):
        print(str(self))
        self._start_time = time.time()
        context = self._run()
        self.print_runtime_stats(self._test_length)
        self._finish_time = time.time()
        self.print_final_stats(context)

    def print_runtime_stats(self, iteration):
        if iteration % 1000 == 0:
            print('\r{:.2%} test completed in {:.5f} sec'.format(
                iteration / self._test_length, time.time() - self._start_time
            ), end='')

    def print_final_stats(self, context):
        print('\r100% test completed in {:.5f} sec; Results:'.format(self._finish_time - self._start_time))
        xi_2 = self._get_xi_2(context)
        for alpha in self._alphas:
            xi_2_l = self._get_xi_2_l(alpha, context)
            symbol = '<= ' if xi_2 <= xi_2_l else ' > '
            symbol2 = 'done' if xi_2 <= xi_2_l else 'FAILED'
            print('\talpha = {:.3f}: {:.3f} {} {:.3f} {}'.format(alpha, xi_2, symbol, xi_2_l, symbol2))

    def _run(self):
        return {}

    def _get_xi_2(self, context):
        return -1.0

    def _get_xi_2_l(self, alpha, context):
        return -1.0


class UnifiedDistributionCriteria(CriteriaBase):
    class _Context:
        def __init__(self, test_len):
            self.expected_count = test_len / 256
            self.distribution = {bytes([t]): 0 for t in range(0, 256)}

    def __init__(self, byte_source, alphas, test_length):
        super().__init__(byte_source, alphas, test_length)

    def _run(self):
        context = self._Context(self._test_length)
        for t in range(self._test_length):
            self.print_runtime_stats(t)
            context.distribution[self._byte_source.byte()] += 1
        return context

    def _get_xi_2(self, context):
        n = context.expected_count
        return sum(((v - n) ** 2/n) for v in context.distribution.values())

    def _get_xi_2_l(self, alpha, context):
        l = 255
        Z = scipy.stats.norm.ppf(1 - alpha)
        return math.sqrt(2 * l) * Z + l


class UnifiedPairDistributionCriteria(CriteriaBase):
    class _Context:
        def __init__(self, test_len):
            self.pairs_distribution = {bytes([t1, t2]): 0 for t1 in range(0, 256) for t2 in range(0, 256)}
            self.first_symbol_distribution = {bytes([t]): 0 for t in range(0, 256)}
            self.last_symbol_distribution = {bytes([t]): 0 for t in range(0, 256)}
            self.n = test_len // 2

    def __init__(self, byte_source, alphas, test_length):
        super().__init__(byte_source, alphas, test_length)

    def _get_xi_2(self, context):
        res_sum = 0
        for i in range(0, 256):
            for j in range(0, 256):
                v_ij = context.pairs_distribution[bytes([i, j])]
                v_i = context.first_symbol_distribution[bytes([i])]
                a_j = context.last_symbol_distribution[bytes([j])]
                if v_i and a_j:
                    res_sum += v_ij ** 2 / (v_i * a_j)
        return context.n * (res_sum - 1)

    def _get_xi_2_l(self, alpha, context):
        l = 255 ** 2
        Z = scipy.stats.norm.ppf(1 - alpha)
        return math.sqrt(2 * l) * Z + l

    def _run(self):
        context = self._Context(self._test_length)
        for t in range(self._test_length // 2):
            self.print_runtime_stats(t)
            pair = self._byte_source.bytes(2)
            context.pairs_distribution[pair] += 1
            context.first_symbol_distribution[pair[0:1]] += 1
            context.last_symbol_distribution[pair[1:2]] += 1
        return context


class UnifiedSequencePartDistributionCriteria(CriteriaBase):
    class _Context:
        def __init__(self, test_len, parts_count):
            self.parts_distributions = {part: {bytes([t]): 0 for t in range(256)} for part in range(parts_count)}
            self.part_length = test_len // parts_count

    def __init__(self, byte_source, alphas, test_length, parts_count):
        super().__init__(byte_source, alphas, test_length)
        self._parts_count = parts_count

    def _run(self):
        context = self._Context(self._test_length, self._parts_count)
        for r in range(self._parts_count):
            for t in range(context.part_length):
                context.parts_distributions[r][self._byte_source.byte()] += 1
                self.print_runtime_stats(r * context.part_length + t)
        return context

    def __repr__(self):
        return '{}(source={}, n_bytes={}, n_bits={}, n_parts={})'.format(
            self.__class__.__name__, self._byte_source, self._test_length, self._test_length * 8, self._parts_count
        )

    def _get_xi_2(self, context):
        res_sum = 0
        for i in range(256):
            v_i = sum(context.parts_distributions[t][bytes([i])] for t in range(self._parts_count))
            a_j = context.part_length
            for j in range(self._parts_count):
                v_ij = context.parts_distributions[j][bytes([i])]
                if v_i and a_j:
                    res_sum += v_ij ** 2 / (v_i * a_j)
        return self._test_length * (res_sum - 1)

    def _get_xi_2_l(self, alpha, context):
        l = 255 * (self._parts_count - 1)
        Z = scipy.stats.norm.ppf(1 - alpha)
        return math.sqrt(2 * l) * Z + l
