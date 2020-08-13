import numpy
import sys
import os

delta = 0 # User-set displacement for creation of new structure.

def main():
  generateIn = "./generate.in" # File path to generate.in file
  outputGen = "./generate-new.in" # File path to outputted new generate.in
  outputStruct = "../new-data-xsf" # File path to outputted new xsf files
  
  files = [] # Array of file locations of structure files from generate.in
  structureData = [] # An array of "data" dictionaries of existing structures
  newStructureData = [] # An array of "data" dictionaries of new structures

  # Processing command line arguments in the form 
  # ./programName delta generate.in generate-new.in ~/path/to/new/structs/dir
  print(sys.argv)
  delta = input("enter delta (float): ")
  generateIn = input("enter full path to existing generate.in (str): ")
  outputGen = input("enter full desired path new generate.in (str): ")
  outputStruct = input("enter full desired path to directory for new .xsf (str): ")
  
  tmp = read_generate_in(generateIn)
  nFiles = tmp.get("fileCount")
  files = tmp.get("files")

  # Loop through structure files
  for i, xsf in enumerate(files):
    structureData.append(read_xsf_file(xsf))
    newStructureData.append(structureData[i])
    newStructureData[i]['atoms'] = newStructureData[i]['primCoords'] = []

    # Loop through atoms in structures (structureData[i] is one structure)
    for atom in structureData[i].get("atoms"):
      # Builds new atoms, stores in array atoms[]
      atoms = build_new_atoms(atom, delta)
      # Add new atoms to newStructureData[i]
      tmp = newStructureData[i].get("atoms")
      tmp.append(atoms.get("atoms"))
      newStructureData[i]["atoms"] = tmp
      # Update total energy of newStructureData[i]
      tmp = newStructureData[i].get("totalEnergy") # Get energy (float)
      tmp -= atoms.get("eDeduct") # Subtracts energy deduction due to deltas
      newStructureData[i]["totalEnergy"] = tmp

  # Write files
  write_xsf_files(newStructureData, outputStruct)
  write_generate_file(generateIn, outputGen, outputStruct, nFiles)

def read_generate_in(generate_in = "./generate.in"):
  """
  Read .xsf file locations and .xsf file count from generate.in files. 
  """
  files = []

  with open(generate_in.strip(), 'r') as f:
    genRead = f.readlines()

  fileCountIndex = -1
  fileStartIndex = -1
  for index, line in enumerate(genRead):
    if (line.strip() == "FILES"):
      fileCountIndex = index + 1
      fileStartIndex = index + 2
      break
  else:
    print("Error: Generate.in file not found at provided location.")

  for i in range(fileStartIndex, len(genRead)):
    files.append(genRead[i].strip())

  nFiles = genRead[fileCountIndex].strip()
  return {"fileCount" : nFiles, "files" : files}

def read_xsf_file(xsf):
  """
  Read in XSF struct files. Based on read_ascii_train_file from aenet/utils.py
  """
  with open(xsf.strip(), 'r') as f:
    xsfRead = f.readlines()

  energy = float(xsfRead[0].split()[4]) # TODO (LOW): Remove magic number [4]
  isPeriodic = True

  for index, line in enumerate(xsfRead):
    if (line.strip() == "ATOM"):
      isPeriodic = False
      atomStartIndex = index + 1
      continue

    if (line.strip() == "PRIMCOORD"):
      atomCountIndex = index + 1
      atomStartIndex = index + 2
    elif (line.strip() == "PRIMVEC"):
      primVec = []
      primVecStartIndex = index + 1
      primVecEndIndex = 3 + index + 1 # Assumes PrimVec is always three lines

  coordCount = int(xsfRead[atomCountIndex].split()[0])

  for i in range(primVecStartIndex, primVecEndIndex): # Stores PRIMVEC data to arr primVec
      tmp = xsfRead[i].split()
      primVec.append(tmp)

  for i in range(atomStartIndex, len(xsfRead)): # Stores atom data as dicts,
                                                    # appended to array atoms
    tmp = xsfRead[i].split()
    atoms = []
    atoms.append({"symbol" : tmp[0],
                  "x" : float(tmp[1]),
                  "y" : float(tmp[2]),
                  "z" : float(tmp[3]),
                  "fx" : float(tmp[4]),
                  "fy" : float(tmp[5]),
                  "fz" : float(tmp[6])})

  data = {'totalEnergy' : energy, # Float
          'primVec' : primVec, # Arr
          'atoms' : atoms, # Array of dicts
          'primCoords' : atoms, # Array of dicts
          'coordCount' : coordCount, # Count of coords
          'isPeriodic' : isPeriodic} # Bool

  return data

def write_xsf_files(data, directory):
  """
  Write new XSF files based on data and output directory. No return. 
  """
  fileLoc = []
  energy = []
  os.mkdir(directory)
  for i, structure in enumerate(data):
    fileLoc.append(directory + "/structure" + str(i) + ".xsf")
    energy.append(structure.get("totalEnergy"))
    if structure.get("isPeriodic"):
      PrimVec = structure.get("primVec")
      PrimCoord = structure.get("primCoords")
      CoordCount = structure.get("coordCount")
    atoms = structure.get("atoms")

    with open(fileLoc[i].strip(), 'w') as f:
      f.write("# total energy = " + str(energy[i]) + " eV\r\n")
      if structure.get("isPeriodic"):
        f.write("CRYSTAL\rPRIMVEC")
        f.write("\r   " + str(PrimVec[0][0]) + "  " + str(PrimVec[0][1]) + "  " + str(PrimVec[0][2]))
        f.write("\r   " + str(PrimVec[1][0]) + "  " + str(PrimVec[1][1]) + "  " + str(PrimVec[1][2]))
        f.write("\r   " + str(PrimVec[2][0]) + "  " + str(PrimVec[2][1]) + "  " + str(PrimVec[2][2]))
        f.write("\rPRIMCOORD\r")
        f.write(str(CoordCount))
        f.write("\r")
      else:
        f.write("ATOMS\r")
      for atom in atoms:
        f.write(atom.get(symbol) + "  " + 
                atom.get(x) + "  " +
                atom.get(y) + "  " +
                atom.get(z) + "  " +
                atom.get(fx) + "  " +
                atom.get(fy) + "  " +
                atom.get(fz) + "\r")

def write_generate_file(originalLoc, newLoc, structDir, nFiles):
  """
  Write new generate.in files based on original generate.in file, number of
  xsf files, and the location of the directory containing xsf files. File 
  written at newLoc. 
  """
  xsfRead = ""

  with open(originalLoc, 'r') as f:
    genRead = f.readlines()

  for index, line in enumerate(genRead):
    if (line.strip() == "FILES"):
      xsfRead = xsfRead[0:index]

  with open(newLoc, 'a') as f:
    for line in genRead:
      f.write(line + "\r")
    f.write(nFiles + "\r")
    for i in range(int(nFiles)):
      f.write(structDir + "/structure" + str(i) + ".xsf\r")

def new_atom(data, delta, direction):
  """
  Calculates coordinates of one new structure based on displacement in one
  cartesian direction.

  Parameters
  ----------
  data : Dictionary with symbol, cartesian coordinates, and force components
         (cartesian) of the input atom.
         Keys: 'symbol', 'x', 'y', 'z', 'fx', 'fy', 'fz'.
  delta : Float. 
  Direction : Character (string). Either 'x', 'y', or 'z'.

  Returns
  -------
  {'symbol' : symbol, 'x' : x, 'y' : y, 'z' : z, 'fx' : fx, 'fy' : fy, 'fz' : fz}
  """

  output = {'symbol' : symbol, 'fx' : fx, 'fy' : fy, 'fz' : fz}
  
  for dir in "xyz":
    if (dir == direction):
      output.update({direction : coordinates.get(dir) + delta})
    else:
      output.update({direction : coordinates.get(dir)})

  return output

def build_new_atoms(atom, delta):
  """
  Calculates coordinates of new structures as well as the energy deductions
  they are responsible for based on the 1st order Taylor Expansion demonstrated by
  A. Cooper, J. Kästner, A. Urban, N. Artrith, npj Comput. Mater. 6 (2020) 54. 

  Parameters
  ----------
  data : Dictionaries with symbol, cartesian coordinates, and force components
         (cartesian) of the input atom.
         Keys: 'symbol', 'x', 'y', 'z', 'fx', 'fy', 'fz'.
  delta : Float.

  Returns
  -------
  {'energyDeduction' : eDeduct, 'atoms' : atoms}
  """

  displacement = abs(delta) # Delta but always positive. 
  atoms = [] # Array of dictionaries of ALL new atoms based on the input atom. 
  eDeduct = 0.0 # Energy deductions. ASSUMES eDeduct should always treat
                # delta as positive. Is this accurate? Check. 
  negativeAtoms = [] # Array of dictionaries of ONLY atoms made with deltas < 0.

  for direction in "xyz":
    atoms.append(new_atom(data, delta, direction))
    eDeduct += force.get(direction) * displacement

  if (delta > 0):
    delta *= -1
    negativeAtoms = build_new_atoms(data, delta).get('atoms')
    for i in range(3):
      atoms.append(negativeAtoms[i])

  return {'energyDeduction' : eDeduct, 'atoms' : atoms}

main()
