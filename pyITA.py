import numpy
import sys
import os
import pprint
import copy

delta = 0

class Atom:
    def __init__(self, symbol, coordinates, forces):
        self.symbol = symbol # String, atomic symbol
        self.coordinates = coordinates # Dictionary
        self.forces = forces # Dictionary
    def displace(self, direction, sign):
        tmp = {}
        if sign == "+":
            tmp = {direction : self.coordinates.get(direction) + delta}
        elif sign == "-":
            tmp = {direction : self.coordinates.get(direction) - delta}
        else:
            sys.exit("No sign specified for atom shift")
        self.coordinates.update(tmp)

class Structure:
    def __init__(self, energy = 0.0, atoms = None, isPeriodic = True, coordCount = 0, primVec = tuple()): 
        self.energy = energy 
        self.atoms = atoms if (atoms is not None) else list()
        self.isPeriodic = isPeriodic
        self.coordCount = coordCount
        self.primVec = primVec

class Generate_In:
    # WISHLIST: topLines should not be necessary. 
    def __init__(self, structLocs = [], topLines = []):
        self.structLocs = structLocs # Locations of all .xsf files (array of strings)
        self.topLines = topLines # Every line before "FILES" (array of strings)

def main():
    print("began main")
    global delta
    delta = float(input("enter delta (float): "))
    oldGenLoc = input("enter full path to existing generate.in (str): ") # input generate.in location
    newGenLoc = input("enter full desired path new generate.in (str): ") # new generate.in location
    newStructsDir = input("enter full desired path to directory for new .xsf (str): ") # folder for new .xsfs
    aValue = float(input("enter desired A-value (A * size of existing dataset = size of additional dataset): "))

    if aValue < 1:
        sys.exit("A-Value MUST >= 1")

    oldGen = read_generate_in(oldGenLoc) # Object
    structLocs = oldGen.structLocs
    oldStructs = []
    newStructs = []
    oldStructsCount = 0

    print("Reading XSF files")
    for i, xsf in enumerate(structLocs):
        oldStructs.append(read_xsf_to_Structure(xsf))
        oldStructsCount += 1

    newStructsCount = 0
    newStructsMax = aValue * oldStructsCount

    for structure in oldStructs:
        for index, atom in enumerate(structure.atoms):
            for sign in ["+", "-"]:
                for direction in ["x", "y", "z"]:
                    if (newStructsCount < newStructsMax):
                        if isinstance(structure.atoms[index], Atom):
                            tmp = build_new_structure(structure, index, direction, sign)
                            newStructs.append(tmp)
                            newStructsCount += 1
                        else:
                            sys.exit("not isinstance, instead, type is: " + str(type(structure.atoms[index])))

    totalStructsCount = oldStructsCount + newStructsCount
    write_xsf_files(newStructsDir, newStructs)
    write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount, newStructsCount)

def build_new_structure(struct, atomIndex, direction, sign):
    """
    TODO: Figure out why modifications to targetAtom (targetAtom.displace()) is affecting the non-target atoms. Suspected
    line is "targetAtom = newStructure.atoms[atomIndex]". Make sure to pass by value.
    """
    newStructure = Structure(struct.energy, copy.deepcopy(struct.atoms), struct.isPeriodic, struct.coordCount, struct.primVec) # Build new struct
    targetAtom = newStructure.atoms[atomIndex] # fetch target atom
    if isinstance(targetAtom, Atom):
        if sign == "+":
            newStructure.energy -= delta * targetAtom.forces.get(direction) # deduct energy of new structure
        elif sign == "-":
            newStructure.energy += delta * targetAtom.forces.get(direction) # add energy to new structure
        else:
            print("no sign specified")
            sys.exit()
        targetAtom.displace(direction, sign)
        if targetAtom == struct.atoms[atomIndex]:
            print("AAAAAAAAAA PANIC")
        newStructure.atoms[atomIndex] = targetAtom
    else:
        print("targetatom in build_new_structure is not atom")
    return newStructure

def read_generate_in(oldGenLoc):
    print("reading gen in")
    oldGen = Generate_In()
    fileCountIndex = -1
    fileStartIndex = -1

    with open(oldGenLoc.strip(), 'r') as f:
        genRead = f.readlines()

    for index, line in enumerate(genRead):
        oldGen.topLines.append(line)
        if (line.strip() == "FILES"):
            fileCountIndex = index + 1
            fileStartIndex = index + 2
            break
    else:
        print("Error: Generate.in file not found at provided location.")

    for i in range(fileStartIndex, len(genRead)):
        oldGen.structLocs.append(genRead[i].strip())
    
    return oldGen

def read_xsf_to_Structure(xsf):
    structure = Structure()

    with open(xsf.strip(), 'r') as f:
        xsfRead = f.readlines()

    structure.energy = float(xsfRead[0].split()[4])
    
    for index, line in enumerate(xsfRead):
        if (line.strip() == "ATOM"):
            structure.isPeriodic = False
            atomStartIndex = index + 1
        elif (line.strip() == "PRIMCOORD"):
            structure.isPeriodic = True
            atomCountIndex = index + 1
            atomStartIndex = index + 2
        elif (line.strip() == "PRIMVEC"):
            structure.isPeriodic = True
            primVecStartIndex = index + 1
            primVecEndIndex = 3 + index + 1 # Assumes PrimVec is always three lines

    structure.coordCount = int(xsfRead[atomCountIndex].split()[0])

    tmpList = []
    for i in range(primVecStartIndex, primVecEndIndex):
        tmp = xsfRead[i].split()
        tmpList.append(tmp)
    structure.primVec = tuple(tmpList)

    atomCount = 0
    for i in range(atomStartIndex, len(xsfRead)): # Loops through atoms
        tmp = xsfRead[i].split()
        symbol = tmp[0]
        coordinates = {"x" : float(tmp[1]),
                       "y" : float(tmp[2]),
                       "z" : float(tmp[3])}
        forces = {"x" : float(tmp[4]),
                  "y" : float(tmp[5]),
                  "z" : float(tmp[6])}
        structure.atoms.append(Atom(symbol, coordinates, forces))
        atomCount += 1

    return structure

def write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount, newStructsCount):
    print("write_generate_file")
    with open(newGenLoc, 'a') as f:
        for line in oldGen.topLines:
            f.write(line)
        f.write(str(totalStructsCount) + "\n")
        for line in oldGen.structLocs:
            f.write(line + "\n")
        for i in range(newStructsCount):
            f.write(newStructsDir + "/structure{num:04d}.xsf\n".format(num=i+1))

def write_xsf_files(newStructsDir, newStructs):
    print("write_xsf_files")

    locations = []
    energies = []
    os.mkdir(newStructsDir)

    for i, structure in enumerate(newStructs):
        locations.append(newStructsDir + "/structure{num:04d}.xsf".format(num=i+1))
        energies.append(structure.energy)
        if structure.isPeriodic:
            primVec = structure.primVec
            coordCount = structure.coordCount
        atoms = structure.atoms
        with open(locations[i].strip(), 'w') as f:
            f.write("# total energy = " + str(energies[i]) + " eV\n\n")
            if (structure.isPeriodic):
                f.write("CRYSTAL\nPRIMVEC")
                f.write("\n        " + str(primVec[0][0]) + "     " + str(primVec[0][1]) + "     " + str(primVec[0][2]))
                f.write("\n        " + str(primVec[1][0]) + "     " + str(primVec[1][1]) + "     " + str(primVec[1][2]))
                f.write("\n        " + str(primVec[2][0]) + "     " + str(primVec[2][1]) + "     " + str(primVec[2][2]))
                f.write("\nPRIMCOORD\n")
                f.write(str(coordCount))
                f.write("\n")
            else:
                f.write("ATOMS\n")
            success=failure=0
            for atom in atoms:
                if (isinstance(atom, Atom)):
                    success += 1
                    f.write("{: <7}{: .8f}    {: .8f}    {: .8f}    {: .8f}    {: .8f}    {: .8f}\n".format(atom.symbol,
                                                                                                           (atom.coordinates.get("x")),
                                                                                                           (atom.coordinates.get("y")),
                                                                                                           (atom.coordinates.get("z")),
                                                                                                           (atom.forces.get("x")),
                                                                                                           (atom.forces.get("y")),
                                                                                                           (atom.forces.get("z"))))
                else:
                    failure += 1

            if failure >= 1:
                print("Failures: {fail}".format(fail=failure))

main()
