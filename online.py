import glob
import json
import shodan
import time

shodan_client = shodan.Shodan("UP0w4Q2nzKn3RMJYB7XXgN25xCNI0YTv")

file_list = glob.glob("onionscan_results/*.json")

file = open('OpenServices.txt','w')

ssh_key_list = []
key_to_hosts = {}

for json_file in file_list:

    

    with open(json_file, "rb") as fd:

        scan_result = json.load(fd)

        if scan_result['online'] is not 'false':

        	print scan_result['hiddenService']

        	file.write(scan_result['hiddenService']+"\n")



file.close()