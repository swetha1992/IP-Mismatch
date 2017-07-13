# IP-Mismatch.
The idea of the code is to identify IP and subnetmask pair that is mismatched from original and actual setup

Program Flow:
1.Reads the give IPDATA-JSON and extract IP, Subnet and hostname and put it to "extract.csv".
2.USPOP and UKPOP are set of JSON files obtained from various APIs that store the ip/subnet values from different servers running across the globe.(It contains lakhs of data)
3.Reads every file from the two folders and generates "truesource.csv" which is actual implementation of IP, Subnet pair.
4.Comparison is made between both the files and result.csv is obtained. (Since lakh of data is to be checked, simple loop with condtion would take lot of time and hence, dictionary was created for each pair and then comparion was made. Since hashing is effective way of searhing value in key,value pair, it reduced lot of time)
5.An HTML file would be created finally the shows the the mismatched ip/subnet pair in a table format along with their host name.
