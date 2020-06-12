#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:45:20 2020

@author: Jian Wang
"""

import bitset as bst
from util import Utility as utl
from builtins import staticmethod
import numpy as np


class SpnCipher:
    
    SBoxTbl = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
    SBoxInvTbl = [14, 3, 4, 8, 1, 12, 10, 15, 7, 13, 9, 6, 11, 2, 0, 5]
    PermuteTbl = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]

    def __init__(self):
        pass
    
    def getSBox(self, bits4):
        # idx = utl.toInteger(bSet, 4)
        idx = int(bits4)
        return utl.toBitSet(self.SBoxTbl[idx], 4)

    def getSBoxInv(self, bits4):
        # idx = utl.toInteger(bSet, 4)
        idx = int(bits4)
        return utl.toBitSet(self.SBoxInvTbl[idx], 4)

    def getSBoxGroup(self, bits16):
        result = bst.Bitset(0, 16)

        for i in range(4):
            toSBox = bst.Bitset(0, 4)
            for j in range(4):
                # toSBox.set(j, bSet.get(i * 4 + j))
                toSBox[j] = bits16[i * 4 + j]
        
            fromSBox = self.getSBox(toSBox)
            for j in range(4):
                result[i * 4 + j] = fromSBox[j]
            
        return result

    def getSBoxInvGroup(self, bits16):
        result = bst.Bitset(0, 16);
        for i in range(4):
            toSBox = bst.Bitset(0, 4)
            for j in range(4):
                toSBox[j] = bits16[i * 4 + j]

            fromSBox = self.getSBoxInv(toSBox)
            for j in range(4):
                result[i * 4 + j] = fromSBox[j]

        return result

    def permuteBits(self, bits16):
        bSetPerm = bst.Bitset(0, 16)
        for i in range(16):
            bSetPerm[self.PermuteTbl[i]] = bits16[i]
            
        return bSetPerm

    def EncRound(self, ptBits, keyBits, permute=False):
        ptBits ^= keyBits
        ctBits = self.getSBoxGroup(ptBits)
        if permute:
            ctBits = self.permuteBits(ctBits)
        return ctBits

    def DecRound(self, ctBits, keyBits, permute=False):
        if permute:
            ctBits = self.permuteBits(ctBits)
        ptBits = self.getSBoxInvGroup(ctBits)

        ptBits ^= keyBits
        return ptBits;

    def Encrypt(self, ptBits, roundKeys):
        #ptBits = utl.getCopy(ptBits, 16)
        for i in range(4):
            ptBits = self.EncRound(ptBits, roundKeys[i], i != 3)
        ptBits ^= roundKeys[4]
        return ptBits

    def Decrypt(self, ctBits, roundKeys):
        #ctBits = utl.getCopy(ctBits, 16);
        ctBits ^= roundKeys[4]
        for i in range(3, -1, -1):
            ctBits = self.DecRound(ctBits, roundKeys[i], i != 3)
        return ctBits

    def partialEncrypt(self, ctBits, roundKey=0, roundNo=3):
        #ctBits ^= roundKey;
        ctBits = self.EncRound(ctBits, roundKey, roundNo != 3)
        return ctBits

    def partialDecrypt(self, ctBits, roundKey, roundNo):
        #ctBits ^= roundKey;
        ctBits = self.DecRound(ctBits, roundKey, roundNo != 3)
        return ctBits

    #get Diff Pair in 4 bits
    def getDiffPair4(self):
        X = np.arange(16, dtype=bst.Bitset)
        Y = np.zeros(16, dtype=bst.Bitset)
        for i in range(16): 
            X[i] = utl.toBitSet(i, 4)
            Y[i] = self.getSBox(X[i])
        
        # Difference Pair Matrix
        dpm = np.zeros(16*16, dtype=int).reshape(16,16)
        dp = np.zeros(16, dtype=int)
        for i in range(16):
            for j in range(16):
                dx = utl.toBitSet(j, 4)
                Xprm = X[i] ^ dx
                Yprm = Y[i] ^ Y[int(Xprm)]
                #jj = int(dx)
                val = int(Yprm)
                dpm[i][j] = val
            # stat the high prob

        for j in range(16):
            #dp[j] = np.max(dpm[:,j])
            col = dpm[:,j]
            counts = np.bincount(col)   #count occurrence of 0..array_max (e.g. bincount([0, 1, 1])=[0:1, 1:2, 2:0])
            mx = np.argmax(counts)
            dp[j] = mx            

        #get DDT (Diff Distribution Table) of SBox
        ddt = np.zeros(16*16, dtype=int).reshape(16,16)
        for i in range(16):
            #unique, counts = np.unique(dpm[:,i], return_counts=True)
            #counts = np.pad(counts, (0,16-counts.shape[0]))
            counts = np.bincount(dpm[:,i])
            counts = np.pad(counts, (0,16-counts.shape[0]))
            ddt[i, :] = counts
            
        return dp, dpm, ddt

    #Diff Pair in 16 bits
    def getDiffPair16(self, seed16, dp):
        X = utl.toBitSet(0xF000, 16)
        Y = utl.toBitSet(seed16, 16)
        Z = utl.toBitSet(0, 16)
        for i in range(4):
            sb = int(X & Y) >> (4-1 - i) * 4
            sb = int(dp[sb])
            sb = sb << (4-1 - i) * 4
            Xpm = utl.toBitSet(sb, 16)
            Z = Xpm | Z
            X = X >> 4

        return Z

    def getLastRoundDiffPair(self, dp, seed):
        print('delta P =', "{0:#0{1}X}".format(seed,6))

        print('       ____....____....')
        print('U1 =', "{0:#0{1}b}".format(int(seed),18), "= {0:#0{1}X}".format(seed,6))
        z = self.getDiffPair16(seed, dp)
        print('V1 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(z)))

        z = self.permuteBits(z)
        print('U2 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(seed)))
        z = self.getDiffPair16(int(z), dp)
        print('V2 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(z)))
        
        z = self.permuteBits(z)
        print('U3 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(seed)))
        z = self.getDiffPair16(int(z), dp)
        print('V3 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(z)))

        z = self.permuteBits(z)
        print('U4 =', "{0:#0{1}b}".format(int(z),18), "= {0:#0{1}X}".format(int(z),6))   #bin(int(seed)))


    def test1(self):
        ptext = utl.toBitSet(0x2345, 16)
        sub1 = self.getSBoxGroup(ptext)
        print('substitution:', utl.toInteger(sub1, 16), '-', int(sub1))
        
        print('permutation: ', int(self.permuteBits(ptext)))
        
        sub1 = self.getSBoxGroup(utl.toBitSet(0x1234, 16))
        sub2 = self.getSBoxGroup(utl.toBitSet(0x5678, 16))
        subinv3 = self.getSBoxInvGroup(utl.toBitSet(0x9abc, 16))
        print('permutation: ', int(sub1), " - ", int(sub2))
        print('subinv: ', int(subinv3))
    
    #Test encrypt/decrypt
    def test2(self):
        spnKey = [bst.Bitset(0x1234, 16), bst.Bitset(0x5678, 16), bst.Bitset(0x9ABC, 16), 
              bst.Bitset(0xDEF0, 16), bst.Bitset(0x1357, 16)]
        pt = 0x1234
        ctenc = self.Encrypt(utl.toBitSet(pt, 16), spnKey)  
        #ctenc = utl.toBitSet(0x52C0, 16)
        ptdec = self.Decrypt(ctenc, spnKey)
        print('Step1: Encrypt(0x1234) = ', hex(int(ctenc)), 
              '\nStep2:          Decrypt(',hex(int(ctenc)),') = ', hex(int(ptdec)), 
              '\nStep3: The original plaintext = ', hex(pt), ', it equals to the result of Step2')
    
    #Test encrypt/decrypt
    def test3(self):
        spnKey = [bst.Bitset(0x1234, 16), bst.Bitset(0x5678, 16), bst.Bitset(0x9ABC, 16), 
              bst.Bitset(0xDEF0, 16), bst.Bitset(0x1357, 16)]
        # process of encrypting
        #deltaX = utl.toBitSet(0x0b00, 16)
        deltaX = utl.toBitSet(0x1234, 16)
        for i in range(4):
            deltaY = self.partialEncrypt(deltaX, spnKey[i], i)
            print('y', i+1, '=', hex(int(deltaY)))
            deltaX = deltaY
        deltaY ^= spnKey[4]
        print('y5 = ', hex(int(deltaY)))

        # process of encrypting
        deltaY ^= spnKey[4]
        print('x4 = ', hex(int(deltaY)))
        for i in range(3, -1, -1):
            deltaX = self.partialDecrypt(deltaY, spnKey[i], i)
            print('x', i, '=', hex(int(deltaX)))
            deltaY = deltaX

    def test4(self):
        deltaX = utl.toBitSet(0x0b00, 16)

        dY = self.getSBoxGroup(deltaX)
        print(hex(int(dY)))
        
        print('dX = ', hex(int(deltaX)))
        for i in range(4):
            deltaY = self.partialEncrypt(deltaX)
            print('y', i+1, '=', hex(int(deltaY)))
            deltaX = deltaY
    
    def test5(self):
        dp, dpm, ddt = self.getDiffPair4()
        print('Diff Pair = \n', dp)
        #print(dpm)
        print('\nDDT (Difference Distribution Table) = \n', ddt)
    
    def test6(self):
        dp = self.getDiffPair4()
#        print('delta P = 0xB000')
#        self.getLastRoundDiffPair(dp, 0xB000)  # 0b0000 1011 0000 1011
        self.getLastRoundDiffPair(dp, 0x0B00)  # 0b0000 0110 0000 0110
#         print('seed = 0x00B0')
#         self.getLastRoundDiffPair(dp, 0x00B0)  # 0b0000 0101 0000 0101
#         print('seed = 0x000B')
#         self.getLastRoundDiffPair(dp, 0x000B)  # 0b0000 1010 0000 1010

#         print('seed = 0xD000')
#         self.getLastRoundDiffPair(dp, 0xD000)  # 0b1011 0000 1011 0000
#         print('seed = 0x0D00')
#         self.getLastRoundDiffPair(dp, 0x0D00)  # 0b0110 0000 0110 0000
#         print('seed = 0x00D0')
#         self.getLastRoundDiffPair(dp, 0x00D0)  # 0b0101 0000 0101 0000
        print('\n')
        self.getLastRoundDiffPair(dp, 0x000D)  # 0b1010 0000 1010 0000


#         print('seed = 0x1000')
#         self.getLastRoundDiffPair(dp, 0x1000)
#         print('seed = 0x0100')
#         self.getLastRoundDiffPair(dp, 0x0100)
#         print('seed = 0x0010')
#         self.getLastRoundDiffPair(dp, 0x0010)
#         print('seed = 0x0001')
#         self.getLastRoundDiffPair(dp, 0x0001)
# 
#         print('seed = 0x2000')
#         self.getLastRoundDiffPair(dp, 0x2000)
#         print('seed = 0x0200')
#         self.getLastRoundDiffPair(dp, 0x0200)
#         print('seed = 0x0020')
#         self.getLastRoundDiffPair(dp, 0x0020)
#         print('seed = 0x0002')
#         self.getLastRoundDiffPair(dp, 0x0002)
# 
#         print('seed = 0x3000')
#         self.getLastRoundDiffPair(dp, 0x3000)
#         print('seed = 0x0300')
#         self.getLastRoundDiffPair(dp, 0x0300)
#         print('seed = 0x0030')
#         self.getLastRoundDiffPair(dp, 0x0030)
#         print('seed = 0x0003')
#         self.getLastRoundDiffPair(dp, 0x0003)
# 
#         print('seed = 0x4000')
#         self.getLastRoundDiffPair(dp, 0x4000)
#         print('seed = 0x0400')
#         self.getLastRoundDiffPair(dp, 0x0400)
#         print('seed = 0x0040')
#         self.getLastRoundDiffPair(dp, 0x0040)
#         print('seed = 0x0004')
#         self.getLastRoundDiffPair(dp, 0x0004)
# 
#         print('seed = 0x0005')
#         self.getLastRoundDiffPair(dp, 0x0005)
#         print('seed = 0x0006')
#         self.getLastRoundDiffPair(dp, 0x0006)
#         print('seed = 0x0007')
#         self.getLastRoundDiffPair(dp, 0x0007)
#         print('seed = 0x0008')
#         self.getLastRoundDiffPair(dp, 0x0008)
#         print('seed = 0x0009')
#         self.getLastRoundDiffPair(dp, 0x0009)
#         print('seed = 0x000A')
#         self.getLastRoundDiffPair(dp, 0x000A)
#         print('seed = 0x000C')
#         self.getLastRoundDiffPair(dp, 0x000C)
#         print('seed = 0x000D')
#         self.getLastRoundDiffPair(dp, 0x000D)     #*********** [1010 0000 1010 0000]
#         print('seed = 0x000E')
#         self.getLastRoundDiffPair(dp, 0x000E)


#SpnCipher().test1()
#SpnCipher().test2()
#SpnCipher().test3()
#SpnCipher().test4()
#SpnCipher().test5()
#SpnCipher().test6()

#SpnCipher().test5()

