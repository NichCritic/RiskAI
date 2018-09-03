from __future__ import division

import math


def armies_needed_to_attack(threshold, max_allied_armies, enemy_armies):
    allied_armies = enemy_armies
    percent = 0
    while percent < threshold and allied_armies < max_allied_armies:
        allied_armies += 1
        percent = cumulative(0.7, allied_armies, enemy_armies)
    return allied_armies+1
    

def get_attack_odds(us, them):
    p = 0.6
    n = int(us.armies)
    k = int(them.armies)
    return cumulative(p, n, k)

def cumulative(p, n, k):
    #In n trials, return the chance of getting at least k successes
    q = 0
    for c in range(k, n):
        
        q += binomial(p, n, c)
    return q
    

def binomial(p, n, k):
    return choose(n, k) * (p ** k) * ((1-p)**(n-k))



def choose(n, k):
    if k > n or n < 0 or k < 0:
        return 1000000
    return math.factorial(n)/(math.factorial(k)*math.factorial(n-k))




