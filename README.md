# IECTools
Bravida SystemHouse Solutions Integra API toolkit

This requires the "zeep" SOAP library. Install with
```bash
pip3 install zeep
```

You need to put the WSDL file for your Integra server in a suitable place. You can fetch it from `http[s]://<server>:<port>/IEC?singleWsdl`

There's a sample .ini file included, so you can just copy that and modify it.

Enter, at a minimum, the wsdl path, the actual endpoint address and the session token in the config file, place that file in a suitable location, well protected.

## getPerson.py

Run
```bash
python3 getPerson.sh <config file> <environment> <ID>
```

Example: You store the wsdl file as /usr/local/share/IEC.wsdl and update the wsdl setting in the .ini file for the "Prod" environment.
Then you store the .ini file as /usr/local/etc/IEC.ini and protect it so that only relevant users can read it, and then you run
```bash
python3 getPerson.sh /usr/local/etc/IEC.ini Prod 54123
```

If everything is correctly set up, it will print the FreeInfo1 field and Name of the cardholder with the ID "54123".

## checkCardReaders.py

Create a local MySQL/MariaDB database, add a user with access to the database, and create a table "readers":
```sql
create database iectools;
grant all on iectools.* to 'iectools'@'localhost' identified by 'foobar';
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

Add the database configuration to the config file, and run
```bash
python3 getPerson.sh /usr/local/etc/IEC.init Prod
```

The script will load all the card readers from Integra into a temporary table, compare this with the master table and produce a JSon document listing deleted, added and modified readers, including the relevant fields.

You may want to modify this to call some kind of service endpoint if you want this to generate events on an enterprise integration bus. Please note that the first run will produce a JSon document with *all* the readers as "added". You may want to do a dry run.