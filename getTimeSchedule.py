#!/usr/bin/env python3

"""getTimeSchedule.py: Get a Time Schedule by Id and print some info about it."""

__author__ = "Hans Liss"
__copyright__ = "Copyright 2021, Hans Liss"
__license__ = "BSD 2-Clause License"
__version__ = "1.1"
__maintainer__ = "Hans Liss"
__email__ = "Hans@Liss.nu"
__status__ = "Example code"

from zeep import Client
import uuid
import sys
import configparser
import argparse

## Read command-line parameters and configuration file
parser = argparse.ArgumentParser(description='get a Time Schedule by ID and print some fields')
parser.add_argument('-c', '--configfile', required=True,
                    help='path to configuration file')
parser.add_argument('-i', '--instance', required=True,
                    help='name of the instance to use from the config file')
parser.add_argument('-I', '--id', required=True,
                    help='Id of the Time Schedule you want to retrieve')
parser.add_argument('fields', metavar='field', nargs='+')

args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.configfile)

wsdl = config[args.instance]['wsdl']
endpoint = config[args.instance]['endpoint']
sessiontoken = config[args.instance]['sessiontoken']

## Create a SOAP client and from that, create a new service with the correct endpoint
client = Client(wsdl)
client.service._binding_options['address'] = endpoint

## Request data should contain whatever is in the 'request' subdocument within the
## SOAP request XML
request_data={'request' : {'SessionToken' : uuid.UUID('{' + sessiontoken + '}'),
                           'MessageId' : uuid.uuid4(),
                           'Id' : args.id}}

## Call the method and get a response object
response=client.service.GetTimeScheduleById(**request_data)

## Print out the result
for field in args.fields:
    print(field + ": " + str(response[field]))

