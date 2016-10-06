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

NUM_TRAINING=100000

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
        self.dict_users={}
#        logging.info('Created Object for segments list of each user (0,1), with sex (1=F,0=M)')

    def CreateDictWithSex(self):
        count=0
        with open(self.inFile_name,'r') as fi:
            self.reader = csv.DictReader(fi,delimiter='/')
#            print('sem list>>>>>>>>>>>>>>',self.segmList)
            for row in self.reader:
#                print(row)
                count+=1
                find=0
                tmp_list=[]
#                print("row['SEGMENTS'].split(',')",row['SEGMENTS'].split(','))
                for segm in self.segmList:
                    if segm.strip("'") in row['SEGMENTS'].split(','):
                        tmp_list.append('1')
                        find=1
                    else:
                        tmp_list.append('0')
                if row['SEX']=='F':
                    tmp_list.append('1')
                else:
                    tmp_list.append('0')
                if find==1:
                    self.dict_users[row['CODE']]=tmp_list
            logging.info('Created Dictionary for user: key is the code, value the list os segments')
            logging.info('Number of row in rader: %i'%count)
            return self.dict_users


class SelectRandomList:
    """Class to select a random list pof user for validation"""
    def __init__(self,outFile,dict_validation,segmList):
        self.outFile_name = outFile
        self.dict_validation=dict_validation
        self.dict_training={}
        self.segmList=segmList
        logging.info('Created Object random lists to be use in training ad validation')


    def SelectRandomList(self):
#        print(self.dict_validation)
        logging.info("Using a training set of %i"%NUM_TRAINING)
        logging.info("Using a validation set of %i"%len(self.dict_validation.keys()))
        random_keys=random.sample(self.dict_validation.keys(),NUM_TRAINING)
#        print('random_keys',random_keys)
        for key in random_keys:
            self.dict_training[key]=self.dict_validation.pop(key)
        logging.info('Created dicts for training and validation')
#        print(self.dict_training)


    def PrintRandomLists(self):
        logging.info('Printing the dictionaries to ut files')
        with open(self.outFile_name+'_valid','w') as out:
            for item in self.segmList[:-1]:
                out.write(str(item)+',')
            out.write(str(self.segmList[-1])+'\n')
            writer = csv.writer(out,delimiter=',')
#            writer.writerow(self.dict_validation.keys())
#            writer.writerows(zip(*self.dict_validation.values()))
            for key, value in self.dict_validation.items():
                writer.writerow(value)
        with open(self.outFile_name+'_train','w') as out:
            for item in self.segmList[:-1]:
                out.write(str(item)+',')
            out.write(str(self.segmList[-1])+'\n')
            writer = csv.writer(out,delimiter=',')
            for key, value in self.dict_training.items():
                writer.writerow(value)





def main(inFile,outFile,allSegmts):
    logging.info("START")
    logging.info("Creation of segments list")
    segmList_ob=SegmentsList(allSegmts)
    segmList=segmList_ob.CreateList()
    logging.info("Creation of dictionary of arrays of segments for classification")
    logging.info("Keys=users code, value=array of 1 and 0")
    logging.info("1= has segments. Last one: 1=F, 0=M")
    features_array_ob=CreateFeaturesArray(inFile,segmList)
    dict_users=features_array_ob.CreateDictWithSex()
#    print("dict_users")
#    pprint(dict_users)
    logging.info("Random selection of lists for training and validation using %i lines for training"%NUM_TRAINING)
    logging.warning("IF THE DIMENSION OF THE TRAINING SET IS 0, THE SELECTION WILL BE DONE IN THE CLASSIFICATION SCRIPT")
    random_lists_ob=SelectRandomList(outFile,dict_users,segmList)
    random_lists_ob.SelectRandomList()
    random_lists_ob.PrintRandomLists()
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
