import hashlib
from binascii import hexlify

def get_hash(s1, s2):
    concatenated_string = s1 + s2
    return hashlib.sha256(concatenated_string).digest()

class Repository:
    def __init__(self, server, faulty=0):
        self.server = server
        self.latest_summary = None
        self.keys_used = {}
        self.commitments = []
        self.faulty = faulty

    def publish_latest_summary(self, summary):
        self.latest_summary = summary

    def verify_hash_chain(self, hash_chain, i, y, summary):
        if self.faulty == 1:
            return True

        if hash_chain == None:
            return False
            
        hash = get_hash(str(i), str(y))
        for i in range(len(hash_chain)):
            parity, h = hash_chain[i]
            if parity == 0:
                hash = get_hash(hash, h)
            else:
                hash = get_hash(h, hash)

        return hash == summary

    def validate_and_publish(self, i, y, a, r, yprime, rprime):
        if self.faulty == 1:
            return True

        if r == self.latest_summary:
            is_first_chain_correct = self.verify_hash_chain(a, i, y, r)
        else:
            return False

        is_second_chain_correct = self.verify_hash_chain(a, i + 1, yprime, rprime)
        if is_first_chain_correct and is_second_chain_correct:
            self.latest_summary = rprime
            self.commitments.append(rprime)
            return True
        else:
            return False

    def verify(self, message, id, i, z, c, t, a):
        if self.faulty == 1:
            return True

        public_key = self.server.signers[id].signer.public_key
        rt = self.commitments[t]
        y = int(hexlify(get_hash(message, z)), 16)
        is_public_key_valid = self.verify_hash_chain(c, i, z, public_key)
        is_commitment_valid = self.verify_hash_chain(a, i, y, rt)
        return is_public_key_valid and is_commitment_valid

    def get_latest_summary(self):
        return self.latest_summary
