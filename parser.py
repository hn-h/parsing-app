from classes import Transaction, Customer, Vehicle
import sys, json
from bs4 import BeautifulSoup
import time
from pathlib import Path
import pandas as pd

def parser(file_format,source_path1,source_path2):
    """
    handles the parsing process depending on the arguments.

    :file_format: format of the source file (xml, csv, ...)
    :source_path1: path to first source file
    :source_path2: path to second source file
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

    elif file_format=='csv':
        #reading csv files into pandas dataframe
        customers=pd.read_csv(source_path1)
        vehicles=pd.read_csv(source_path2)
        #change the date format to be YYYY-MM-DD
        customers['date']=pd.to_datetime(customers.date)
        customers['date'].dt.strftime('%Y-%m-%d')
        #join data of the two files into one dataframe (inner join)
        data_joined=pd.merge(customers, vehicles, left_on='id', right_on='owner_id', how='inner')
        #get a list of unique customers as some customers has more than one car (after join)
        unique_customers_ids = data_joined.owner_id.unique()
        #loop over each customer and extract his data into a list of transaction objects
        for cst_id in unique_customers_ids:
            cst = data_joined[data_joined.owner_id==cst_id]
            transaction.file_name=source_path1
            transaction.date=str(cst.date.iloc[0]).split(' ')[0]
            transaction.customer.id=str(cst_id)
            transaction.customer.name=str(cst.name.iloc[0])
            transaction.customer.address=str(cst.address.iloc[0])
            transaction.customer.phone=str(cst.phone.iloc[0])
            # loop over each vehicle per customer
            for i in range(len(cst)):
                transaction.vehicles.append(Vehicle(str(cst.id_y.iloc[i]),
                                                    str(cst.make.iloc[i]),
                                                    str(cst.vin_number.iloc[i]),
                                                    str(cst.model_year.iloc[i])))
            data_dic=transaction.get_dic()
            #output file name
            out_filename='output/csv/' + str(time.time()) + '_' + Path(source_path1).stem + '.json'
            #check if output directory exists, if not make one
            Path('output/csv/').mkdir(parents=True, exist_ok=True)
            #get a json file for each customer in customers.csv
            with open(out_filename, 'w') as f:
                json.dump(data_dic, f, ensure_ascii=False, indent=4)
            #reset transaction parameters to start with next customer
            transaction = Transaction()

#to run script from shell
if __name__=='__main__':
    file_format=sys.argv[1]
    source_path1=sys.argv[2]
    try:
        source_path2=sys.argv[3]
    except:
        source_path2=''
    parser(file_format,source_path1,source_path2)
