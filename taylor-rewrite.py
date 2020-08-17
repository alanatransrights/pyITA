import numpy
import sys
import os

global delta = 0

class Structure:
    def __init__(self, energy, atoms, isPeriodic):
        self.energy = energy # Float
        self.atoms = atoms # Array of objects
        self.isPeriodic = isPeriodic # Boolean
    
    def build_new_structure(self, atomIndex, direction, sign):
        newStructure = Structure(energy, atoms, isPeriodic) # Build new struct
        targetAtom = newStructure.atoms[atomIndex] # Fetch target atom
        if newStructure.energy
            newStructure.energy -= delta * targetAtom.forces.get(direction) # Deduct energy of new structure
        elif
        newStructure.atoms[atomIndex] = targetAtom.displace(direction, sign) # Replace atom of new structure
        return newStructure

class Atom:
    def __init__(self, symbol, coordinates, forces):
        self.symbol = symbol # String, atomic symbol
        self.coordinates = coordinates # Dictionary
        self.forces = forces # Dictionary
    def displace(self, direction, sign):
        if sign == "+":
            self.coordinates[direction] += delta
        elif sign == "-":
            self.coordinates[direction] -= delta
        else:
            sys.exit("No sign specified for atom shift")

class Generate_In:
    # WISHLIST: topLines should not be necessary. 
    def __init__(self, structLocs, topLines):
        self.structLocs = structLocs # Locations of all .xsf files (array of strings)
        self.topLines = topLines # Every line before "FILES" (array of strings)
        break

def main():
    global delta = input("enter delta (float): ")
    oldGenLoc = input("enter full path to existing generate.in (str): ") # input generate.in location
    newGenLoc = input("enter full desired path new generate.in (str): ") # new generate.in location
    newStructsDir = input("enter full desired path to directory for new .xsf (str): ") # folder for new .xsfs
    aValue = input("enter desired A-value (A * size of existing dataset = size of additional dataset): ")

    if aValue < 1:
        sys.exit("A-Value MUST >= 1")

    oldGen = read_generate_in(oldGenLoc) # Object
    structLocs = oldGen.structLocs
    oldStructs = []
    newStructs = []
    oldStructCount = 0

    for xsf in structLocs:
        oldStructs.append(read_xsf_to_Structure(xsf))
        oldStructsCount += 1

    newStructsCount = 0
    newStructsMax = aValue * oldStructsCount

    for structure in oldStructs: 
        for index, atom in enumerate(structure.atoms):
            for direction in "xyz":
                for sign in "+-":
                    if newStructsCount < newStructsMax:
                        tmp = structure.build_new_structure(index, direction, sign)
                        newStructs.append(tmp)
                        newStructsCount++
    
    totalStructsCount = oldStructsCount + newStructsCount

    write_xsf_files(newStructsDir, newStructs)
    write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount)

def read_generate_in(oldGenLoc):
    with open(generate_in.strip(), 'r') as f:
        genRead = f.readlines()

    fileCountIndex = -1
    fileStartIndex = -1

    for index, line in enumerate(genRead):
        if (line.strip() == "FILES"):
            lastTopIndex = index - 1
            fileCountIndex = index + 1
            fileStartIndex = index + 2
    else:
        print("Error: Generate.in file not found at provided location.")

    for i in range(fileStartIndex, len(genRead)):
        files.append(genRead[i].strip())

    fileCount = int(genRead[fileCountIndex].strip())

def read_xsf_to_Structure(xsf):
    # TODO Create array of Atom s with respective symbols, coordinates, and forces for each structure.
    # TODO Create object of Structure with energy, array of atoms, and isPeriodic
    break

def write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount):
    # TODO
    break

def write_xsf_files(newStructsDir, newStructs):
    # TODO
    break
