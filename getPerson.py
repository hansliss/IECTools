#!/usr/bin/python3

from zeep import Client
import uuid
import sys
import configparser

## Read command-line parameters and configuration file
config = configparser.ConfigParser()
config.read(sys.argv[1])
ENV = sys.argv[2]
ID = sys.argv[3]
wsdl = config[ENV]['wsdl']
endpoint = config[ENV]['endpoint']
sessiontoken = config[ENV]['sessiontoken']

## Create a SOAP client and from that, create a new service with the correct endpoint
client = Client(wsdl)
client.service._binding_options['address'] = endpoint

## Request data should contain whatever is in the 'request' subdocument within the
## SOAP request XML
request_data={'request' : {'SessionToken' : uuid.UUID('{' + sessiontoken + '}'),
                           'MessageId' : uuid.uuid4(),
                           'Id' : ID}}

## Call the method and get a response object
response=client.service.GetCardholderById(**request_data)

## Print out the result
print("PNR: " + response.FreeInfo1)
print("Name: " + response.FirstName + " " + response.Surname)

