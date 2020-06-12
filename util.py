#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:36:28 2020

@author: Jian Wang
"""

import bitset as bst
from time import sleep 

class Utility:

    @staticmethod
    def getCopy(bset, totalBits):
        newset = bst.Bitset(0, totalBits)
        for i in range(totalBits):
            newset[i] = bset[i]
        return newset
    
    @staticmethod
    def toInteger(bset, totalBits):
        acc = 0
        for i in range(totalBits):
            #if bset.get(totalBits - i - 1):
            if bset[totalBits - i - 1]:
                acc += (1 << i)
        return acc

    @staticmethod
    def toBitSet(value, totalBits):
        idx = totalBits - 1
        result = bst.Bitset(0, totalBits)
        while value > 0:
            #result.set(idx, value % 2 == 1)
            result[idx] = (value % 2 == 1)
            value //= 2
            idx -= 1
        return result

    @staticmethod    
    def progbar(curr, total, full_progbar):
        frac = curr/total
        filled_progbar = round(frac*full_progbar)
        print('\r', '#'*filled_progbar + '-'*(full_progbar-filled_progbar), '[{:>7.2%}]'.format(frac), end='')

    @staticmethod    
    def test1():
        bso = Utility.toBitSet(0xabcd, 16)
        val = Utility.toInteger(bso, 16)
        print(val)

    @staticmethod
    def test2():
        for i in range(100+1):
            Utility.progbar(i, 100, 30)
            sleep(0.02)
        print()

#Utility.test1()
#Utility.test2()


