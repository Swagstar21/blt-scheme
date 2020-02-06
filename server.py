from signer import get_hash, Signer
from math import log
from binascii import hexlify
from random import randint

def generate_random_digest():
    digest = []
    for _ in range(32):
        digest.append(randint(0, 255))
    return "".join([chr(x) for x in digest])

class Server:
    def __init__(self, number_signers, signers, faulty=0):
        self.number_signers = number_signers
        self.signers = signers
        self.current_user = 0
        self.faulty = faulty
        self.number_levels = int(log(self.number_signers, 2)) + 1
        self.summary = None
        self.hashes = [['X' for _ in range(self.number_signers)] for _ in range(self.number_levels)]
        self.summary = self.calculate_summary()
        self.time = 0

    def register_user(self, signer):
        self.signers[self.current_user].signer = signer
        signer.set_node(self.signers[self.current_user])
        self.signers[self.current_user].id = self.current_user
        self.current_user += 1

    def calculate_summary(self):  
        if self.faulty == 1:
            return generate_random_digest()

        self.hashes[0] = [get_hash(str(self.signers[i].i), str(self.signers[i].y)) for i in range(self.number_signers)]

        for i in range(1, self.number_levels):
            for j in range(0, 2 ** (self.number_levels - i - 1)):
                self.hashes[i][j] = get_hash(self.hashes[i - 1][j * 2], self.hashes[i - 1][j * 2 + 1])

        return self.hashes[self.number_levels - 1][0]

    def extract_hash_chain(self, id):
        hash_chain = []

        if self.faulty == 1:
            for _ in range(self.number_levels - 1):
                hash_chain.append((1, generate_random_digest()))

            return hash_chain

        for i in range(self.number_levels - 1):
            if id % 2 == 0:
                index_tree_peer = id + 1
                hash_chain.append((0, self.hashes[i][index_tree_peer]))
            else:
                index_tree_peer = id - 1
                hash_chain.append((1, self.hashes[i][index_tree_peer]))

            id = int(id / 2)

        return hash_chain

    def give_hash_chain(self, id, y, repository):
        hash_chain = []

        if self.faulty == 1:
            for _ in range(self.number_levels - 1):
                hash_chain.append((1, generate_random_digest()))

            return hash_chain

        self.summary = self.calculate_summary()
        r = self.summary
        hash_chain = self.extract_hash_chain(id)
        old_y = self.signers[id].y
        self.signers[id].i += 1
        self.signers[id].y = y
        rprime = self.calculate_summary()

        is_valid = repository.validate_and_publish(self.signers[id].i - 1, old_y, hash_chain, r, y, rprime)

        if is_valid:
            new_hash_chain = self.extract_hash_chain(id)
            self.summary = rprime
            self.time += 1
            return new_hash_chain
        else:
            self.signers[id].i -= 1
            self.signers[id].y = old_y
            return None

        