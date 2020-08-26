import numpy
import math
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
        print(number, name.strip())
        structNames.update({number : name.strip()})
    return structNames

# Reads first n structures within a predict.out file, returns as a list of Data objects. 
def readPredictOut(entry, n):
    structures = list()
    absForce = list()
    atomCount = 0
    i = 0
    num = 1

    while (num < n+1 and i < len(entry)):
        tmp = entry[i].split()
        if len(tmp) < 1:
            pass
        elif ("Ti" == tmp[0] or "O" == tmp[0]):
            absForce.append((tmp[4], tmp[5], tmp[6]))
            atomCount += 1
        elif ("Total" == tmp[0] and "energy" == tmp[1]):
            totalEnergy = float(tmp[3])
            relativeEnergy = float(totalEnergy) / atomCount
            newObj = Data(num, tuple(absForce), totalEnergy, relativeEnergy, atomCount)
            structures.append(newObj)
            absForce = []
            totalEnergy = 0.0
            relativeEnergy = 0.0
            atomCount = 0
            num += 1
        i += 1
    return structures

# Reads in secondary, reference predict.out file containing all structures within the original predict.out file. Returns a list of Data objects.
def prepareCanonicals(structNames, canonicalLoc, n):
    canonicals = dict()
    with open(canonicalLoc, "r") as f:
        canonicalFile = f.readlines()
    structures = readPredictOut(canonicalFile, n)
    for i in range(1, n+1):
        name = "../TiO2-xsf/structure{:04d}.xsf".format(i)
        if (len(structures) >= i-1):
            canonicals.update({name : structures[i-1]})
        else:
            print("EXCEPTION")
    print(len(canonicals))
    return canonicals

# Calculates relative energy errors as compared to reference values provided at the top of provided .xsf files. 
def calculateRelativeEnergyErrors(structs, structNames):
    absErrors = []
    for structure in structs:
        fileName = structNames.get(structure.structureNum)
        # print("A: {fileName}".format(fileName=fileName))
        # print(structure.structureNum, fileName)
        with open(fileName, "r") as f:
            canonicalEnergy = float(f.readline().split()[4]) / structure.atomCount
        # print(str(format(canonicalEnergy)), "-", str(structure.relativeEnergy), "=", str(abs(canonicalEnergy-structure.relativeEnergy)))
        # print(abs(canonicalEnergy - structure.relativeEnergy))
        absErrors.append(abs(canonicalEnergy - structure.relativeEnergy))
    return absErrors

# Calculates relative energy RMSEs as compared to reference value.
def calculateRelativeEnergyRMSE(structs, structNames):
    RMSE = 0.0
    for i, structure in enumerate(structs, start=1):
        fileName = structNames.get(structure.structureNum)
        # print("B: {fileName}".format(fileName=fileName))
        with open(fileName, "r") as f:
            canonicalEnergy = float(f.readline().split()[4]) / structure.atomCount
        RMSE += pow((structure.relativeEnergy - canonicalEnergy), 2)
    RMSE = math.sqrt(RMSE)
    return RMSE

# Calculates absolute force errors as compared to "canonical".
def calculateAbsoluteForceErrors(structs, structNames, canonicals):
    absErrors = list()
    for i, structure in enumerate(structs, start=1): #Loops through list of structure data
        for j, absForces in enumerate(structure.absoluteForce): # Loops through absolute forces of every atom in structure
            for k, absForce in enumerate(absForces): # Loops through absolute forces
                structName = structNames.get(structure.structureNum)
                absErrors.append(abs(float(absForce)) - float(canonicals.get(structName).absoluteForce[j][k]))
    return absErrors

def main():
    predictOutFiles = []
    predictEntries = []
    structureFiles = []
    energies = []
    predictData = []
    relativeEnergyErrors = []
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
        print(len(predictData[i]))
        canonicals = prepareCanonicals(structNames, canonicalFile, 7815)
        relativeEnergyErrors.append(calculateRelativeEnergyErrors(predictData[i], structNames))
        print(sum(relativeEnergyErrors[i])/7815)
        print("RMSE: {a}".format(a=calculateRelativeEnergyRMSE(predictData[i], structNames)))
        print(len(calculateAbsoluteForceErrors(predictData[i], structNames, canonicals)))



main()
