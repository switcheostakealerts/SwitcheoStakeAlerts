import urllib.request
import json 
import time
import os.path
import sys
import datetime


def getJSONFromUrl(fetch_url):
    #Fetch json data from the url
    with urllib.request.urlopen(fetch_url, timeout=1) as url:
        data = json.loads(url.read().decode())
        return data


def requestFromAPI(request):
    #sends a request to the API, returns json data

    url = 'https://tradescan.switcheo.org/' + request
    print('Request: ' + url, end="")
    data = getJSONFromUrl(url)
    print(' SUCCESS')
    return data


def requestFromAPIWithRetry(request):
    #Gets data from API, retry until success.

    retryCounter = 0
    while True :
        try:
            return requestFromAPI(request)
        except:
            #sys.stdout.flush()
            retryCounter = retryCounter + 1
            print(' FAILED ' + str(retryCounter)+ 'x')
            time.sleep(1)     



def loadJSONFromFile(file):
    #reads a json string from file
    with open(file) as json_file:
        return json.load(json_file)



def saveJSONToFile(data,file):
    #Save a json string to a file

    with open(file, "w") as write_file:
        json.dump(data, write_file, indent=4, sort_keys=True)    



def getChangeInSigningInfos(oldInfo,newInfo):
    #Compares old signing info to new signing info
    
    #newInfo should always be from a later block, sometimes the API does not give the latest block
    if int(oldInfo['height']) >= int(newInfo['height']):
        return [{'error': 'New Block Height is not larger than old block height'}]

    changes = []

    #Loop though validators in the old info
    for validator in oldInfo['result']:

        address = validator['address']

        #Search for the address in the new info
        foundMatch = False
        for new in newInfo['result']:
            if address == new['address']:
                foundMatch = True
                break

        if not foundMatch:
            print('Address ' + address + ' in old not found in new')
            #TODO: send warning ping
            continue

        # If the jailed_until tag has increased the validator has been slashed
        newDateStr = new['jailed_until'][0:19]       #ignore ms
        oldDateStr = validator['jailed_until'][0:19] #ignore ms
        #print(newDateStr,oldDateStr)

        newDate = datetime.datetime.strptime(newDateStr, '%Y-%m-%dT%H:%M:%S') #2021-02-10T11:44:20 (.204519008Z) cut off
        oldDate = datetime.datetime.strptime(oldDateStr, '%Y-%m-%dT%H:%M:%S')   


        if newDate > oldDate:
            #moniker = getMonikerFromConsAddress(address) or address
            changes.append({'address':address,'jailed_until':newDate})

    return changes

def getMonikerFromConsAddress(address):
    #Gets the moniker of a validator from an address

    validators = requestFromAPIWithRetry('get_all_validators')

    for v in validators:
        if v['ConsAddress'] == address:
            return v['Description']['moniker']

    #If it is still not there then we can't find it.
    return False

def getMonikerFromSavedConsAddress(address):
    #Gets the moniker of a validator from an address

    if os.path.isfile('all_validators.json'):
        #Load validator info from file
        validators = loadJSONFromFile('all_validators.json')

        #If the address is there return it
        for v in validators:
            if v['ConsAddress'] == address:
                return v['Description']['moniker']

        #If the address is not there update the file and try again
        validators = requestFromAPIWithRetry('get_all_validators')
        saveJSONToFile(validators,'all_validators.json')

        for v in validators:
            if v['ConsAddress'] == address:
                return v['Description']['moniker']

        #If it is still not there then we can't find it.
        return False

    else:

        #download file and try again
        validators = requestFromAPIWithRetry('get_all_validators')
        saveJSONToFile(validators,'all_validators.json')
        return getMonikerFromConsAddress(address)



def getNewSigningInfos():

    #print('Getting new signing infos...')

    while True:
        new_signing_infos = requestFromAPIWithRetry('slashing/signing_infos')

        if 'result' in new_signing_infos:
            break

        print('Getting new signing infos... No result in returned json.')

    #print('Getting new signing infos... SUCCESS')

    return new_signing_infos


def alertMessageSigningInfos(changes):

        #Block height error
        if len(changes)==1:
            if 'error' in changes[0]:
                return '0'

        #No change
        if len(changes) == 0:
            return '1'

        #Change in jail status
        if len(changes)>0:
            message = []
            for m in changes:
                time = m['jailed_until'].strftime("%Y-%m-%d %H:%M:%S")
                name = getMonikerFromConsAddress(m['address']) or m['address']
                message.append('Validator ' + name + ' has been jailed until '+ time + ' for missing too many blocks. Tokens delegated to this validator have been slashed.')

        return message


def main():

    #print(os.path)
    #print(sys.path)
    #print(os.path.dirname(__file__))

    old_signing_infos = loadJSONFromFile('signing_infos.json')
    while True:
        
        new_signing_infos = getNewSigningInfos()
        changes = getChangeInSigningInfos(old_signing_infos, new_signing_infos)
        message = alertMessageSigningInfos(changes)
        print(changes, message)

        if message == '0':
            time.sleep(5)
            continue
   
        print('  Updating signing_infos.json')
        old_signing_infos = new_signing_infos
        saveJSONToFile(old_signing_infos, 'signing_infos.json')

        time.sleep(60)


if __name__ == '__main__':
    main()


# def getRequestFromPublicNodes(request, nodes):
#     #https://tradescan.switcheo.org/monitor
#     for node in nodes:
#         url = 'http://' + node['ip'] + ':1318/' + request
#         #print(url)
#         try: 
#             getDataFromUrl(url)
#             print(url)
#             #print(getDataFromUrl(url))
#         except:
#             print(url + ' not readable')





# public_nodes = loadJSONFromFile('monitor.json')