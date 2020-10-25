#!/usr/bin/env python3

"""checkCardReaders.py: Use a local MySQL database to keep track of card readers and produce a 'changes' JSon document."""

__author__ = "Hans Liss"
__copyright__ = "Copyright 2020, Hans Liss"
__license__ = "BSD 2-Clause License"
__version__ = "1.1"
__maintainer__ = "Hans Liss"
__email__ = "Hans@Liss.nu"
__status__ = "Example code"

from zeep import Client
import MySQLdb
import uuid
import sys
import datetime
import configparser
import json
import argparse

## Read command-line parameters and configuration file
parser = argparse.ArgumentParser(description='Find changes in CardReaders')
parser.add_argument('-c', '--configfile', required=True,
                    help='path to configuration file')
parser.add_argument('-i', '--instance', required=True,
                    help='name of the instance to use from the config file')
parser.add_argument('-l', '--logprefix',
                    help='prefix for log files. Datestamp will be added')
parser.add_argument('-f', '--force', action='store_true',
                    help='register changes even when deletes exceeds 200')

args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.configfile)

if args.logprefix is not None:
    logfile = open(datetime.date.today().strftime(args.logprefix + "%Y-%m-%d"), "a")
    def log(str):
        logfile.write(datetime.datetime.now().strftime("%H:%M:%S\t") + str + "\n")
else:
    def log(str):
        pass

wsdl = config[args.instance]['wsdl']
endpoint = config[args.instance]['endpoint']
sessiontoken = config[args.instance]['sessiontoken']

# We do some fairly ugly string concatenation to create SQL queries below. 
readerFields = ['Id', 'ParentFolderPath', 'Name', 'Description', 'AccessPointId', 'CardReaderType', 'SecurityLevel']

try:
    conn = MySQLdb.connect(
        host = config[args.instance]['db_host'],
        port = 3365,
        user = config[args.instance]['db_user'],
        password = config[args.instance]['db_password'],
        database = config[args.instance]['db_db'],
    )
    dbCursor = conn.cursor()
    dbCursor.execute("CREATE TEMPORARY TABLE readersTemp like readers")
except MySQLdb.Error as e:
    print(f"Error connecting to MySQL Platform: {e}")
    sys.exit(1)



## Create a SOAP client and from that, create a new service with the correct endpoint
client = Client(wsdl)
client.service._binding_options['address'] = endpoint

## Request data should contain whatever is in the 'request' subdocument within the
## SOAP request XML
request_data={'request' : {'SessionToken' : uuid.UUID('{' + sessiontoken + '}'),
                           'MessageId' : uuid.uuid4(),
                           'PageSize' : 100}}

done=False
pageNo=0
doneCount=0
while (not done):
    request_data['request']['PageIndex']=pageNo
    ## Call the method and get a response object
    try:
        response=client.service.GetCardReadersList(**request_data)
    except:
        e = sys.exc_info()[0]
        print(f"SOAP Error: {e}")
        sys.exit(1)

    totalCount = response.TotalCount
    batch = []
    for reader in response.Results.__values__['CardReaderModel']:
        values = []
        for fieldName in readerFields:
            values.append(reader[fieldName])
        batch.append(values)
    try:
        queryString = "INSERT INTO readersTemp ("
        first = True
        for fieldName in readerFields:
            if(first):
                first = False
            else:
                queryString += ","
            queryString += fieldName
        queryString += ") values (%s,%s,%s,%s,%s,%s,%s)"
        dbCursor.executemany(queryString, batch)
    except MySQLdb.Error as e:
            print(f"Error on insert: {e}")
            sys.exit(1)

    doneCount = doneCount + len(response.Results.__values__['CardReaderModel'])
    pageNo = pageNo + 1
    #print("Done %d out of %d, at page %d" % (doneCount, totalCount, pageNo))
    if doneCount >= totalCount:
        done = True

deleted = [];
added = [];
modified = [];
# These are deleted
dbCursor.execute('SELECT r.Id from readers r left join readersTemp rt on rt.Id = r.Id where rt.Id IS NULL')
for row in dbCursor:
    deleted.append(row[0])
    log("Deleted: %d" % row[0])

# select all from readersTemp left join readers
fieldListRt = ""
fieldListR = ""
fieldListChanged = ""
first = True
for fieldName in readerFields:
    if(first):
        first = False
    else:
        fieldListRt += ","
        fieldListR += ","
        fieldListChanged += " OR "
    fieldListRt += "rt." + fieldName
    fieldListR += "r." + fieldName
    fieldListChanged += "NOT ( rt." + fieldName + " <=> r." + fieldName + ")"
queryString = "SELECT " + fieldListRt + "," + fieldListR + " from readersTemp rt left join readers r on rt.Id = r.Id where r.Id IS NULL or " + fieldListChanged

dbCursor.execute(queryString)
for row in dbCursor:
    # If right side of JOIN is null, the reader has been added
    if row[len(readerFields)] is None:
        reader = {}
        for i in range(len(readerFields)):
            reader[readerFields[i]] = row[i]
        added.append(reader)
        log("Added: %d" % row[0])
    else:
        reader = {}
        reader['Id'] = row[0]
        for i in range(len(readerFields)):
            if row[i] != row[i + len(readerFields)]:
                reader[readerFields[i]] = row[i]
                log("Modified: %d field %s changed from \"%s\" to \"%s\"" % (row[0], readerFields[i], row[i + len(readerFields)], row[i]))
        modified.append(reader)

if len(deleted) < 200 or args.force:
    if len(deleted) > 0 or len(added) > 0 or len(modified) > 0:
        dbCursor.execute("DELETE FROM readers")
        dbCursor.execute("INSERT INTO readers SELECT * FROM readersTemp")
        conn.commit()
        update={}
        update['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        update['deleted'] = deleted
        update['added'] = added
        update['modified'] = modified
        print(json.dumps(update, indent=2))
else:
    print("The number of deletes is large (%d) and the -f flag was not given. Doing nothing." % len(deleted))
    
conn.close()
