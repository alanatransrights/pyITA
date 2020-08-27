import numpy
import math
import sys
import os
from pprint import pprint
import copy
import statistics

class Data:
    def __init__(self, structureNum = 0, absForce = tuple(), totalEnergy = 0.0, relativeEnergy = 0.0, atomCount = 0, name = ""):
        self.structureNum = structureNum
        self.absoluteForce = absForce
        self.totalEnergy = totalEnergy
        self.relativeEnergy = relativeEnergy
        self.atomCount = atomCount
        self.name = name

class Structure:
    def __init__(self, relativeEnergyError = 0.0, name = ""):
        self.relativeEnergyError = relativeEnergyError
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

# Calculates relative energy RMSEs as compared to reference value.
def calculateRelativeEnergyRMSE(relativeEnergyErrors):
    RMSE = 0.0
    for error in relativeEnergyErrors:
        RMSE += pow(error, 2)
    RMSE = math.sqrt(RMSE)
    return RMSE

# Calculates absolute force errors as compared to "canonical".
def calculateAbsoluteForceErrors(structs, structNames, canonicals):
    absErrors = list()
    for i, structure in enumerate(structs, start=1): #Loops through list of structure data
        for j, absForces in enumerate(structure.absoluteForce): # Loops through absolute forces of every atom in structure
            for k, absForce in enumerate(absForces): # Loops through absolute forces
                structName = structNames.get(structure.structureNum)
                absErrors.append(abs(float(absForce) - float(canonicals.get(structName).absoluteForce[j][k])))
    return absErrors

def readSavedEnergies(dataEntry):
    structures = list()
    for i in range(len(dataEntry)):
        tmp = dataEntry[i].split()
        if len(tmp) < 1:
            continue 
        if "../TiO2-xsf/" in tmp[9]:
            structures.append(Structure(float(tmp[5]), tmp[9].strip()))
    return structures

def main():
    tmp = ""
    dataLocs = []
    dataFiles = []
    readEntries = []
    structures = []
    absRelativeEnergyErrors = []
    RMSEs = []
    relativeErrorsCount = 0
    absRelEn = []

    while True:
        tmp = input("Enter validation save_energies data loc: ")
        if tmp == "":
            break
        dataLocs.append(tmp)

    canonicalLocation = input("EXPERIMENTAL: Enter canonical file loc: ")

    for i, elem in enumerate(dataLocs):
        with open(elem, "r") as f:
            dataFiles.append(f.readlines())
        # canonicals = prepareCanonicals(structNames, canonicalFile, 7815)
        readEntries.append(readSavedEnergies(dataFiles[i]))
        print(type(readEntries[i]))
        absRelativeEnergyErrors.append([])

        for structure in readEntries[i]:
            absRelativeEnergyErrors[i].append(abs(structure.relativeEnergyError))
            relativeErrorsCount += 1
        
        print(statistics.median(absRelativeEnergyErrors[i]))
        print(statistics.mean(absRelativeEnergyErrors[i]))
        absRelEn.extend(absRelativeEnergyErrors[i])
        RMSEs.append(calculateRelativeEnergyRMSE(absRelativeEnergyErrors[i]))
        print("RMSE: {a}".format(a=calculateRelativeEnergyRMSE(absRelativeEnergyErrors[i])))
        # print(sum(calculateAbsoluteForceErrors(predictData[i], structNames, canonicals))/len(calculateAbsoluteForceErrors(predictData[i], structNames, canonicals)))
    print(statistics.median(absRelEn))
    # print(median(RMSEs))

main()
