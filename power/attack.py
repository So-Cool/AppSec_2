#! /usr/bin/python
import sys, subprocess, random
from numpy import mean
from numpy import zeros
from numpy import matrix
# from scipy.stats.stats import pearsonr
from numpy import corrcoef
from numpy import where
from pprint import pprint

# CONSTANTS
#   number of attacks
AttacksNo   = 500
#
# Input size in octets
inputOctets = 32
# Key size in bits
keySize     = 128
# octet size
octet = 256

# Rijndael S-box
# taken from: http://anh.cs.luc.edu/331/code/aes.py
sbox =  [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67,
        0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59,
        0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7,
        0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1,
        0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05,
        0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83,
        0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29,
        0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
        0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa,
        0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c,
        0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc,
        0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
        0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19,
        0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee,
        0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
        0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4,
        0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6,
        0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70,
        0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9,
        0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e,
        0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1,
        0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0,
        0x54, 0xbb, 0x16]

SboxLookup = matrix([
  [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
  [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
  [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
  [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
  [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
  [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
  [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
  [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
  [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
  [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
  [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
  [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
  [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
  [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
  [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
  [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
  ])




# interact with altered device --- testing stage
def interactR( G ) :
  t = []
  # Send      G      to   attack target.
  for i in G :
    target_in.write( "%X\n" % ( i ) ) ; target_in.flush()
    target_in.write( "%X\n" % ( N ) ) ; target_in.flush()
    target_in.write( "%X\n" % ( long(d, 2) ) ) ; target_in.flush()
    # Receive time from attack target.
    # time that is left is reductions in multiplications + squares + reductions in squares
    t.append( int( target_out.readline().strip() )  )
    target_out.readline().strip()
  return t




# interact with real device
def interact( G, limit ) :
  t = []
  # Send G to attack target
  target_in.write( "%X\n" % ( G ) ) ; target_in.flush()
  # Receive power trace from attack target
  _traces = target_out.readline().strip()[:limit]

  if _traces[-1] == ',' or _traces[-1] == ' ' :
    _traces = _traces[:-1]

  __traces = _traces.split(',')
  traces = []
  for i in __traces :
    traces.append( int( i ) )
  # Receive decryption from attack target
  dec = target_out.readline().strip()
  return (traces, dec)

# get power traces
def trace( plainTexts, inType, quantity, upperBound ) :
  traces = []
  if inType == 'first' :
    for i in plainTexts:
        ( trace, cipher ) = interact( i, upperBound )
        no = trace[0]
        traces.append( trace[ 1 : int( no * quantity ) ] )
  else :
    print "Not defined type."
  return traces

# get intermediate result---first S-box
def Sbox( plainTexts, keyHypothesis, byte ) :
  # define output
  V = zeros( (len(plainTexts), len(keyHypothesis)) )

  # mask proper byte
  mpl = keySize / inputOctets
  mask = '1' * mpl
  mask = int( mask, 2 )
  mask = mask << ( byte * mpl )

  # get the state matrix
  for ic, i in enumerate(plainTexts) :
    # extract byte
    extractedByte = i & mask
    for jc, j in enumerate(keyHypothesis) :
      temp = ( extractedByte ^ j ) + 1 # +1 in MatLab WHY =1 !!!!!!!!!!!!!!!!!!!!
      V[ic, jc] = SubBytes( temp )

  return V

# define SUbbytes function---Section 5.1.1
#  http://csrc.nist.gov/publications/fips/fips197/fips-197.pdf
def SubBytes( x ) :
  hexStr = "%X" % x
  hexStr = hexStr.zfill( 2 )
  # print "( " + hexStr[0] + " , " + hexStr[1] + " )"
  return SboxLookup[ int(hexStr[0], 16), int(hexStr[1], 16) ]

# Get Hamming weight for the matrix
def getHamming( Vi ) :
  dim = Vi.shape
  Hi  = zeros( dim )
  for i in range( dim[0] ) :
    for j in range( dim[1] ) :
      Hi[i, j] = hammingWeigh( Vi[i, j] )
  return Hi

# get Hamming weigh of a single word
def hammingWeigh( x ) :

  if x != int(x):         #
    print "LOLOLOLO: ", x #
  x = int(x)

  binRep = bin( x )[2:]
  return binRep.count('1')

# get traces correlation
def getMxCorrelation( Hi, Ti ) :
  # calculate correlation between all columns of *Hi* and *Ti*
  ( r , Hc ) = Hi.shape
  ( r , Tc ) = Ti.shape

  R = zeros( (Hc, Tc) )
  for i in range(Hc) :
    for j in range(Tc) :
      # R[i, j] = pearsonr( Hi[:, i], Ti[:, j] )[0]
      R[i, j] = corrcoef( Hi[:, i].T, Ti[:, j].T )[0][1]
  return R

# Find correct octet
def findBit( R ) :
  maximum = R.max()
  mx = where( R == maximum )
  mxR = mx[0].tolist()[0]
  mxC = mx[1].tolist()[0]
  print "max: ", maximum, " R:  ", mxR, " C:  ", mxC
  minimum = R.min()
  mn = where( R == minimum )
  mnR = mn[0].tolist()[0]
  mnC = mn[1].tolist()[0]
  print "min: ", minimum, " R:  ", mnR, "  C: ", mnC

  if abs(maximum) > abs(minimum) :
    return mxR
  else if abs(maximum) < abs(minimum) :
    return mnR
  else :
    print "values equal don't know what to do!"
    exit()



if ( __name__ == "__main__" ) :
  # Key guess
  key = ""
  # generate 128-bit strings for attacks
  plainTexts = []
  for i in range(AttacksNo) :
    rb = random.getrandbits( keySize )
    plainTexts.append( rb )
  print "Attacks Generated.\nStarting interaction."

  # Produce a sub-process representing the attack target.
  target = subprocess.Popen( args   = sys.argv[ 1 ],
                             stdout = subprocess.PIPE, 
                             stdin  = subprocess.PIPE )

  # Construct handles to attack target standard input and output.
  target_out = target.stdout
  target_in  = target.stdin

  # Get traces --- take first 10%
  # create sampling vector to select trace entries
  sampleSize = 0.05
  samplingType = 'first'

  #find the limit
  ( tr, cr ) = interact(plainTexts[0], None)
  ub = int( tr[0] * sampleSize * 5 )

  # extract trace entries
  traces = trace( plainTexts, samplingType, sampleSize, ub )
  traces = matrix( traces )

  # create key hypothesis
  keyHypothesis = range( octet )

  print "Recovering the key bit by bit..."
  # perform first S-box
  for i in range( keySize ) :
    print "1"
    Vi = Sbox( plainTexts, keyHypothesis, i ) # i = 1
    print "2"
    Hi = getHamming( Vi )
    print "3"
    Ri = getMxCorrelation( Hi, traces )
    print "4"
    b = findBit( Ri )
    hb = "%X" % b
    hb = hb.zfill(4)
    key = hb + key
    print "Partial key: ", key

print "Key: ", key


  # attack until good key is found
  # while True :
  #   secretKey = attack( attacks, attackExp )
  #   if decipher == encrypt(cipher, secretKey+'1', N):
  #     LSB = '1'
  #     break
  #   elif decipher == encrypt(cipher, secretKey+'0', N):
  #     LSB = '0'
  #     break
  #   else : # if does not fit --- try again
  #     print "Failed to recover key --- trying again!"
  #     print "Increasing sample space"
  #     AttacksNo += 1000
  #     # generate 1024-bit strings for attacks
  #     i = 0
  #     plainTexts = []
  #     while( i < AttacksNo ) :
  #       rr = random.getrandbits( 1024 )
  #       # check whether are less than N
  #       if rr < N :
  #         plainTexts.append( rr )
  #         i += 1
  #     attacks = plainTexts

  # print "Secret key in bin format: ", secretKey+LSB    
  # print "Secret key in hex format: %X" % ( long(secretKey+LSB, 2) )






  # Globals
  # np0, N, rsq = 0, 0, 0
  # publicKey[i] = long( k, 16 )
  # exp = "{0:b}".format( publicKey[1] )

