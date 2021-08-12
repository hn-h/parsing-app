class Transaction():
    """
    This class represents the main transaction tag/entry
    """
    def __init__(self):
      self.file_name=''
      self.date=''
      self.customer=Customer()
      self.vehicles=[]

    def get_dic(self):
      """
      Returns the transaction data in a python dictionary
      """
      transaction_dic={'file_name':self.file_name,
                       'transaction':{
                                    'date':self.date,
                                    'customer':self.customer.get_dic(),
                                    'vehicles':[vehicle.get_dic() for vehicle in self.vehicles]
                                    }
                        }

      return transaction_dic

class Customer():
    """
    This class represents the customer tag/info in the data
    """
    def __init__(self):
        self.id=''
        self.name=''
        self.address=''
        self.phone=''

    def get_dic(self):
        """
        Returns the customer data in a python dictionary
        """
        customer_dic={'id':self.id,
                      'name':self.name,
                      'address':self.address,
                      'phone':self.phone}

        return customer_dic


class Vehicle():
    """
    This class represents the vehicle tag/info in the data
    """
    def __init__(self,id='',make='',vin_number='',model_year=''):
        self.id=id
        self.make=make
        self.vin_number=vin_number
        self.model_year=model_year

    def get_dic(self):
        """
        Returns the vehicle data in a python dictionary
        """
        vehicle_dic={'id':self.id,
                      'make':self.make,
                      'vin_number':self.vin_number,
                      'model_year':self.model_year}

        return vehicle_dic
