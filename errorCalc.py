import numpy
import sys
import os
from pprint import pprint
import copy

class Data:
    def __init__(self, structureNum = 0, absForce = tuple(), totalEnergy = 0.0, relativeEnergy = 0.0, atomCount = 0, name = ""):
        self.structureNum = structureNum
        self.absoluteForce = absForce
        self.totalEnergy = totalEnergy
        self.relativeEnergy = relativeEnergy
        self.atomCount = atomCount
        self.name = name

def readPredictIn(predictInLoc):
    structNames = dict()
    with open(predictInLoc, "r") as f:
        predictIn = f.readlines()
    for i, line in enumerate(predictIn):
        if line.strip() == "FILES":
            fileNames = predictIn[i+2:len(predictIn)]
    for number, name in enumerate(fileNames, start=1):
        structNames.update({number : name.strip()})
    return structNames

def readPredictOut(entry, n):
    structures = []
    absForce = []
    atomCount = 0
    print("NUMS")
    for num in range(1, n+1): #Fixed error, now terminates at n
        for i in range(0, len(entry)):
            print(entry[i])
            tmp = entry[i].split()
            print(tmp)
            if len(tmp) < 1:
                continue
            elif ("Ti" == tmp[0] or "O" == tmp[0]):
                print("has Ti or O")
                absForce.append((tmp[4], tmp[5], tmp[6]))
                atomCount += 1
            elif ("Total" == tmp[0] and "energy" == tmp[1]):
                print("has Total energy")
                totalEnergy = float(tmp[3])
                relativeEnergy = float(totalEnergy) / atomCount
                newObj = Data(num, tuple(absForce), totalEnergy, relativeEnergy, atomCount)
                print(newObj)
                structures.append(newObj)
                absForce = []
                totalEnergy = 0.0
                relativeEnergy = 0.0
                atomCount = 0
                i += 1
    print(structures)
    return structures

def prepareCanonicals(structNames, canonicalLoc, n):
    canonicals = dict()
    print("CANONICALS")
    for i in range(1, n+1):
        name = structNames.get(i)
        structures = readPredictOut(canonicalLoc, 7715)
        print(i, structures)
        canonicals.update({name : structures[i-1]})
    return canonicals

def calculateRelativeEnergyErrors(structs, structNames):
    absErrors = []
    for structure in structs:
        fileName = structNames.get(structure.structureNum)
        print(structure.structureNum, fileName)
        with open(fileName, "r") as f:
            canonicalEnergy = float(f.readline().split()[4]) / structure.atomCount
        absErrors.append(abs(canonicalEnergy - structure.relativeEnergy))
    return absErrors

def calculateAbsoluteForceErrors(structs, structNames, canonical):
    absErrors = []
    for i, structure in enumerate(structs, start=1):
        for j, absForce in enumerate(structure.absoluteForce):
            absErrors.append(abs(float(absForce) - canonical.get(structNames.get(i)).absoluteForce[j]))
    return absErrors 

def calculateRelativeEnergyRMSE(structs, structNames, canonical):
    RMSE = 0.0
    for i, structure in enumerate(structs, start=1):
        RMSE += pow((structure.relativeEnergy - canonical.get(structNames.get(i)).relativeEnergy), 2)
    RMSE = sqrt(RMSE)
    return RMSE

def main():
    predictOutFiles = []
    predictEntries = []
    structureFiles = []
    energies = []
    predictData = []
    tmp = ""

    tmp = input("Enter predict.in file loc: ")
    structNames = readPredictIn(tmp)

    while tmp != "":
        tmp = input("Enter next predict.out file loc: ")
        if tmp == "":
            continue
        predictOutFiles.append(tmp)

    canonicalFile = input("Enter canonical file loc: ")

    print(predictOutFiles)
    for i, elem in enumerate(predictOutFiles):
        with open(elem, "r") as f:
            predictEntries.append(f.readlines())
        predictData.append(readPredictOut(predictEntries[i], 500))
        # canonical = prepareCanonicals(structNames, canonicalFile, 500)
        # print(calculateRelativeEnergyErrors(predictData[i], structNames))
        # print(calculateAbsoluteForceErrors(predictData[i], structNames, canonical))
        # print(calculateRelativeEnergyRMSE(predictData[i], structName, canonical))

main()
