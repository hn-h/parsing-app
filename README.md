# parsing-app

Parse data with different formats to unified format with well defined structure, writes it to json files and inserts it into Mongo database.

Currently available formats: ```xml, csv```. 

## Installation

First you need to install modules which is required to run this app (you can make a new environment and install this modules into, check [virtualenv](https://virtualenv.pypa.io/en/latest/index.html)).

You can install this modules using:
```bash
pip install -r requirements.txt
```

## Usage
you can use ```parser.py -h``` to check updated usage instructions and supported formats.
```bash
$ parser.py -h
```
```
App which parsing data into certain json format and inserting it into mongodb

positional arguments:
  xml <file.xml>        parsing file.xml data and output it in json format
  csv <customer_file.csv> <vehicle_file.csv>
                        parsing csv files data and output it in json format

optional arguments:
  -h, --help            show this help message and exit
```
### Example
```python
parser.py xml file1.xml
#write your file path in case it's not in the same directory

parser.py csv customers_file1.csv vehicles_file1.csv
#write your files paths in case files is not in the same directory
```

## Output
For xml files, output exists in ```output/xml/``` directory.  
For csv files, output exists in ```output/csv/``` directory.  
In both cases output also is inserted into a Mongodb hosted on AWS server, xml collection for xml files and csv collection is for csv files.

You can check database through ```mongodb-compass``` using below connection/link:  
```mongodb+srv://trufla_admin:P%40ssw0rd@cluster0.anspp.mongodb.net/trufla```
