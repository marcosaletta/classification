import os
import sys
from getopt import getopt
import csv


import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

logger = logging.getLogger("prepare-ePrice")

##########################################################################
### usage
##########################################################################
def usage(msg):
   if msg=='0':
      print("=========================")
      print("ERRORE: %s" % 'Missing variabile in input')
      print("=========================")
#   print( "Usage: %s -i  input-file\n" % sys.argv[0]
   print("Usage: %s -f file in input" % sys.argv[0])
   print("Usage: %s -o file output" % sys.argv[0])
   print("Usage: %s -h help\n" % sys.argv[0])
   print("Example :-f  ePRICE_20160727.txt -o $ ePRICE_20160727-Cassandra.txt\n"%sys.argv[0])
   raise SystemExit


#####################################################################


class DictCreation:
    """Class to prepare create dict from line"""
    
    type= 'ePrice_dict'
    
    def __init__(self,line):
        self.line=line
        self.dict_line={}
        
    def createDict(self):
        self.splitted=self.line.split(";")
        self.dict_line['code']=self.splitted[0].split("^")[0]
        for item in self.splitted[1:]:
            try:
                self.dict_line[item.split(":")[0]]=item.split(":")[1].strip("\n")
            except IndexError:
                print(item)
        return self.dict_line
    
class CheckFileds:
    """Class to check if there are missing fileds"""
    
    type= 'ePrice_fileds'
    
    def __init__(self,dict_line):
        self.dict_line=dict_line
            
    def checkFileds_dict(self):
        self.Fields_list=['code','registrato','sesso','eta','citta','provincia','acquirente','interessi','Frequency','Monetary','Recency','DateLastOrder','numfigli','occupazione']
        for field in self.Fields_list:
            if field not in self.dict_line:
                self.dict_line[field]=''
        return self.dict_line
        
        
    





def main(inFile,outFile):
    file_out=open(outFile, 'w',encoding='utf-8')
    first=0
    with open(inFile,'r', encoding='mac_roman') as file_in:
        for line in file_in:
            dict_line_ob=DictCreation(line)
            dict_line=dict_line_ob.createDict()
            dict_line_comp_ob=CheckFileds(dict_line)
            dict_line_comp=dict_line_comp_ob.checkFileds_dict()
            w = csv.DictWriter(file_out, dict_line_comp.keys())
            if first==0:
                w.writeheader()
                first=1
            w.writerow(dict_line_comp)








if __name__=="__main__":
   opts, args = getopt(sys.argv[1:], "f:o:h")
   opts = dict(opts)
   inFile=None
   outFile=None
   #for opt, arg in opts:
   if '-f' in opts:
      inFile=str(opts['-f'])
   if '-o' in opts:
      outFile=str(opts['-o'])
   if '-h' in opts:
      usage('msg')
   if ('-f' not in opts==True and '-o' not in opts==True and '-h' not in opts==True):
       usage('0')
   main(inFile,outFile)            