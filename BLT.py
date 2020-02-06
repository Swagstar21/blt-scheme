from repository import Repository
from server import Server
import hashlib
import binascii
from user_node import User_Node
from math import log
from signer import Signer
import time

def get_hash(s1, s2):
    concatenated_string = s1 + s2
    return hashlib.sha256(concatenated_string).digest()

def initialize_topology(number_signers, number_keys_per_signer=32):
    signers = [User_Node(i) for i in range(number_signers)]
    s = Server(number_signers, signers)
    r = Repository(s)
    r.latest_summary = s.summary
    r.commitments.append(s.summary)
    S = []
    for i in range(number_signers):
        S.append(Signer(number_keys_per_signer))
        S[i].register(s)

    return s, S, r

def normal_functioning():
    number_signers = 8
    print "================= Some regular transactions ================="
    s, signers, r = initialize_topology(number_signers)
    for i in range(number_signers):
        signers[i].sign_message("Signer {} greets you!".format(i), s, r)

def multiple_signatures():
    number_signers = 2
    number_keys_per_signer = 16
    print "================= Multiple signatures for a user ================="
    s, signers, r = initialize_topology(number_signers, number_keys_per_signer)
    for i in range(number_keys_per_signer):
        signers[0].sign_message("Number {}".format(i), s, r)

def stress_testing_the_concept():
    number_signers = 256
    number_keys_per_signer = 32

    print "================= Stress test ================="
    s, signers, r = initialize_topology(number_signers, number_keys_per_signer)

    print "The timer has started..."
    start_time = time.time()

    for i in range(number_signers):
        for j in range(number_keys_per_signer):
            signers[i].sign_message("Signing with the {}th key".format(j), s, r, verbose_level=0)

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print "For {} signers, each signing {} messages, the operation took {} seconds for a total of {} messages signed" \
        .format(number_signers, number_keys_per_signer, round(elapsed_time, 2), number_signers * number_keys_per_signer)

def signer_uses_an_earlier_key():
    number_signers = 2
    number_keys_per_signer = 16
    print "================= Signer signs using a used key  ================="
    s, signers, r = initialize_topology(number_signers, number_keys_per_signer)
    signers[0].sign_message("Tricking the system", s, r)
    signers[0].sign_message("Tricking the system", s, r, unused_key_index=0)

def user_masquerades_as_another():
    number_signers = 4
    number_keys_per_signer = 8
    print "================= User masquerades as other user ================="
    signers = [User_Node(i) for i in range(number_signers)]
    s = Server(number_signers, signers)
    r = Repository(s)
    r.latest_summary = s.summary
    r.commitments.append(s.summary)
    S = []
    for i in range(number_signers):
        S.append(Signer(number_keys_per_signer))
        S[i].register(s)

    S[0].sign_message("Not my message", s, r, i=2)

def faulty_server():
    number_signers = 8
    print "================= Faulty server ================="
    s, signers, r = initialize_topology(number_signers)
    s.faulty = 1
    for i in range(number_signers):
        signers[i].sign_message("Signer {} tries in vain to sign its message!".format(i), s, r)

def faulty_repository():
    number_signers = 8
    print "================= Faulty repository ================="
    s, signers, r = initialize_topology(number_signers)
    r.faulty = 1
    signers[0].sign_message("Alice sends Bob 1$", s, r)
    signers[1].sign_message("Bob sends Alice 4$", s, r)
    signers[2].sign_message("Alice sends Trudy 10000$", s, r)

if  __name__ == "__main__":
    line = raw_input("Run scenario number: ")
    print
    while line != "exit":
        if line == "1":
            normal_functioning()
        elif line == "2":
            multiple_signatures()
        elif line == "3":
            stress_testing_the_concept()
        elif line == "4":
            signer_uses_an_earlier_key()
        elif line == "5":
            user_masquerades_as_another()
        elif line == "6":
            faulty_server()
        elif line == "7":
            faulty_repository()
        elif line == "show":
            print
            print "Scenarios:"
            print "1) Regular functioning with 8 users"
            print "2) A single user signs multiple documents"
            print "3) Performance test"
            print "4) User tries to sign a message with an earlier key"
            print "5) User tries to masquarade as another"
            print "6) Server is faulty"
            print "7) Repository is faulty"
        print
        line = raw_input("Run scenario number: ")

    
