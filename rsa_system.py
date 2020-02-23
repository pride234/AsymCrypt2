import hashlib
import math


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def gcd_ext(a, b):
    x, _x, y, _y = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, _x = _x, x - _x * q
        y, _y = _y, y - _y * q
    return (x, y, a)


class DataConvert:
    @classmethod
    def int_to_bytes(cls, int_to_convert):
        bytes_amount = math.ceil(len(hex(int_to_convert)[2:]) / 2)
        return int_to_convert.to_bytes(bytes_amount, 'big')

    @classmethod
    def bytes_to_int(cls, bytes_to_convert):
        return int.from_bytes(bytes_to_convert, 'big')

    @classmethod
    def str_to_int(cls, str_to_convert):
        byte_repr = str_to_convert.encode('latin1')
        return cls.bytes_to_int(byte_repr)

    @classmethod
    def int_to_str(cls, int_to_convert):
        byte_repr = cls.int_to_bytes(int_to_convert)
        return byte_repr.decode('latin1')


class RSASystem:
    def __init__(self, prime_prg, min_bits=256):
        self.__prime_prg = prime_prg
        self.__private_key = None
        self.__public_key = None
        self.__min_bits = min_bits
        self.__p = None
        self.__q = None

    def generate_key_pair(self, low_boundary=None, high_boundary=None):
        low_boundary = low_boundary or 2 ** self.__min_bits - 1
        high_boundary = high_boundary or low_boundary * 2
        print('Initializing P and Q')
        self.__p = self.__prime_prg.prime_in_range(low_boundary, high_boundary)
        self.__q = self.__prime_prg.prime_in_range(low_boundary, high_boundary)
        self.__recompute_key_pair()

    def __recompute_key_pair(self):
        n = self.__p * self.__q
        phi_n = (self.__p - 1) * (self.__q - 1)

        e = self.__prime_prg.rand_in_range(2, phi_n - 1)
        while gcd(e, phi_n) != 1:
            e = self.__prime_prg.rand_in_range(2, phi_n - 1)
        assert(gcd(phi_n, e) == 1)

        d, _, _ = gcd_ext(e, phi_n)
        d = d % phi_n
        self.__private_key = (n, d)
        self.__public_key = (n, e)

    def get_public_key(self):
        return self.__public_key

    def get_private_key(self):
        return self.__private_key

    def set_keys(self, n, e, d):
        self.__public_key = (n, e)
        self.__private_key = (n, d)

    @staticmethod
    def encrypt(message, key):
        n, e = key
        return pow(message, e, n)

    @staticmethod
    def decrypt(cypher, key):
        # Basically the same as encrypt
        n, d = key
        return pow(cypher, d, n)

    @staticmethod
    def sign(message, private_key, hash_algo='SHA1'):
        if hash_algo is not None:
            digest = DataConvert.bytes_to_int(
                hashlib.new(
                    hash_algo,
                    DataConvert.int_to_bytes(message)
                ).digest()
            )
        else:
            digest = message
        n, d = private_key
        return pow(digest, d, n)

    @staticmethod
    def verify(message, signature, open_key, hash_algo='SHA1'):
        if hash_algo is None:
            digest = message
        else:
            digest = DataConvert.bytes_to_int(
                hashlib.new(
                    hash_algo,
                    DataConvert.int_to_bytes(message)
                ).digest()
            )
        n, e = open_key
        decrypted_digest = pow(signature, e, n)
        return digest == decrypted_digest

    def send_key(self, key, receiver_public_key):
        k1 = self.encrypt(key, receiver_public_key)
        s = self.encrypt(key, self.get_private_key())
        s1 = self.encrypt(s, receiver_public_key)
        return (k1, s1)

    def receive_key(self, sender_public_key, k1, s1):
        k_1 = self.decrypt(k1, self.get_private_key())
        s = self.decrypt(s1, self.get_private_key())
        k_2 = self.decrypt(s, sender_public_key)
        if k_1 == k_2:
            return k_1
        else:
            print('receive failure')
