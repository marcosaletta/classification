import os
import sys
from getopt import getopt
import csv
import logging
from pprint import pprint
import operator


#SOGLIA_PERC=0.5
#SOGLIA_COUNT_F=500
#SOGLIA_COUNT_M=500
SOGLIA_PERC=0.3
SOGLIA_COUNT_F=500
SOGLIA_COUNT_M=500




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
   print("Usage: %s -f file input wit segments and sex" % sys.argv[0])
   print("Usage: %s -o file output" % sys.argv[0])
   print("Usage: %s -m file mapping" % sys.argv[0])
   print("Usage: %s -h help\n" % sys.argv[0])
   print("Example: %s -f  hashu_for_trining  -o output_file.txt \n"%sys.argv[0])
   raise SystemExit


#####################################################################




class CreateDict:
    """Class to prepare the dict of an anagrafica file"""

    type='CreateDict'

    def __init__(self,inFile,outFile,file_Mapping):
        self.inFile_name=inFile
        self.outFile_name=outFile
        self.file_Mapping_name=file_Mapping
        self.dict_all={}
        self.dict_all['M']={}
        self.dict_all['F']={}
        self.dict_uniq={}
        self.dict_uniq['M']={}
        self.dict_uniq['F']={}
        self.dict_perc={}
        self.dict_perc['M']={}
        self.dict_perc['F']={}

    def GenderDict(self):
        inFile=open(self.inFile_name,'r')
        self.reader = csv.DictReader(inFile,delimiter='/')
        for row in self.reader:
            inizio=0
            #print(row)
            sesso=row['SEX'].strip()
            #print('sesso:',sesso)
            string=row['SEGMENTS']
            #while inizio<len(string) and inizio!=-1:
                #inizio=string.find("^")
                #if inizio!=-1:
                    #inizio_corr=inizio+1
                    #string=string[inizio_corr:]
            splitted=string.split(",")
            for segm in splitted:
                if segm not in self.dict_all[sesso]:
                    self.dict_all[sesso][segm]=0
                self.dict_all[sesso][segm]+=1
        logging.info("Found %i segments for M, %i segments for F"%(len(self.dict_all['M'].keys()),len(self.dict_all['F'].keys())))
        inFile.close()

    def FindUniq(self):
#        pprint(self.dict_all['F'])
        for key in self.dict_all['M']:
            if key not in self.dict_all['F']:
                self.dict_uniq['M'][key]=self.dict_all['M'][key]
        for key in self.dict_all['F']:
            if key not in self.dict_all['M']:
                self.dict_uniq['F'][key]=self.dict_all['F'][key]
            else:
                perc=abs((self.dict_all['F'][key]-self.dict_all['M'][key])/(self.dict_all['F'][key]+self.dict_all['M'][key]))
#                if perc>SOGLIA_PERC and max(self.dict_all['F'][key],self.dict_all['M'][key])>SOGLIA_COUNT :
                if perc>SOGLIA_PERC:
                    if self.dict_all['F'][key]>self.dict_all['M'][key] and self.dict_all['F'][key]>SOGLIA_COUNT_F:
                        self.dict_perc['F'][key]=perc
                    else:
                        if self.dict_all['M'][key]>SOGLIA_COUNT_M:
                            self.dict_perc['M'][key]=perc

    def WriteOutFile(self):
        with open(self.outFile_name,'w') as out:
            out.write("MALE UNIQ SEGMENTS:")
            w = csv.writer(out)
            w.writerow(["SEGMENTS","COUNT"])
            w.writerows(self.dict_uniq['M'].items())

            w.writerow(['FEMALE UNIQ SEGMENTS:',' '])
            w.writerow(["SEGMENTS","COUNT"])
            #print(self.dict_uniq['F'].keys())
            w.writerows(self.dict_uniq['F'].items())

            w.writerow(['PERCT DIFFERENCES MALE:',' '])
            w.writerow(["SEGMENTS","PERC"])
            self.sorted_perc_male = sorted(self.dict_perc['M'].items(), key=operator.itemgetter(1), reverse=True)
            for item in self.sorted_perc_male:
                w.writerow(item)
            w.writerow(["PERCT DIFFERENCES FEMALE:",' '])
            w.writerow(["SEGMENTS","PERC"])
            self.sorted_perc_female = sorted(self.dict_perc['F'].items(), key=operator.itemgetter(1), reverse=True)
            for item in self.sorted_perc_female:
                w.writerow(item)


    def WriteGrep(self):
        file_Mapping=open(self.file_Mapping_name,'r')
        lines=file_Mapping.readlines()
#        with open(self.outFile_name+'description','w') as des:
        des=open(self.outFile_name+'_description','w')
        querys=open(self.outFile_name+'_querys','w')
        list_segm=open(self.outFile_name+'_list','w')
        des.write('DESCRIPTION MALE\n')
#            pprint(self.sorted_perc_male)
        querys.write('MALE\n')
        for item in self.sorted_perc_male:
#            print(item,item[0])
            # querys.write(item[0]+' OR ')
            # list_segm.write(item[0]+'\n')
            for line in lines:
#                print('line')
                if item[0] in line:
                    #print('find')
                    des.write(str(item[1])+'-'+line+'\n')
                    querys.write(item[0]+' OR ')
                    list_segm.write(item[0]+'\n')
        querys.write('\n\n')
        des.write('DESCRIPTION FEMALE\n')
        querys.write('FEMALE\n')
        for item in self.sorted_perc_female:
            for line in lines:
                if item[0] in line:
                    des.write(str(item[1])+'-'+line+'\n')
                    querys.write(item[0]+' OR ')
                    list_segm.write(item[0]+'\n')

        des.close()
        file_Mapping.close()
        querys.close()






def main(inFile,outFile,file_Mapping):
    logging.info("START")
    logging.info("Creation of dictionary of segments")
    dict_all_ob=CreateDict(inFile,outFile,file_Mapping)
    dict_all_ob.GenderDict()
    logging.info("Search for uniq and more relavant segments to discrimate between M and F")
    logging.info("Values for treshold: percent. diff %f, tresh. M %i, tresh. F %i"%(SOGLIA_PERC,SOGLIA_COUNT_M,SOGLIA_COUNT_F))
    dict_all_ob.FindUniq()
    logging.info("Write out files: recap, query and list")
    dict_all_ob.WriteOutFile()
    logging.info("Write out description of segments (taken from %s)"%file_Mapping)
    dict_all_ob.WriteGrep()
    logging.info("END")

#    pprint(dict_eprice)








if __name__=="__main__":
   opts, args = getopt(sys.argv[1:], "f:o:m:h")
   opts = dict(opts)
   inFile=None
   outFile=None
   #for opt, arg in opts:
   if '-f' in opts:
      inFile=str(opts['-f'])
   if '-o' in opts:
      outFile=str(opts['-o'])
   if '-m' in opts:
      file_Mapping=str(opts['-m'])
   if '-h' in opts:
      usage('msg')
   if'-f' not in opts and '-o' not in opts and '-m' not in opts and '-h' not in opts:
       usage('0')
   main(inFile,outFile,file_Mapping)
