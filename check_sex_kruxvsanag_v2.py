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
   print("Usage: %s -e file anagarafica ePrice" % sys.argv[0])
   print("Usage: %s -s file anagrafica SaldiPrivati" % sys.argv[0])
   print("Usage: %s -o file output" % sys.argv[0])
   print("Usage: %s -k file krux" % sys.argv[0])
   print("Usage: %s -h help\n" % sys.argv[0])
   print("Example :-e  ePRICE_20160727.txt -s SaldiPrivati_20160824.txt -o output_file.txt -k outTmp.txt  \n"%sys.argv[0])
   print("Example :python3 check_sex_kruxvsanag.py -s ../anagrafica_files/saldi_sesso -e ../anagrafica_files/ePrice_code_sesso -o ../anagrafica_files/test_all_user -k ../anagrafica_files/hashu_for_trining\n"%sys.argv[0])
   raise SystemExit


#####################################################################


class CheckFileds:
    """Class to check if there are missing fileds"""

    type= 'ePrice_fileds'

    def __init__(self,dict_line,dict_type):
        self.dict_line=dict_line
        self.dict_type=dict_type
        self.Fields_list=['code','sesso']

    def checkFileds_dict(self):
        not_found=0
        for field in self.Fields_list:
            if field not in self.dict_line:
                not_found=1
                continue
        if not_found==0:
            self.dict_type[self.dict_line['code']]=self.dict_line['sesso']
        return self.dict_type


class CheckSex:
    """Class to check if the sex assigned by krux is correct"""

    type='CheckSex'

    def __init__(self,FileName_krux,FileName_out,dict_eprice,dict_saldi):
        self.FileName_krux=FileName_krux
        self.FileName_out=FileName_out
        self.dict_saldi=dict_saldi
        self.dict_eprice=dict_eprice
        self.dict_sex={}
        self.dict_sex['Total_line']=0
        # self.dict_sex['M']=0
        # self.dict_sex['F']=0
        # self.dict_sex['CONTRAST_ANAG']=0
        # self.dict_sex['CONTRAST_KRUX']=0
        # self.dict_sex['NoSex']=0
        # self.dict_sex['BiSex']=0

    def CheckSexLine(self):
        file_krux=open(self.FileName_krux,'r')
        file_out=open(self.FileName_out,'w')
#        reader = csv.DictReader(file_krux,delimiter="^")
        file_report=open(self.FileName_out+'_report','w')
        file_training=open(self.FileName_out+'_training','w')
        count_line_hash=0
        for line in file_krux:
            row=line.strip()
            inizio=0
            has_hashu=0
#            sesso=row['SEX'].strip()
            string=row
#            print(string)
            self.string=string
#            print(string)
            while inizio<len(string) and inizio!=-1:
                inizio=string.find("hashu_id")
                if inizio!=-1:
                    has_hashu=1
                    inizio_corr=inizio+9
                    fine=inizio_corr+36
                    code=row[inizio_corr:fine]
                    string=string[inizio_corr:]
#                    print(row[inizio_corr:fine].upper())
            if has_hashu==1:
                #print('HASHU',row[inizio_corr:fine].upper())
                sesso_tmp=self.CheckInDict(row[inizio_corr:fine].upper())
                count_line_hash+=1
                #print('sesso_tmp',sesso_tmp)
            else:
                continue
            #print(row[fine:].split(','))
            if 'JmvTH_eE' in row[fine:].split(',') and 'JmvTheyd' not in row[fine:].split(','):
                sesso='F'
                #print('F')
            elif 'JmvTheyd' in row[fine:].split(',') and 'JmvTH_eE' not in row[fine:].split(','):
                sesso='M'
                #print('M')
            elif 'JmvTheyd' in row[fine:].split(',') and 'JmvTH_eE' in row[fine:].split(','):
                sesso='BiSex'
            else:
                sesso=None
#                continue
            if sesso_tmp=="CONTRAST_ANAG":
                sesso=sesso_tmp
            elif sesso_tmp==None and sesso!=None and sesso!="BiSex":
                sesso="Sex_Krux_only"
            elif sesso_tmp==None and sesso=="BiSex":
                sesso="BiSex_NoSex"
                print(code)
            else:
#                if sesso!=sesso_tmp and sesso!="BiSex" and sesso!="None":
                if sesso!=sesso_tmp and (sesso=="M" or sesso=="F"):
                    sesso="CONTRAST_KRUX"
#                            print('ko',len(sesso_tmp),len(row['SEX'].strip()))
                elif sesso!=sesso_tmp and sesso=="BiSex":
                    sesso="BiSex"
                elif sesso!=sesso_tmp and sesso==None:
                    sesso="Sex_anag_only"
                else:
                    sesso=sesso_tmp
#                            print('ok')
#                print(string)
#            print("******************************************")
            if sesso=="CONTRAST_KRUX":
                file_out.write(code+'\n')
            # if sesso==None:
            #     sesso="NoSex_in_Anagrafica"
            self.CreateReport(sesso)
            if sesso_tmp!=None:
                only_segm=self.PrepareTraining()
                file_training.write(code+'/'+sesso_tmp+'/'+only_segm+'\n')
#        print("-------------------------------------")
        pprint(self.dict_sex)
        pprint(self.dict_sex,file_report)
        print("-------------------------------------")
        print(count_line_hash)


    def CheckInDict(self,code):
        try:
            self.sex_eprice=self.dict_eprice[code]
        except KeyError:
            self.sex_eprice=None
        try:
            self.sex_saldi=self.dict_saldi[code]
        except KeyError:
            self.sex_saldi=None
        if self.sex_eprice!=None and self.sex_saldi!=None:
            if self.sex_eprice==self.sex_saldi:
                return self.sex_eprice
            else:
                print('##############################################################CONTRAST_ANAG')
                return "CONTRAST_ANAG"
        else:
            if self.sex_eprice!=None:
                return self.sex_eprice
            elif self.sex_saldi!=None:
                return self.sex_saldi
            else:
                return None

    def CreateReport(self,sesso):
 #       print(sesso)
        self.dict_sex['Total_line']=self.dict_sex['Total_line']+1
        if sesso not in self.dict_sex:
            self.dict_sex[sesso]=0
        self.dict_sex[sesso]=self.dict_sex[sesso]+1


    def PrepareTraining(self):
        inizio=0
        string=self.string
        while inizio<len(string) and inizio!=-1:
            print(string)
            print(string.find('^'))
            inizio=string.find('^')
#            print("--------------",inizio)
            if inizio!=-1:
                string=string[inizio+1:]
        print(string)
        return string












def main(FileEprice,FileSaldi,outFile,FileKrux):
    logging.info("START")
    logging.info("Processing ePrice anagrafica")
    dict_eprice={}
    lines_in_eprice=0
    with open(FileEprice,'r',encoding='mac_roman') as ep:
        for line in ep:
            dict_line_ob=DictCreation(line)
            dict_line=dict_line_ob.createDict()
            dict_eprice_ob=CheckFileds(dict_line,dict_eprice)
            dict_eprice=dict_eprice_ob.checkFileds_dict()
            lines_in_eprice+=1
    logging.info("linee in eprice:%i, chiavi:%i"%(lines_in_eprice,len(dict_eprice.keys())))
    logging.info("Processing SaldiPrivati anagrafica")
    dict_saldi={}
    lines_in_saldi=0
    with open(FileSaldi,'r',encoding='mac_roman') as sa:
        for line in sa:
            dict_line_ob=DictCreation(line)
            dict_line=dict_line_ob.createDict()
            dict_saldi_ob=CheckFileds(dict_line,dict_saldi)
            dict_saldi=dict_saldi_ob.checkFileds_dict()
            lines_in_saldi+=1
    logging.info("linee in eprice:%i, chiavi:%i"%(lines_in_saldi,len(dict_saldi.keys())))
    logging.info("Start SEX check")
    krux_check=CheckSex(FileKrux,outFile,dict_eprice,dict_saldi)
    krux_check.CheckSexLine()
    logging.info("END")
#    pprint(dict_eprice)















if __name__=="__main__":
   opts, args = getopt(sys.argv[1:], "e:s:o:k:h")
   opts = dict(opts)
   inFile=None
   outFile=None
   #for opt, arg in opts:
   if '-e' in opts:
      FileEprice=str(opts['-e'])
   if '-s' in opts:
      FileSaldi=str(opts['-s'])
   if '-k' in opts:
      FileKrux=str(opts['-k'])
   if '-o' in opts:
      outFile=str(opts['-o'])
   if '-h' in opts:
      usage('msg')
   if ('-e' not in opts==True and '-s' not in opts==True and '-o' not in opts==True and '-k' not in opts==True and '-h' not in opts==True):
       usage('0')
   main(FileEprice,FileSaldi,outFile,FileKrux)
