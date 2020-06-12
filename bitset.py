#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:15:58 2020

@author: Jian Wang
"""

"""
bitset.py

Written by Geremy Condra

Licensed under GPLv3

Released 3 May 2009

This module provides a simple bitset implementation
for Python.
"""

from collections.abc import Sequence
import math

class Bitset(Sequence):
    """A very simple bitset implementation for Python.

    Note that, like with normal numbers, the leftmost
    index is the MSB, and like normal sequences, that
    is 0.

    Usage:
        >>> b = Bitset(5)           //init op.
        >>> b                       //get all items
        Bitset(101)
        >>> b[:]                    //getitem op.
        [True, False, True]
        >>> b[1:3:1]                //getitem in sequence.slice
        [False, True]
        >>> b[0] = False            //setitem op.
        Bitset(001)
        >>> b[0:3:2] = True         //setitem in sequence.slice
        Bitset(101)
        >>> b << 1                  //lshift
        Bitset(1010)
        >>> b >> 1                  //rshift
        Bitset(010)
        >>> b & 1                   //101 and 001 = 001
        Bitset(001)
        >>> b | 2                   //101 or 010 = 111
        Bitset(111)
        >>> b ^ 6                   //101 xor 110 = 011
        Bitset(011)
        >>> ~b                      //101 inverse = 010
        Bitset(010)
        >>> int(b)
        5
        >>> str(b)
        101
    """

    value = 0
    length = 0

    @classmethod
    def from_sequence(cls, seq):
        """Iterates over the sequence to produce a new Bitset.

        As in integers, the 0 position represents the LSB.
        """
        n = 0
        for index, value in enumerate(reversed(seq)):
            n += 2**index * bool(int(value))
        b = Bitset(n)
        return b

    def __init__(self, value=0, length=0):
        """Creates a Bitset with the given integer value."""
        self.value = value
        try: self.length = length or math.floor(math.log(value, 2)) + 1
        except Exception: self.length = 0

    def __and__(self, other):
        b = Bitset(self.value & int(other))
        b.length = max((self.length, b.length))
        return b

    def __or__(self, other):
        b = Bitset(self.value | int(other))
        b.length = max((self.length, b.length))
        return b

    def __invert__(self):
        b = Bitset(~self.value)
        b.length = max((self.length, b.length))
        return b

    def __xor__(self, value):
        b = Bitset(self.value ^ int(value))
        b.length = max((self.length, b.length))
        return b

    def __lshift__(self, value):
        b = Bitset(self.value << int(value))
        b.length = max((self.length, b.length))
        return b

    def __rshift__(self, value):
        b = Bitset(self.value >> int(value))
        b.length = max((self.length, b.length))
        return b

    def __eq__(self, other):
        try:
            return self.value == other.value
        except Exception:
            return self.value == other

    def __int__(self):
        return self.value

    def __str__(self):
        s = ""
        for i in self[:]:
            s += "1" if i else "0"
        return s

    def __repr__(self):
        return "Bitset(%s)" % str(self)

    def __getitem__(self, s):
        """Gets the specified position.

        Like normal integers, 0 represents the MSB.
        """
        try:
            start, stop, step = s.indices(len(self))
            results = []
            for position in range(start, stop, step):
                pos = len(self) - position - 1
                results.append(bool(self.value & (1 << pos)))
            return results
        except:
            pos = len(self) - s - 1
            return bool(self.value & (1 << pos))

    def __setitem__(self, s, value):
        """Sets the specified position/s to value.

        Like normal integers, 0 represents the MSB.
        """
        try:
            start, stop, step = s.indices(len(self))
            for position in range(start, stop, step):
                pos = len(self) - position - 1
                if value: self.value |= (1 << pos)
                else: self.value &= ~(1 << pos)
            maximum_position = max((start + 1, stop, len(self)))
            self.length = maximum_position
        except:
            pos = len(self) - s - 1
            if value: self.value |= (1 << pos)
            else: self.value &= ~(1 << pos)
            if len(self) < pos: self.length = pos
        return self

    def __iter__(self):
        """Iterates over the values in the bitset."""
        for i in self[:]:
            yield i

    def __len__(self):
        """Returns the length of the bitset."""
        return self.length

    def test1(self):
        #TEST
        b6 = Bitset(6)
        b18 = Bitset(18)
        
        v6 = b6<<1
        print(b6, v6, int(v6))            # 110=6,    1100=12
        
        v18 = b18>>1
        v18[1] = True
        v18[2] = True
        v18[3] = False
        v18[4] = True
        print(b18, v18, int(v18), v18[3],        # b18=10010=18, v18=01001=9
              '\n length=', len(v18), 
              '\n v6 == v18 ?', v6==v18)

#Bitset().test1()