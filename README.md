# openBEM report
The EPC data is shared publically here: https://epc.opendatacommunities.org. The epc website let's you bulk download all the EPC data for the England and Wales. I wanted a way to analyse the data in the EPC data in a certain area and automatically create a report of the data.  The script extracts data from the open EPC data and generates a report when given the certificates.csv file is given as an input. 

The report includes:
- A graph of the number of EPCs against property type (house, flat, massionette, Bunaglow, Park home)
- A graph of the number of EPCs at energy ratings against number of records

```
python3 open_bem.py -i /path/to/certificates.csv
```

Future improvements:
- Add more plots
- Allow more than one local authority to be run in one time
- Improve CLI so you only have to pass in name of authority
- Add all the data to a DB