import os
import sys
from getopt import getopt
import csv
import logging
from pprint import pprint
import operator
import random


# SOGLIA_PERC=0.3
# SOGLIA_COUNT_F=2000
# SOGLIA_COUNT_M=500


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
   print("Usage: %s -f file input " % sys.argv[0])
   print("Usage: %s -o file output" % sys.argv[0])
   print("Usage: %s -l file with the list of segments (vertical)" % sys.argv[0])
   print("Usage: %s -h help\n" % sys.argv[0])
   print("Example :-f  hashu_for_trining  -o output_file.txt \n"%sys.argv[0])
   raise SystemExit


#####################################################################


class SegmentsList:
    """Class to create the list of all segments used in classification."""

    type="CreateList"
    def __init__(self, allSegmts):
        self.allSegmts_name = allSegmts
        self.segmList=[]
        logging.info('Created Object for list of segments')

    def CreateList(self):
        with open(self.allSegmts_name,'r') as s:
            for line in s:
                self.segmList.append(line.replace("\n",''))
            logging.info('Creation of the list of segments')
        return self.segmList

class CreateFeaturesArray:
    """Class ro create the array of features for each user"""
    def __init__(self,inFile,segmList):
        self.inFile_name = inFile
        self.outFile_name = outFile
        self.segmList=segmList
#        self.dict_users={}
#        logging.info('Created Object for segments list of each user (0,1), with sex (1=F,0=M)')

    def CheckAndPrint(self):
        count=0
        with open(self.inFile_name,'r') as fi, open(self.outFile_name+"_WITH_SEX",'w') as sex, open(self.outFile_name+"_NO_SEX",'w') as asex:
            for line in fi:
                splitted=line.split("^")
                code=splitted[0]
                segments=splitted[-1].split(",")
                count+=1
                find=0
                has_sex=0
                num_sex=0
                num_asex=0
                tmp_list=[]
#                print("row['SEGMENTS'].split(',')",row['SEGMENTS'].split(','))
                for segm in self.segmList:
                    if segm.strip("'") in segments:
                        tmp_list.append('1')
                        find=1
                    else:
                        tmp_list.append('0')
                if 'JmvTH_eE' in segments and 'JmvTheyd' not in segments:
                    tmp_list.append('1')
                    has_sex=1
                elif 'JmvTH_eE' not in segments and 'JmvTheyd' in segments:
                    tmp_list.append('0')
                    has_sex=1
                if find==1:
                    if has_sex==1:
                        num_sex+=1
                        sex.write(str(code)+',')
                        for ele in tmp_list[:-1]:
                            sex.write(ele+",")
                        sex.write(tmp_list[-1]+"\n")
                    else:
                        num_asex+=1
                        asex.write(str(code)+',')
                        for ele in tmp_list[:-1]:
                            asex.write(ele+",")
                        asex.write(tmp_list[-1]+"\n")
            logging.info('Printed list of features for user')
            logging.info('Printed feature for %i users with sex info in %s'%(num_sex,self.outFile_name+"_WITH_SEX"))
            logging.info('Printed feature for %i users without sex info in %s'%(num_asex,self.outFile_name+"_NO_SEX"))
            logging.info('Number of row in the original inFile: %i'%count)
#            return self.dict_users




def main(inFile,outFile,allSegmts):
    logging.info("START")
    logging.info("Creation of segments list")
    segmList_ob=SegmentsList(allSegmts)
    segmList=segmList_ob.CreateList()
    logging.info("Creating lists of features, 1= has segments. Last one: 1=F, 0=M")
    features_array_ob=CreateFeaturesArray(inFile,segmList)
    dict_users=features_array_ob.CheckAndPrint()
    logging.info("END")











if __name__=="__main__":
   opts, args = getopt(sys.argv[1:], "f:o:l:h")
   opts = dict(opts)
   inFile=None
   outFile=None
   #for opt, arg in opts:
   if '-f' in opts:
      inFile=str(opts['-f'])
   if '-o' in opts:
      outFile=str(opts['-o'])
   if '-l' in opts:
       allSegmts=str(opts['-l'])
   if '-h' in opts:
      usage('msg')
   if ('-f' not in opts==True and '-o' not in opts==True and '-m' not in opts==True and '-h' not in opts==True):
       usage('0')
   main(inFile,outFile,allSegmts)
