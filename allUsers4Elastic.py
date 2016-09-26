import os
import sys
from getopt import getopt
import csv
import logging
from pprint import pprint
from prepareePrice import DictCreation


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

logger = logging.getLogger("check sex of krux id vs anagrafica")

##########################################################################
### usage
##########################################################################
def usage(msg):
   if msg=='0':
      print("=========================")
      print("ERRORE: %s" % 'Missing variabile in input')
      print("=========================")
#   print( "Usage: %s -i  input-file\n" % sys.argv[0]
   print("Usage: %s -i file input" % sys.argv[0])
   print("Usage: %s -o file output" % sys.argv[0])
   print("Usage: %s -h help\n" % sys.argv[0])
   print("Example: python3 %s -i inFile -o output_file.txt \n"%sys.argv[0])
   raise SystemExit


#####################################################################


def main(inFile,outFile):
    logging.info("START")
    logging.info("FILE OPENED INN READ %s"%inFile)
    file_in=open(inFile,'r')
    logging.info("FILE OUT %s"%outFile)
    num_lines=0
    with open(outFile,'w') as out:
        for line in file_in:
            num_lines+=1
            splitted=line.split("^")
            out.write(splitted[0]+"/"+splitted[-1]+"\n")
    logging.info("WRITTEN %i LINES IN %s"%(num_lines,outFile))
    logging.info("END")
    file_in.close()


if __name__=="__main__":
   opts, args = getopt(sys.argv[1:], "i:o:h")
   opts = dict(opts)
   inFile=None
   outFile=None
   #for opt, arg in opts:
   if '-i' in opts:
      inFile=str(opts['-i'])
   if '-o' in opts:
      outFile=str(opts['-o'])
   if '-h' in opts:
      usage('msg')
   if '-i' not in opts and '-o' not in opts and '-h' not in opts:
       usage('0')
   main(inFile,outFile,)
