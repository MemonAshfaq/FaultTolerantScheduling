'''
Created on 5 Apr 2019

@author: aspak.rogatiya
'''
import fractions

def _lcm(a,b): return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    return reduce(_lcm, a)