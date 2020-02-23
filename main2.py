from generators import BytePRG, Wolfram, GenCache
from prime_prg import PrimePRG, IntInRangePRG
from prime_tests import MillerRabinPrimeNumberTest
from rsa_system import RSASystem, DataConvert


def complete_test_run():
    prg_cache = GenCache(Wolfram(seed=0), allow_storage=True)
    byte_prg = prg_cache.new_iterator()

    prg = IntInRangePRG(byte_prg)
    prime_test = MillerRabinPrimeNumberTest(prg, 10)
    prime_prg = PrimePRG(byte_prg, prime_test)

    A = RSASystem(prime_prg)
    A.generate_key_pair()
    B = RSASystem(prime_prg)
    B.generate_key_pair()

    pq_A, pq_B = A.get_public_key()[0], B.get_public_key()[0]

    if pq_A > pq_B:
        A, B = B, A
        pq_A, pq_B = pq_B, pq_A

    # message = prg.rand_in_range(2 ** 10, pq_A)
    message = DataConvert.str_to_int('Just a test string')

    cypher_A = A.encrypt(message, A.get_public_key())
    signature = A.sign(message, A.get_private_key(), hash_algo=None)
    decrypted_A = A.decrypt(cypher_A, A.get_private_key())
    A_signature_verified = A.verify(decrypted_A, signature, A.get_public_key(), hash_algo=None)
    if message == decrypted_A:
        print('A encryption and decryption was done correctly')
        print('message:   {}\ndecrypted: {}'.format(hex(message), hex(decrypted_A)))
    else:
        print('A encryption/decryption FAILURE')
    if A_signature_verified:
        print('A signature was verified')
    else:
        print('A signature FAILURE')
    print('\nRSA data to check:')
    print('Public  key: {}'.format(A.get_public_key()))
    print('HEX Public  key: ({}, {})'.format(hex(A.get_public_key()[0]), hex(A.get_public_key()[1])))
    print('Private key: {}'.format(A.get_private_key()))
    print('HEX Private key: ({}, {})'.format(hex(A.get_private_key()[0]), hex(A.get_private_key()[1])))
    print('message: {} ( {} ( {} ) )'.format(DataConvert.int_to_str(message), hex(message), message))
    print('cypher: {} ({})'.format(hex(cypher_A), cypher_A))
    print('signature: {} ({})'.format(hex(signature), signature))
    print('\n\n')

    cypher_B = B.encrypt(message, B.get_public_key())
    signature = B.sign(message, B.get_private_key())
    decrypted_B = B.decrypt(cypher_B, B.get_private_key())
    B_signature_verified = B.verify(decrypted_B, signature, B.get_public_key())
    if message == decrypted_B:
        print('B encryption and decryption was done correctly')
        print('message:   {}\ndecrypted: {}\n'.format(hex(message), hex(decrypted_B)))
    else:
        print('B encryption/decryption FAILURE')
    if B_signature_verified:
        print('B signature was verified')
    else:
        print('B signature FAILURE')

    key = prg.rand_in_range(2 ** 10, pq_A)
    k1, s1 = A.send_key(key, B.get_public_key())
    received = B.receive_key(A.get_public_key(), k1, s1)
    if key == received:
        print('Key was received correctly: {}'.format(hex(received)))
    print('Send/Receive key RSA info')
    print('Key: {}({})\nk1: {} ({})\ns1: {} ({})'.format(hex(key), key, hex(k1), k1, hex(s1), s1))


def simple_test_run():
    A = RSASystem(None, None)
    public_key = (int('A6A648F9F178DB768AC2F7055BAAB0E094B93F153107791F438079070A59C7D7', 16), int('10001', 16))
    A.set_keys(public_key[0], public_key[1], None)
    message = DataConvert.str_to_int('test text message to encrypt')
    cypher = A.encrypt(message, public_key)
    isSignatureCorrect = A.verify(message=int('4a7573742061207465737420737472696e67', 16),
        signature= int('5422DEB46C9AA64221476B83A4D4653D0B970ED3D900FD30016DE796A3C3F935', 16),
        open_key=public_key,
        hash_algo=None)
    print('Message = {} ({})'.format(hex(message), message))
    print('Cypher = {} ({})'.format(hex(cypher), cypher))
    print('The signature is correct: {}'.format(isSignatureCorrect))
    print('\n\n')
    print('\n\n')
    

def send_recieve_test_run():
    server_pub_key = (
        int('A6A648F9F178DB768AC2F7055BAAB0E094B93F153107791F438079070A59C7D7', 16), 
        int('10001', 16)
    )
    own_public_key = (
        int('1a044d07979c609bf916fb2a4f9f53e9766ce6c7a9769427ed7a8051bedc87b657b7629e4942ea1a3845481bed734937b79f31becd9f7520c47e16a0363af6c1b', 16),
        int('1820d6eb8465ba89ec895249003a0f69af92e29b1b05a4a3b5050173cc15deebd095f056dbcd8da7354ae73420d257b0f62623b3838a5c3f97e296557aada4e57', 16),
    )
    own_private_key = (
        int('1a044d07979c609bf916fb2a4f9f53e9766ce6c7a9769427ed7a8051bedc87b657b7629e4942ea1a3845481bed734937b79f31becd9f7520c47e16a0363af6c1b', 16),
        int('747cc5536648656dd98cea24dceea08888789fb9fb4ea47254b12ad9d14abaa6c6eb8cf6db6467629d5a862d6129bf6ba98e76f8463da7787fcba344cf8bafe7', 16),
    )
    own_small_pub_key = (
        int('59c0743274f9ea85cab3114bfbae5766f16b9c619c395414e2810d9858bb8d81', 16),
        int('3e5cc1c8d9f38e04fb0e07cebde474efc1f80958e1a29eb87be74ed7f4cb84e9', 16),
    )
    own_small_private_key = (
        int('59c0743274f9ea85cab3114bfbae5766f16b9c619c395414e2810d9858bb8d81', 16),
        int('19f418a7357d84ca19032ce945654af49e4eeef260f5608129c777003d6746b9', 16),
    )
    A = RSASystem(None, None)
    a_small = RSASystem(None, None)
    A.set_keys(own_public_key[0], own_public_key[1], own_private_key[1])
    a_small.set_keys(own_small_pub_key[0], own_small_pub_key[1], own_small_private_key[1])
    
    key = DataConvert.str_to_int('super important key')
    k1, s1 = a_small.send_key(key, server_pub_key)
    print('Sent k : {}\nk1: {}\nS1: {}'.format(hex(key), hex(k1), hex(s1)))
    
    recieved_key = A.receive_key(
        k1=int('B6D46C0D6C904F22C2F078DAB988DD4811058A0186E0793B861F2498349C1CD35E6594C82FF9D16695FB72D8212ACE32A96768E77F20162705BDE2A3891A73CA', 16),
        s1=int('0175873F8D3ECC4E62528F4C34C94EFC661B114315CC0CCB3B356C686555270F409417CF721149459B127F0C474FFC13F888B3CD17548F516B3D98C3999BB9AFC0', 16),
        sender_public_key=server_pub_key
    )
    print('recieved_key = {}'.format(hex(recieved_key) if recieved_key else recieved_key))

complete_test_run()
simple_test_run()
send_recieve_test_run()