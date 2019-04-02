from __future__ import print_function

print("[HEEEYYYY!!!] Importing Modules")

from stem.control import Controller
from stem import Signal
from threading import Timer
from threading import Event

import codecs
import json
import os
import random
import subprocess
import sys
import time

#Initializing two EMpty list
#To hold List of onions 
onions = []
session_onions = []

identity_lock = Event()
identity_lock.set()


print("[HEYYYY!!!!] Building some helper functions")

def get_onion_list():

    #Check to see if This file exists
    #If so, open it and split the lines
    #and store tham in the array
    if os.path.exists("onion_master_list.txt"):

        with open("onion_master_list.txt") as fd:

            stored_onions = fd.read().splitlines()

    else:

        print("[!] No oinion master list Download it!")
        sys.exit(0)

    print("[*] Total Onions for scanning: %d" %len(stored_onions))

    return stored_onions




def store_onion(onion):

    print("[++] Storing %s in master list" %onion)

    #Write the hidden service (onion) to this file
    with codecs.open("onion_master_list.txt", "ab", encoding = "utf8") as fd:
        fd.write("%s\n" %onion)

    return


def run_onionscan(onion):

    print("[*] Onionscanning %s" %onion)

    process = subprocess.Popen(["onionscan", "webport=0", "--jsonReport", "--simpleReport= false",
                                onion], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    process_timer = Timer(300,handle_timeout,args=[process,onion])
    process_timer.start()

    # wait for the onion scan results
    stdout = process.communicate()[0]

    # we have received valid results so we can kill the timer 
    if process_timer.is_alive():
            process_timer.cancel()
            return stdout

    print("[!!!] Process timed out!")	

    return None


def handle_timeout(process,onion):
 
    global session_onions
    global identity_lock 

    # halt the main thread while we grab a new identity
    identity_lock.clear()

    # kill the onionscan process
    try:
            process.kill()
            print("[!!!] Killed the onionscan process.")
    except:
            pass

    # Now we switch TOR identities to make sure we have a good connection
    with Controller.from_port(port=9051) as torcontrol:

            # authenticate to our local TOR controller
            torcontrol.authenticate("PythonRules")

            # send the signal for a new identity
            torcontrol.signal(Signal.NEWNYM)

            # wait for the new identity to be initialized
            time.sleep(torcontrol.get_newnym_wait())

            print("[!!!] Switched TOR identities.")

    # push the onion back on to the list	
    session_onions.append(onion)
    random.shuffle(session_onions)

    # allow the main thread to resume executing
    identity_lock.set()	

    return

def process_results(onion, json_response):
    global onions
    global session_onions

    #If there is no results directory
    #Create it!!
    if not os.path.exists("onionscan_results"):
        os.mkdir("onionscan_results")

    #Write results to file
    #Named after the scan
    with open("%s/%s.json" % ("onionscan_results", onion), "wb") as fd:
        
        fd.write(json_response)
    
    #Play with the string
    #So its readable
    scan_result = ur"%s" %json_response.decode("utf-8")
    
    scan_result = json.loads(scan_result)

    #Search for linkedOnions
    #relatedOnionDomains
    #relatedOnionServices
    if scan_result['identifierReport']['linkedOnions'] is not None:
        add_new_onions(scan_result['identifierReport']['linkedOnions'])

    if scan_result['identifierReport']['relatedOnionDomains'] is not None:
        add_new_onions(scan_result['identifierReport']['relatedOnionDomains'])

    if scan_result['identifeirReport']['relatedOnionServices'] is not None:
        add_new_onions(scan_result['identifeirReport']['relatedOnionServices'])
        
    return

def add_new_onions(new_onion_list):

    global onions
    global sessions_onions

    for linked_onions in new_onions_list:

        if linked_onion not in onions and linked_onion.endswith(".onion"):

            print("[++] Discivered new .onion => %s" %linked_onion)

            onions.append(linked_onion)
            session_onions.append(linked_onion)
            random.shuffle(session_onions)
            store_onion(linked_onion)

    return


onions = get_onion_list()

random.shuffle(onions)
session_onions = list(onions)

count = 0

while count < len(onions):

    identity_lock.wait()


    print("[*] Running %d of %d." % (count, len(onions)))
    onion = session_onions.pop()


    if os.path.exists("onionscan_results/%s.json" %onion):
        
        print("[!] Already retrieved %s. Skipping." %onion)
        count += 1

        continue
    
    result = run_onionscan(onion)
    
    if result is not None:
        
        if len(result):
            process_results(onion, result)
            
            count += 1
    

