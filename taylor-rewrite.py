import numpy
import sys
import os

delta = 0

class Structure:
    def __init__(self, energy = 0.0, atoms = [], isPeriodic = True, coordCount = 0, primVec = []):
        self.energy = energy 
        self.atoms = atoms 
        self.isPeriodic = isPeriodic
        self.coordCount = coordCount
        self.primVec = primVec
    
    def build_new_structure(self, atomIndex, direction, sign):
        newStructure = Structure(self.energy, self.atoms, self.isPeriodic) # Build new struct
        targetAtom = newStructure.atoms[atomIndex] # Fetch target atom
        if sign == "+":
            newStructure.energy -= delta * targetAtom.forces.get(direction) # Deduct energy of new structure
        elif sign == "-":
            newStructure.energy += delta * targetAtom.forces.get(direction) # Add energy to new structure
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
    def __init__(self, structLocs = [], topLines = []):
        self.structLocs = structLocs # Locations of all .xsf files (array of strings)
        self.topLines = topLines # Every line before "FILES" (array of strings)

def main():
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
                        newStructsCount += 1
    
    totalStructsCount = oldStructsCount + newStructsCount

    write_xsf_files(newStructsDir, newStructs)
    write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount, newStructsCount)

def read_generate_in(oldGenLoc):
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
            structure.primVec = []
            primVecStartIndex = index + 1
            primVecEndIndex = 3 + index + 1 # Assumes PrimVec is always three lines

    structure.coordCount = int(xsfRead[atomCountIndex].split()[0])
    
    for i in range(primVecStartIndex, primVecEndIndex):
        tmp = xsfRead[i].split
        structure.primVec.append(tmp)

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

    return structure

def write_generate_file(oldGen, newGenLoc, newStructsDir, totalStructsCount):
    with open(newGenLoc, 'a') as f:
        for line in oldGen.topLines:
            f.write(line)
        f.write(str(totalStructsCount) + "\n")
        for line in oldGen.structLocs:
            f.write(line)
        for i in range(newStructsCount):
            f.write(newStructsDir + "/structure{num:04d}.xsf\n".format(num=i))

def write_xsf_files(newStructsDir, newStructs):
    locations = []
    energies = []
    os.mkdir(newStructsDir)

    for i, structure in enumerate(newStructs):
        locations.append(newStructsDir + "/structure{num:04d}.xsf".format(num=i))
        energies.append(structure.get("totalEnergy"))
        if structure.get("isPeriodic"):
            primVec = structure.primVec
            primCoord = structure.primCoords
            coordCount = structure.coordCount
        atoms = structure.atoms

        with open(fileLoc[i].strip(), 'w') as f:
            f.write("# total energy = " + str(energy[i]) + " eV\r\n")
            if structure.get("isPeriodic"):
                f.write("CRYSTAL\rPRIMVEC")
                f.write("\r   " + str(primVec[0][0]) + "  " + str(primVec[0][1]) + "  " + str(primVec[0][2]))
                f.write("\r   " + str(primVec[1][0]) + "  " + str(primVec[1][1]) + "  " + str(primVec[1][2]))
                f.write("\r   " + str(primVec[2][0]) + "  " + str(primVec[2][1]) + "  " + str(primVec[2][2]))
                f.write("\rPRIMCOORD\r")
                f.write(str(coordCount))
                f.write("\r")
            else:
                f.write("ATOMS\r")
            for atom in atoms:
                f.write(atom.symbol + "  " +
                        atom.coordinates.get("x") + "  " +
                        atom.coordinates.get("y") + "  " +
                        atom.coordinates.get("z") + "  " +
                        atom.forces.get("x") + "  " +
                        atom.forces.get("y") + "  " +
                        atom.forces.get("z") + "\n")

main()
