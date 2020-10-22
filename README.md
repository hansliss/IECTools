# IECTools
Bravida SystemHouse Solutions Integra Easy Connect (IEC) API toolkit

## Introduction
### Dependencies
This requires the "zeep" SOAP library. Install with
```bash
pip3 install zeep
```

Scripts that use a local database require the MySQLdb package for python. On CentOS
and other yum-based systems, you should be able to find it as the ```MySQL-python```
package. On Ubuntu and other debian-based systems, install the ```python-mysqldb```
package. If you are using Windows, Google is your friend.

### Configuration
You need to put the WSDL file for your Integra server in a suitable place.
You can fetch it from `http[s]://<server>:<port>/IEC?singleWsdl`

There's a sample .ini file included, so you can just copy that and modify it.

Enter, at a minimum, the WSDL path, the actual endpoint address and the session
token in the config file, place that file in a suitable location, well protected.

The examples below assume that you've downloaded the WSDL file and set all the
relevant settings in the .ini file for the "Prod" environment, stored the .ini
file as /usr/local/etc/IEC.ini and protected it so that only relevant users can
read it.

## getPerson.py

### Introduction
This script will retrieve a single CardHolder by ID and print out selected details
about that CardHolder. In the current version it will print out the FreeInfo1 field
as NIN (here "PNR" for non-obvious reasons) and the name, composited from given name
and surname.

### Usage

```bash
python3 getPerson.sh <config file> <environment> <ID>
```

### Example
#### Command
```bash
$ python3 getPerson.sh /usr/local/etc/IEC.ini Prod 54123
```
#### Result
```
PNR: 12345678
Name: Allan Kaka
```

## checkCardReaders.py

### Introduction
This script will load all the card readers from Integra into a temporary table,
compare this with the master table and produce a JSon document containing deleted,
added and modified readers, including the relevant fields.

You may want to modify this to call some kind of service endpoint if you want this
to generate events on an enterprise integration bus.

Please note that the first run will produce a JSon document with *all* the readers
as "added". You may want to do a dry run to seed the database.

### Preparations
Create a local MySQL/MariaDB database, add a user with access to the database, and create a table "readers":
```sql
create database iectools;
grant all on iectools.* to 'iectools'@'localhost' identified by 'whatever';
create table readers (
       	     Id int,
       	     ParentFolderPath varchar(255),
	     Name varchar(255),
	     Description varchar(255),
	     AccessPointId int,
	     CardReaderType varchar(32),
	     SecurityLevel varchar(32),
	     primary key(Id));
```
Add the database configuration to the config file.

### Usage

```bash
python3 checkCardReaders.sh <config file> <environment>
```

### Example

#### Command
```bash
python3 getPerson.sh /usr/local/etc/IEC.init Prod
```
#### Result
```json
{
  "timestamp": "2020-10-22T08:36:51.819563Z",
  "deleted": [
    4711
  ],
  "added": [
    {
      "Id": 621235,
      "ParentFolderPath": "Building 3\\Custodial",
      "Name": "0050-32 Storeroom 3",
      "Description": "New 2020-10-22",
      "AccessPointId": 625420,
      "CardReaderType": "SimonsVoss",
      "SecurityLevel": "Unlocked"
    }
  ],
  "modified": [
    {
      "Id": 598727,
      "Name": "0031-12 Office",
      "CardReaderType": "SmartIntegoVCN"
    },
    {
      "Id": 534269,
      "Name": "0011-02 West side"
    }
  ]
}
```

