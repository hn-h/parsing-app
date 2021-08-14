from classes import Transaction, Customer, Vehicle
import sys
import json
from bs4 import BeautifulSoup
import time
from pathlib import Path
import pandas as pd
import requests
import pymongo
import urllib


def db_connect():
    """
    fuction to connect to mongodb using pymongo module
    """
    db_credentials = {
                    'database_name': 'trufla',
                    'username': 'trufla_admin',
                    'password': 'P@ssw0rd',
                    'cluster': 'cluster0'
    }
    CONNECTION_STRING = "mongodb+srv://{}:{}@{}.anspp.mongodb.net" \
                        "/{}?retryWrites=true&w=majority"
    CONNECTION_STRING = CONNECTION_STRING.format(
                            db_credentials['username'],
                            urllib.parse.quote(db_credentials['password']),
                            db_credentials['cluster'],
                            db_credentials['database_name'])

    client = pymongo.MongoClient(CONNECTION_STRING)
    # get database from cluster
    return client[db_credentials['database_name']]


def insert_to_db(format, data):
    """
    inserts data into connected mongodb
    :format: data file format (xml, csv, ...)
    :data: data to be inserted in python dictionary format
    """

    db = db_connect()

    if format == 'xml':
        xml_collection = db['xml']
        xml_collection.insert_one(data)

    elif format == 'csv':
        csv_collection = db['csv']
        csv_collection.insert_one(data)


def decode_vin(vin_number, model_year):
    # define a list of parameters needed from the vin API
    info_parameters = ['Model', 'Manufacturer', 'PlantCountry', 'VehicleType']

    url = "https://vpic.nhtsa.dot.gov/api/vehicles/" \
          "DecodeVinValues/{}?format=json&modelyear={}"
    url = url.format(vin_number, model_year)

    # make a get request to the API using requests module
    res = requests.get(url)

    # convert json to python dictionary
    res_dic = res.json()

    # return a list of needed information
    return [res_dic['Results'][0][params] for params in info_parameters]


def parser(file_format, source_path1, source_path2):
    """
    handles the parsing process depending on the arguments.
    :file_format: format of the source file (xml, csv, ...)
    :source_path1: path to first source file
    :source_path2: path to second source file
    """

    # define a Transaction object to start input data in
    transaction = Transaction()

    # in case input file doesn't exist
    if file_format == 'xml':
        try:
            with open(source_path1, 'r') as f:
                data = f.read()
        except FileNotFoundError:
            print("Can't find source file, please make sure file exists!")
            return

        # using beautifulsoup to start reading data using tags name
        bs = BeautifulSoup(data, 'xml')
        # getting data using find method: bs.find(<nametag>).text
        transaction.file_name = source_path1
        transaction.date = bs.find('Date').text
        customer_tag = bs.find('Customer')
        transaction.customer = Customer(customer_tag.get('id'),
                                        customer_tag.find('Name').text,
                                        customer_tag.find('Address').text,
                                        customer_tag.find('Phone').text)

        # loop over vehicle tags and append into a transaction's vehicles list
        # as customer may have more than one car
        for vehicle in bs.find_all('Vehicle'):
            # get enriched data by decoding vin using API
            enriched_data = decode_vin(vehicle.find('VinNumber').text,
                                       vehicle.find('ModelYear').text)

            transaction.vehicles.append(
                                Vehicle(
                                        vehicle.get('id'),
                                        vehicle.find('Make').text,
                                        vehicle.find('VinNumber').text,
                                        vehicle.find('ModelYear').text,
                                        enriched_data[0], enriched_data[1],
                                        enriched_data[2], enriched_data[3]))

        # using Transaction.get_dic() to get a dictionary of transaction data
        data_dic = transaction.get_dic()

        # required output file name: <timeStamp>_<sourceFileName>.json
        out_filename = ('output/xml/' + str(time.time()) + '_' +
                        Path(source_path1).stem + '_enriched.json')

        # check if output directory exists, if not make one
        Path('output/xml/').mkdir(parents=True, exist_ok=True)

        # dump dictionary into a .json file
        # ensure_ascii is false in case names contains latin characters (é)
        with open(out_filename, 'w') as f:
            json.dump(data_dic, f, ensure_ascii=False, indent=3)
        # inserting data to database
        insert_to_db('xml', data_dic)

    elif file_format == 'csv':
        # in case no vehicle file was given
        if source_path2 == '':
            print('Please add 2 files for csv format.' +
                  ' customers file & vehicle file.')
            print('parser.py csv <customer file> <vehicle file>')
            return

        # reading csv files into pandas dataframe
        # Abort if can't find file
        try:
            customers = pd.read_csv(source_path1)
            vehicles = pd.read_csv(source_path2)
        except:
            print("Can't find source file, please make sure file exists!")
            return

        # change the date format to be YYYY-MM-DD
        customers['date'] = pd.to_datetime(customers.date)
        customers['date'].dt.strftime('%Y-%m-%d')

        # join data of the two files into one dataframe (inner join)
        data_joined = pd.merge(customers, vehicles, left_on='id',
                               right_on='owner_id', how='inner')

        # get a list of unique customers as some
        # customers has more than one car (after join)
        unique_customers_ids = data_joined.owner_id.unique()
        # loop over each customer and extract his data
        for cst_id in unique_customers_ids:
            cst = data_joined[data_joined.owner_id == cst_id]
            transaction.file_name = source_path1
            transaction.date = str(cst.date.iloc[0]).split(' ')[0]
            transaction.customer = Customer(str(cst_id),
                                            str(cst.name.iloc[0]),
                                            str(cst.address.iloc[0]),
                                            str(cst.phone.iloc[0]))

            # loop over each vehicle per customer
            for i in range(len(cst)):
                # get enriched data by decoding vin using API
                enriched_data = decode_vin(str(cst.vin_number.iloc[i]),
                                           str(cst.model_year.iloc[i]))

                transaction.vehicles.append(
                                    Vehicle(
                                        str(cst.id_y.iloc[i]),
                                        str(cst.make.iloc[i]),
                                        str(cst.vin_number.iloc[i]),
                                        str(cst.model_year.iloc[i]),
                                        enriched_data[0], enriched_data[1],
                                        enriched_data[2], enriched_data[3]))

            data_dic = transaction.get_dic()

            # output file name
            out_filename = ('output/csv/' + str(time.time()) + '_' +
                            Path(source_path1).stem + '_enriched.json')

            # check if output directory exists, if not make one
            Path('output/csv/').mkdir(parents=True, exist_ok=True)

            # get a json file for each customer in customers.csv
            with open(out_filename, 'w') as f:
                json.dump(data_dic, f, ensure_ascii=False, indent=3)

            # inserting data to database
            insert_to_db('csv', data_dic)

            # reset transaction parameters to start with next customer
            transaction = Transaction()

    else:
        print("Our app doesn't handle " + file_format +
              " format. Current available formats are [xml, csv].")


def help_screen():
    """
    function to add a help screen to the script (parser.py -h)
    """
    import argparse
    help = argparse.ArgumentParser(
        description='App which parsing data into certain json' +
                    ' format and inserting it into mongodb',
        epilog='Please note that current available formats are [xml, csv].')

    help.add_argument('[xml <file.xml>]',
                      help='parsing file.xml and output it in json format')

    help.add_argument('[csv <customer_file.csv> <vehicle_file.csv>]',
                      help='parsing csv files and output it in json format')

    help.parse_args()

# to run script from shell
if __name__ == '__main__':
    # to add a help screen [parser.py -h]
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        help_screen()

    file_format = sys.argv[1]
    source_path1 = sys.argv[2]
    try:
        source_path2 = sys.argv[3]
    except:
        source_path2 = ''

    parser(file_format, source_path1, source_path2)
