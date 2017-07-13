import json
import csv
import os, sys
from urllib.request import urlopen
from ipaddress import IPv4Network
from ipaddress import IPv4Interface

#Filenames and Paths
PRIMARY_JSON_FILE="samplejson.json"
EXTRACT_CSV="extract.csv"
TRUE_SOURCE_CSV="truesource.csv"
RESULT_CSV="result.csv"
DATA_CENTRE_CSV="datacentre.csv"
RESULTANT_HTML="resultant.html"
PATH_USPOP="C:/Swetha/Job/json task/json task - release -1/USPOP/USPOP"
PATH_UKPOP="C:/Swetha/Job/json task/json task - release -1/UKPOP/UKPOP"

#globally used variables
global IP_MISMATCH_COUNT
global IP_MISMATCH_LIST

#reads the given JSON (sampleJSON.json) and creates extract.csv which is an extract of ip, subnetmask and hostname from sampleJSON
def readJSON():
 with open(PRIMARY_JSON_FILE) as data_file:    
     data = json.load(data_file)
     no_of_json_obj=len(data)
     csvlist=[]
     for i in range(0,no_of_json_obj):
            if 'vip_count' in data[i]:
                no_of_vips=data[i]['vip_count']
            if 'vips' in data[i]:
                    for j in range(0,no_of_vips):
                        csvlist.append([data[i]['vips'][j][0],data[i]['vips'][j][3],data[i]['hostname']])
     w=csv.writer(open(EXTRACT_CSV, "w"))
     w.writerows(csvlist)
     
#generates truesource of ip and subnet mask reading data from various APIS
def generateTrueSource():
    iplist = []
    iphostswithsub = []
    ipdict = {}
    w = csv.writer(open(TRUE_SOURCE_CSV, "a"))
    directory_list=[PATH_USPOP,PATH_UKPOP]
    cwd=os.getcwd()
    csvlist=[]
    
    #move to the specified directory and list the files from the directory
    for path in directory_list:
        print(path)
        os.chdir(path)
        file_list=os.listdir(path)
        for file_name in file_list:
            with open(file_name) as datafile :
                data = json.load(datafile)
                for key in data:
                    iplist.append(key["subnet"])
                for key1 in iplist:
                    interface = IPv4Interface(key1)
                    value = interface.with_netmask
                    ip,netmask = value.split("/") 
                    for addr in IPv4Network(key1,strict=False):
                        ipdict[addr] = netmask
                for key, val in ipdict.items():
                        csvlist.append([key, val])
                w.writerows(csvlist)
        os.chdir(cwd)
#compare the two files EXTRACT_CSV and TRUE_SOURCE_CSV and generates RESULT_CSV
def compareFILES():
     ipdict = {'ip':'subnetmask'}
     ipdicttruth ={'ip':'subnetmask'}
     iphostdict={'ip':'hostname'}
     csvlist=[]
     w = csv.writer(open(RESULT_CSV, "a"))
     
     #read extract.csv and generate ipdcit
     with open(EXTRACT_CSV,'r') as csvfile:    
         rows = csv.reader(csvfile)
         for row in rows:
               if row:
                   ipdict[row[0]]=row[1]
                   iphostdict[row[0]]=row[2]

     #read truesource.csv and generate ipdcittruth
     with open(TRUE_SOURCE_CSV, 'r') as csvfile:
         rows = csv.reader(csvfile)
         for row in rows:
             if row:
                 ipdicttruth[row[0]]=row[1]
             
     #generate mismatching elements
     for key,val in ipdict.items():
         if key in ipdicttruth.keys():
             if ipdict[key] and ipdicttruth[key] and ipdict[key]!=ipdicttruth[key]:
                 csvlist.append([key,ipdict[key],ipdicttruth[key],iphostdict[key]])
     w.writerows(csvlist)

     #setting global variables 
     global IP_MISMATCH_COUNT
     IP_MISMATCH_COUNT=len(csvlist)
     global IP_MISMATCH_LIST
     IP_MISMATCH_LIST=csvlist

#generates DATA_CENTRE_CSV
def generateDataCentreIpList():
    data_centre_ip_dict={}
    with open(PRIMARY_JSON_FILE) as data_file:    
     data = json.load(data_file)
     no_of_json_obj=len(data)
     csvlist=[]
     w = csv.writer(open(DATA_CENTRE_CSV, "w"))
     for i in range(0,no_of_json_obj):
            if 'hostname' in data[i] and 'vips' in data[i]:
                if data[i]['hostname'] not in data_centre_ip_dict:
                    data_centre_ip_dict[data[i]['hostname'].split('.')[1]]=data[i]['vips'][0][0]
     for key,val in data_centre_ip_dict.items():
                 csvlist.append([key,data_centre_ip_dict[key]])
     w.writerows(csvlist)

#generates HTML
def createHTML():
    style= """
            <html>
            <head>
            <title> task</title>
            <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
            <style> 
                 body {
                 font-family: 'Roboto', sans-serif;
                 }
                 table {
                 border-collapse: collapse;
                 border-spacing: 0;
                 border: 1px solid #bbb;
                 }
                 th {
                    border-top: 1px solid #ddd;
                    padding: 4px 8px;
                    background: #99ccff;
                }
                td{
                    border-top: 1px solid #ddd;
                    padding: 4px 8px;
                    background: #e6f2ff;
                }
                p{
                	margin: 40px;
                	margin-left: -480px;
                	font-size: 18px
                }
             </style>
             </head>  
            """
    
    with open(RESULTANT_HTML, 'w') as htmlFile:
        htmlFile.write(style)
        htmlFile.write('<body><center>')
        htmlFile.write('<p>Mismatched IP count :%s</p>'% (IP_MISMATCH_COUNT))
        htmlFile.write('<table> <tr> <th>IP</th> <th width="40%">HOST NAME</th> <th> CURRENT SUBNETMASK</th> <th> ACTUAL SUBNETMASK</th> </tr> ')
        for i in range(0, len(IP_MISMATCH_LIST)):
            htmlFile.write('<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td> </tr>' %(IP_MISMATCH_LIST[i][0],IP_MISMATCH_LIST[i][3],IP_MISMATCH_LIST[i][1],IP_MISMATCH_LIST[i][2]))
        htmlFile.write('</table>')  
        htmlFile.write('</center></body>')
        htmlFile.write('</html>')

try :
    readJSON();
    generateTrueSource();
    compareFILES();
    generateDataCentreIpList()
    createHTML();

except Exception as e:
    print("It seems there is a problem reading the file. The problem says :"+str(e))
     

