from random import randint
from binascii import hexlify
import hashlib
from math import log
from repository import Repository

def generate_random_key(k):
    key = []
    for _ in range(k // 8):
        key.append(randint(0, 255))
    return "".join([chr(x) for x in key])

def get_hash(s1, s2):
    concatenated_string = s1 + s2
    return hashlib.sha256(concatenated_string).digest()

class Signer:
    def __init__(self, N, k=256, keys=None):
        self.node = None
        self.unused_key_index = 0
        self.bits_per_key = k
        if keys == None:
            keys = []
            for _ in range(N):
                key = generate_random_key(k)
                keys.append(key)
                
        self.private_keys = keys

        self.number_levels = int(log(N, 2)) + 1
        self.calculate_public_key(N)

    def calculate_public_key(self, N):
        self.partial_hash = [["X" for _ in range(N)] for _ in range(self.number_levels)]

        self.partial_hash[0] = [get_hash(str(i), self.private_keys[i]) for i in range(N)]
        
        for i in range(1, self.number_levels):
            for j in range(0, 2 ** (self.number_levels - i - 1)):
                self.partial_hash[i][j] = get_hash(self.partial_hash[i - 1][j * 2], self.partial_hash[i - 1][j * 2 + 1])

        self.public_key = self.partial_hash[self.number_levels - 1][0]

    def set_node(self, node):
        self.node = node

    def get_id(self):
        return self.node.id

    def register(self, server):
        server.register_user(self)

    def verify_hash_chain(self, summary, hash_chain):
        if hash_chain == None and summary != None:
            return False
            
        hash = get_hash(str(self.node.i), str(self.node.y))
        for i in range(len(hash_chain)):
            parity, h = hash_chain[i]
            if parity == 0:
                hash = get_hash(hash, h)
            else:
                hash = get_hash(h, hash)

        return hash == summary

    def extract_hash_chain(self, id):
        hash_chain = []
        for i in range(self.number_levels - 1):
            if id % 2 == 0:
                index_tree_peer = id + 1
                hash_chain.append((0, self.partial_hash[i][index_tree_peer]))
            else:
                index_tree_peer = id - 1
                hash_chain.append((1, self.partial_hash[i][index_tree_peer]))

            id = int(id / 2)

        return hash_chain

    def sign_message(self, message, server, repository, i=None, y=None, unused_key_index=None, time=None, verbose_level=1):
        if unused_key_index == None:
            unused_key_index = self.unused_key_index
        if y == None:
            y = int(hexlify(get_hash(message, self.private_keys[unused_key_index])), 16)
        if i == None:
            i = self.get_id()
        if time == None:
            time = server.time
            
        hash_chain = server.give_hash_chain(i, y, repository)

        summary = repository.get_latest_summary()
        
        verify_hash = self.verify_hash_chain(summary, hash_chain)

        is_tuple_valid = repository.verify(message, self.get_id(), self.node.i, self.private_keys[self.unused_key_index], self.extract_hash_chain(self.unused_key_index), server.time, hash_chain)

        if verbose_level == 1:
            if verify_hash == True and is_tuple_valid == True:
                print "Signer {}: Message \"{}\" was successfully signed".format(self.get_id(), message)
            else:
                print "Signer {}: Message \"{}\" has an invalid signature".format(self.get_id(), message)
                return

        self.unused_key_index += 1