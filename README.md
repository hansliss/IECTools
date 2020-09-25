# IECTools
Bravida SystemHouse Solutions Integra API toolkit

This requires the "zeep" SOAP library. Install with
     pip3 install zeep

You need to put the WSDL file for your Integra server in a suitable place. You can fetch it from `http[s]://<server>:<port>/IEC?singleWsdl`

There's a sample .ini file included, so you can just copy that and modify it.

Enter the wsdl path, the actual endpoint address and the session token in the config file, place that file in a suitable location, well protected, and run
```bash
python3 getPerson.sh <config file> <environment> <ID>
```

Example: You store the wsdl file as /usr/local/share/IEC.wsdl and update the wsdl setting in the .ini file for the "Prod" environment.
Then you store the .ini file as /usr/local/etc/IEC.ini and protect it so that only relevant users can read it, and then you run
```bash
python3 getPerson.sh /usr/local/etc/IEC.ini Prod 54123
```

If everything is correctly set up, it will print the NIN and Name of the cardholder with the ID "54123".
