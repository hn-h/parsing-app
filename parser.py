from classes import Transaction, Customer, Vehicle
import sys, json
from bs4 import BeautifulSoup
import time
from pathlib import Path

def parser(file_format,source_path1):
    """
    handles the parsing process depending on the arguments.

    :file_format: format of the source file (xml, csv, ...)
    :source_path1: path to source file
    """
    # define a Transaction object to start input data in
    transaction = Transaction()
    if file_format=='xml':
        with open(source_path1, 'r') as f:
            data = f.read()

        # using beautifulsoup with xml parser to start reading data using tags name
        bs = BeautifulSoup(data, 'xml')
        #getting data using find method: bs.find(<nametag>).text
        transaction.file_name=source_path1
        transaction.date=bs.find('Date').text
        customer_tag=bs.find('Customer')
        transaction.customer.id=customer_tag.get('id')
        transaction.customer.name=customer_tag.find('Name').text
        transaction.customer.address=customer_tag.find('Address').text
        transaction.customer.phone=customer_tag.find('Phone').text
        #loop over vehicle tags and append into a transaction's vehicles list as customer may have more than one car
        for vehicle in bs.find_all('Vehicle'):
            transaction.vehicles.append(Vehicle(vehicle.get('id'),
                                                vehicle.find('Make').text,
                                                vehicle.find('VinNumber').text,
                                                vehicle.find('ModelYear').text))
        #using Transaction.get_dic() to get a dictionary of transaction data
        data_dic=transaction.get_dic()
        #required output file name: <timeStamp>_<sourceFileName>.json
        out_filename='output/xml/' + str(time.time()) + '_' + Path(source_path1).stem + '.json'
        #check if output directory exists, if not make one
        Path('output/xml/').mkdir(parents=True, exist_ok=True)
        #dump dictionary into a .json file, ensure_ascii is false in case names contains latin characters (é)
        with open(out_filename, 'w') as f:
            json.dump(data_dic, f, ensure_ascii=False, indent=3)

#to run script from shell
if __name__=='__main__':
    file_format=sys.argv[1]
    source_path1=sys.argv[2]
    parser(file_format,source_path1)
