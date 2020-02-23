import random

from generators import BytePRG, GenCache
from generators import LehmerLow
from generators import LehmerHigh
from generators import L20
from generators import L89
from generators import Geffe
from generators import Wolfram
from generators import Librarian
from generators import BM
from generators import BMBytes
from generators import BBS
from generators import BBSBytes

from criterias import UnifiedDistributionCriteria
from criterias import UnifiedPairDistributionCriteria
from criterias import UnifiedSequencePartDistributionCriteria


# SEED = random.randint(0, 2 ** 48)
SEED = 1


def print_generator_sample(generator):
    default_length = 100
    print('{:<15}: {}'.format(generator.__class__.__name__, generator.bytes(default_length).hex()))


def main():
    generators = [
        BytePRG(seed=SEED),
        LehmerLow(seed=SEED),
        LehmerHigh(seed=SEED),
        L20(seed=SEED),
        L89(seed=SEED),
        Geffe(seed=SEED),
        Wolfram(seed=SEED),
        Librarian('silmalirion.txt', prepare=True),
        BM(seed=SEED),
        BMBytes(seed=SEED),
        BBS(seed=SEED),
        BBSBytes(seed=SEED),
    ]
    # alphas = [0.1, 0.075, 0.05, 0.025, 0.01]
    alphas = [0.01, 0.05, 0.1, 0.25, 0.44]
    test_length = 2 * (1000000 // 8)
    for gen in generators:
        print('\nCHECKING {}'.format(gen))
        cache = GenCache(gen, allow_storage=True)
        # print_generator_sample(gen)
        UnifiedDistributionCriteria(cache.new_iterator(), alphas, test_length).run()
        UnifiedPairDistributionCriteria(cache.new_iterator(), alphas, test_length).run()
        UnifiedSequencePartDistributionCriteria(cache.new_iterator(), alphas, test_length, 30).run()


if __name__ == '__main__':
    main()
