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

class PrepareUsers:
    """Class to prepare the list of users to be use in classification."""
    def __init__(self,inFile,outFile):
        super(, self).__init__()
        self.inFile_name = inFile
        self.outFile_name = outFile
        self.maleSeg = 'JmvTheyd'
        self.femSeg = 'JmvTH_eE'

    def PrepareFiles(self):
        with open(self.inFile_name,'r') as fi, with open(self.outFile_name+"_WITH_SEX",'w') as sex, with open(self.outFile_name+"_NO_SEX",'w') as asex:
            sex.write("CODE/SEX/SEGMENTS")
            asex.write("CODE/SEGMENTS")
            num_lines=0
            num_sex=0
            num_asex=0
            for line in fi:
                num_lines+=1
                splitted=line.split("^")
                segments=splitted[-1].split(",")
                if 'JmvTH_eE' not in segments and 'JmvTheyd' not in segments or ('JmvTH_eE' in segments and 'JmvTheyd' in segments):
                    asex.write(splitted[0]+"/"+splitted[-1]+"\n")
                    num_asex+=1
                else:
                    if 'JmvTH_eE' in segments:
                        sex.write(splitted[0]+"/F/"+splitted[-1]+"\n")
                        num_sex+=1
                    else:
                        sex.write(splitted[0]+"/M/"+splitted[-1]+"\n")
                        num_sex+=1
            logging.info("ANALIZED %i USERS "%num_lines)
            logging.info("WRITEN %i USERS IN %s"%(num_asex,self.outFile_name+"_NO_SEX"))
            logging.info("WRITEN %i USERS IN %s"%(num_sex,self.outFile_name+"_WITH_SEX"))


def main(inFile,outFile):
    logging.info("START")
    logging.info("FILE OPENED IN READ %s"%inFile)
    users=PrepareFiles(inFile,outFile)
    users.PrepareFiles()
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
