from random import randint

class User_Node:
    def __init__(self, id, i=-1, y=randint(0, 10000), left_child=None, right_child=None, signer=None):
        self.id = id
        self.i = i
        self.y = y
        self.left_child = left_child
        self.right_child = right_child
        self.signer = signer
        if signer is not None:
            signer.set_node(self)
        self.hash = None

    def set_hash(self, hash):
        self.hash = hash