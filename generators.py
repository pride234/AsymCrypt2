import math
import os
import random


class PRG:
    MAX_INT = 2 ** 32 - 1

    def __init__(self, seed=0):
        self._seed = seed
        self._base_random = random.Random(seed)

    def __repr__(self):
        return '{}(seed={})'.format(self.__class__.__name__, self._seed)

    @property
    def _internal_id(self):
        return '{}_seed_{}'.format(self.__class__.__name__.lower(), self._seed)

    def __str__(self):
        return self.__repr__()

    def _random_int(self, low=0, high=MAX_INT):
        return self._base_random.randint(low, high)


class BitPRG(PRG):
    def bit(self):
        return self._random_int(0, 1)

    def bits(self, amount=42):
        assert amount % 8 == 0
        res = 0
        for t in range(amount):
            res = res << 1
            res += self.bit()
        return res.to_bytes(amount // 8, 'big')

    def byte(self):
        return self.bits(8)

    def bytes(self, amount=42):
        return self.bits(amount * 8)


class BytePRG(PRG):
    MAX_ONE_BYTE_INT = 255

    def _int_to_byte(self, number):
        return bytes([number])

    def byte(self):
        return self._int_to_byte(self._random_int(0, self.MAX_ONE_BYTE_INT))

    def bytes(self, amount=10):
        return b''.join(self.byte() for _ in range(amount))


class LehmerLow(BytePRG):
    def __init__(self, m=2**32, a=2**16+1, c=119, seed=0):
        super().__init__(seed)
        self.m = m
        self.a = a
        self.c = c
        self.x = self._random_int()

    def byte(self):
        self.x = (self.a * self.x + self.c) % self.m
        return self._int_to_byte(self.x % (self.MAX_ONE_BYTE_INT + 1))


class LehmerHigh(LehmerLow):
    def byte(self):
        self.x = (self.a * self.x + self.c) % self.m
        x = self.x >> 24
        return self._int_to_byte(x)


class BitPRGRegister(BitPRG):
    def __init__(self, min_length, seed=0, xor_indexes=None):
        super().__init__(seed)
        self._xor_indexes = xor_indexes or list(range(min_length))
        self._cache = [self._random_int(0, 1) for t in range(min_length)]
        while sum(self._cache) <= 0:
            self._cache = [self._random_int(0, 1) for t in range(min_length)]

    def bit(self):
        x = 0
        for t in self._xor_indexes:
            x = x ^ self._cache[t]
        ret_x, self._cache = self._cache[0], self._cache[1:] + [x]
        # self._cache.append(x)
        return ret_x


class L20(BitPRGRegister):
    def __init__(self, seed=0):
        super().__init__(20, seed, xor_indexes=[17, 15, 11, 0])


class L89(BitPRGRegister):
    def __init__(self, seed=0):
        super().__init__(89, seed, xor_indexes=[51, 0])


class Geffe(BitPRG):
    def __init__(self, seed=0):
        super().__init__(seed)
        self.x_register = BitPRGRegister(11, seed=self._random_int(), xor_indexes=[0, 2])
        self.y_register = BitPRGRegister(9, seed=self._random_int(), xor_indexes=[0, 1, 3, 4])
        self.s_register = BitPRGRegister(10, seed=self._random_int(), xor_indexes=[0, 3])

    def bit(self):
        x = self.x_register.bit()
        y = self.y_register.bit()
        s = self.s_register.bit()
        return (s * x) ^ ((1 ^ s)*y)


class Wolfram(BitPRG):
    def __init__(self, seed=0):
        super().__init__(seed)
        self.r = self._random_int()

    def bit(self):
        x = self.r % 2
        self.r = ((self.r << 1) % self.MAX_INT) ^ (self.r | (self.r >> 1))
        return x


class Librarian(BytePRG):
    _text = ''
    _fallback_limit = 1000

    def __init__(self, filepath='text.txt', prepare=False):
        with open(filepath, 'r', encoding='latin1') as inp:
            text = inp.read().lower()
        if prepare:
            import re
            text = re.sub(r'[^a-z]', '', text)
        self._text = text.encode('latin1')
        self._index = -1
        self._filepath = filepath

    def __repr__(self):
        return '{}(filepath={})'.format(self.__class__.__name__, self._filepath)

    @property
    def _internal_id(self):
        return 'Librarian_{}'.format(self._filepath.replace('.', '_').replace('/', '_').replace('\\', '_'))

    def byte(self):
        self._index += 1
        return self._int_to_byte(self._text[self._index])


class BM(BitPRG):
    def __init__(self, seed=0):
        super().__init__(seed)
        self._q = int('675215CC3E227D3216C056CFA8F8822BB486F788641E85E0DE77097E1DB049F1', 16)
        self._p = int('CEA42B987C44FA642D80AD9F51F10457690DEF10C83D0BC1BCEE12FC3B6093E3', 16)
        assert self._p == 2 * self._q + 1
        self._a = int('5B88C41246790891C095E2878880342E88C79974303BD0400B090FE38A688356', 16)
        self._T = self._random_int(0, self._p - 1)

    def bit(self):
        x = 1 if self._T < self._q else 0
        self._T = self._get_next_T()
        return x

    def _get_next_T(self):
        return pow(self._a, self._T, self._p)


class BMBytes(BytePRG, BM):
    def byte(self):
        k_low = ((256 * self._T) / (self._p - 1)) - 1
        k_high = (256 * self._T) / (self._p - 1)
        k = math.ceil(k_low)
        self._T = self._get_next_T()
        if k < k_low or k >= k_high:
            raise Exception('k should be in [k_low, k_high) BUT {} not in [{} , {})'.format(k, k_low, k_high))
        return self._int_to_byte(k)


class BBS(BitPRG):
    def __init__(self, seed=0):
        super().__init__(seed)
        self._p = int('D5BBB96D30086EC484EBA3D7F9CAEB07', 16)
        self._q = int('425D2B9BFDB25B9CF6C416CC6E37B59C1F', 16)
        self._n = self._p * self._q
        self._r = self._random_int(2, self.MAX_INT)

    def bit(self):
        x = self._r % 2
        self._r = self._get_next_r()
        return x

    def _get_next_r(self):
        return (self._r ** 2) % self._n


class BBSBytes(BBS, BytePRG):
    def byte(self):
        x = self._r % 256
        self._r = self._get_next_r()
        return self._int_to_byte(x)


class _CacheIterator:
    def __init__(self, source):
        self._source = source
        self._index = 0

    def __repr__(self):
        return repr(self._source)

    def __str__(self):
        return self.__repr__()

    def byte(self):
        self._index += 1
        return self._source.get_byte_by_index(self._index - 1)

    def bytes(self, amount=1):
        return b''.join(self.byte() for _ in range(amount))


class GenCache:
    def __init__(self, byte_source, allow_storage=True):
        self._byte_source_position = 0
        self._byte_source = byte_source
        self._allow_storage = allow_storage
        self._filename = os.path.join('caches', '{}.cache'.format(self._byte_source._internal_id))

        if allow_storage:
            self._storage = self.__get_cache_from_storage()
        else:
            self._storage = b''

    def __get_cache_from_storage(self):
        if not os.path.isfile(self._filename):
            with open(self._filename, 'wb') as f:
                f.write(b'')
        with open(self._filename, 'r+b') as file_cache:
            cached_data = file_cache.read()
        return cached_data

    def __update_storage(self, addition):
        if not self._allow_storage:
            return
        with open(self._filename, 'r+b') as file_cache:
            file_cache.seek(len(self._storage))
            file_cache.write(addition)
        self._storage += addition

    def __repr__(self):
        return 'GenCache({})'.format(self._byte_source)

    def __str__(self):
        return self.__repr__()

    def get_byte_by_index(self, index):
        while len(self._storage) <= index:
            addition = self._get_bytes_from_source(len(self._storage), 10000)
            self.__update_storage(addition)
        return self._storage[index:index + 1]

    def _get_bytes_from_source(self, offset, amount):
        assert offset >= self._byte_source_position
        if offset - self._byte_source_position:
            print('Seeking byte_source to {}. {} to go'.format(offset, offset - self._byte_source_position))
        self._byte_source.bytes(offset - self._byte_source_position)
        self._byte_source_position = offset + amount
        return self._byte_source.bytes(amount)

    def new_iterator(self):
        return _CacheIterator(self)
