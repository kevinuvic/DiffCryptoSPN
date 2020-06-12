#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:36:28 2020

@author: Jian Wang
"""
import numpy as np
import random as rdm
import spncipher as spn
import bitset as bst
from util import Utility as utl
from builtins import staticmethod
from numpy import dtype

# Differential Cryptanalysis on SPN Cipher
class DiffCryptSPN:

    def DifferentialCryptoanalysis (self):
        print("Differential Attack on Simple S-Box")
        return

    # 5 spnkeys
    spnKey = []
    #print("Number of Plain/Cipher text:");
    noPair = 5000

    #Partial Subkey Value Matrix
    PSVM = np.zeros((16,16), dtype=int)    # dtype='<U21')  # dtype=str)
    

    def __init__(self, pcPair = 5000, keys = [0x1234, 0x5678, 0x9ABC, 0xDEF0, 0xABCD]):
        self.spnKey = []
        for i in range(5): 
            self.spnKey.append(bst.Bitset(keys[i], 16))
        
        key5 = self.spnKey
        print ('\n\n5 keys = ', hex(int(key5[0])), hex(int(key5[1])), hex(int(key5[2])), hex(int(key5[3])), hex(int(key5[4])))
        
        self.noPair = pcPair
        print ('Plain/Cipher text pair = ', pcPair, '\n')
    
    def generateCipherPairs(self, subRoundKeys, noPairs, deltaPlaintext):
        sBox = spn.SpnCipher()
        
        sets = [[]]
        for i in range(noPairs):
            # plain cipher 1
            p1 = utl.toBitSet(rdm.randint(0, 0xffff), 16)
            c1 = sBox.Encrypt(p1, subRoundKeys)

            # another plain-cipher satisfy deltaPlaintext e.g [0000 1011 0000 0000]
            p2 = utl.getCopy(p1, 16)
            p2 ^= utl.toBitSet(deltaPlaintext, 16)
            c2 = sBox.Encrypt(p2, subRoundKeys)
            
            if i>0: sets.append([c1,c2])
            else: sets[0] = [c1,c2]
        return sets

    
    def partialSubkeyDecrypt(self, partialc, partialk):
        partialc = utl.getCopy(partialc, 4)
        partialc ^= partialk
        sbc = spn.SpnCipher()
        return sbc.getSBoxInv(partialc)

    def DoCryptanalysis(self, deltaPlaintext, subKeyPair, delOutput):


        cipherPairs = self.generateCipherPairs(self.spnKey, self.noPair, deltaPlaintext)

        #Statistic the difference
        myCounts = self.ComputeDiff(cipherPairs, subKeyPair, delOutput)

        #Compute the prob. of occurrence of pairs
        k1, k2, highProb = self.ComputProb(myCounts)

        print('\n subkey', subKeyPair[0], '=' , hex(k1),
              '\n subkey', subKeyPair[1], '=', hex(k2))
        print('count=', myCounts[k1][k2], 'Prob=', highProb)
        if (self.PSVM.shape[0] == 16):
            self.PSVM = np.vstack([self.PSVM, np.arange(16)])     #add 1 row
            self.PSVM = np.hstack([self.PSVM, np.arange(17).reshape(16+1,1)])     #add 1 column
        print(self.PSVM)

        return k1, k2

    def ComputProb(self, myCounts):
        highProb = float(0)
        k1 = int(0)
        k2 = int(0)
        for i in range(16):
            for j in range(16):
                count = myCounts[i][j];
                prob = count / float(self.noPair)
                self.PSVM[j][i] = count# + '/' + str(prob)
                if prob > highProb:
                    highProb= prob
                    k1 = i
                    k2 = j
        return k1, k2, highProb

    def ComputeDiff(self, cipherPairs, subKeyPair, delOutput):
        #Init 16*16 myCounts matrix
        myCounts = np.zeros((16,16), dtype=np.int32)

        iprogress = 0
        for cPair in cipherPairs:
            if iprogress % 30 == 0 : utl.progbar(iprogress, self.noPair, 50)
            iprogress+=1

            c1 = cPair[0]
            c2 = cPair[1]

            st1 = subKeyPair[0]*4
            sp1 = st1 + 4
            st2 = subKeyPair[1]*4
            sp2 = st2 + 4

            for i in range(16):
                for j in range(16):
                    pSubkeyA = utl.toBitSet(i, 4)
                    pSubkeyB = utl.toBitSet(j, 4)

                    #pSubkeyA, e.g bits 4 to 8
                    pCipherA1 = c1[st1:sp1:1]
                    a1Assumption = self.partialSubkeyDecrypt(pCipherA1,
                            pSubkeyA);
                    pCipherA2 = c2[st1:sp1:1];
                    a2Assumption = self.partialSubkeyDecrypt(pCipherA2,
                            pSubkeyA);
                    deltaA = utl.getCopy(a1Assumption, 4)
                    deltaA ^= a2Assumption

                    #pSubkeyA, e.g bits 12-16
                    pCipherB1 = c1[st2:sp2:1];
                    b1Assumption = self.partialSubkeyDecrypt(pCipherB1,
                            pSubkeyB);
                    pCipherB2 = c2[st2:sp2:1];
                    b2Assumption = self.partialSubkeyDecrypt(pCipherB2,
                            pSubkeyB);
                    deltaB =  utl.getCopy(b1Assumption, 4)
                    deltaB ^= b2Assumption

                    #deltaPlaintext e.g. key bits [0000 0110 0000 0110]
                    if (deltaA == delOutput[subKeyPair[0]]) \
                        and (deltaB == delOutput[subKeyPair[1]]):
                        myCounts[i][j] += 1

        utl.progbar(self.noPair, self.noPair, 50)

        return myCounts

    def ComputeDiffCharacteristic(self, seed = 0x0b00):
        SBox = spn.SpnCipher()
        
        rst = bst.Bitset(seed, 16)
        print('S1.DC.X = ', hex(int(rst)))
        rst = SBox.getSBoxGroup(rst)
        print('S1.DC.Y = ', hex(int(rst)))

        rst = SBox.permuteBits(rst)
        print('S2.DC.X = ', hex(int(rst)))
        rst = SBox.getSBoxGroup(rst)
        print('S2.DC.Y = ', hex(int(rst)))
        rst = SBox.permuteBits(rst)

        rst = SBox.permuteBits(rst)
        print('S3.DC.X = ', hex(int(rst)))
        rst = SBox.getSBoxGroup(rst)
        print('S3.DC.Y = ', hex(int(rst)))

        rst = SBox.permuteBits(rst)
        print('S4.DC.X = ', hex(int(rst)))
        
        return

    def sampleTest(self):
        k1, k3 = self.DoCryptanalysis(0x0B00, (1,3), (0, 0b0110, 0, 0b0110))
        k0, k2 = self.DoCryptanalysis(0x000D, (0,2), (0b1010, 0, 0b1010, 0))
        
        print("\n the cryptanalysis last round key = ", k0,k1,k2,k3, '=', hex(k0),hex(k1),hex(k2), hex(k3))
        print("the original last round key = ", hex(int(self.spnKey[4])))

        #self.DoCryptanalysis2()

DiffCryptSPN(1000).sampleTest()
#DiffCryptSPN(2000, [0x1122, 0x3344, 0x5566, 0x7788, 0x9ABC]).sampleTest()
#DiffCryptSPN().ComputeDiffCharacteristic()



