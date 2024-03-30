import os
import sys
import pandas as pd
import json
import argparse
from astrapy.ops import AstraDBOps
from astrapy.db import AstraDB,AstraDBCollection
import time
from datetime import datetime

# custom module import
from src.logger.logging import logging
from src.exception.exception import customexception
from src.utils.utils import save_csv, read_params


class cassandra_operation:
    def __init__(self,token):
         try:  
            # AstraCS:doLWOnBYpANgEvMJbCNNzmhj:28885e470a8b7be5b71dda095813d532fb632ebbadd2a5f516d923923a976b43
            self.client=AstraDBOps(token)
            self.token = token
            logging.info("Astra DB client established...")
            self.db = None
            self.arc_db = None
         except Exception as e: 
            raise customexception(e,sys)
    
    def exist_db(self,db_name):
        try:
            for i in self.client.get_databases():
                if i['info']['name']==db_name:
                    return True
            else:
                return False
        except Exception as e:
            raise customexception(e,sys)
         
    def connect_to_database(self,database_name="Main_db"):
            try:
                if self.exist_db(database_name):
                    logging.info(f"Connecting to database {database_name}...")
                    for i in self.client.get_databases():
                        #  print(i['info']['name'],i['id'])
                        if i['info']['name']==database_name:
                            api_endpoint = i['dataEndpointUrl'][:-9]
                            db = AstraDB(token=self.token,api_endpoint=api_endpoint)
                            logging.info(f"Database Connection  Successful ({database_name})... ")
                            return db
                else:  
                    logging.info(f"Connecting to database {database_name} Failed as Database does not exist...")
                    raise Exception(f'Database "{database_name}" does not exist, First create it and then access it using this function')
            except Exception as e:
                logging.info(f"Connecting database {database_name} unsuccessful ",e)
                raise customexception(e,sys)
    
    def pull_latest_data(self,database_name="Main_db",raw_data_path=None,passwd=None):
            try:
                db_con = self.connect_to_database(database_name=database_name)
                list_of_docs = []
                if len(db_con.get_collections()["status"]["collections"])==0:
                    logging.info(f"No Data for pulling in {database_name} DB")
                    return
                for collection in db_con.get_collections()["status"]["collections"]:
                    col_obj = db_con.collection(collection)
                    generator = col_obj.paginated_find(filter={},options={})
                    for doc in generator:
                        list_of_docs.append(doc)
                df_retrieved = pd.DataFrame(list_of_docs).drop('_id',axis=1)
                logging.info(f"Latest data pulled from {database_name} successfully...")
                save_csv(file_path=raw_data_path,sep=",",index=False,header=df_retrieved.columns,df_obj=df_retrieved)
                logging.info(f"Latest csv file saved in {raw_data_path} dir...")

                ##create / connect to archived database
                self.arc_db = self.create_database(database_name="Archived",passwd=passwd)
                json_list = []
                # Iterate through each row of the DataFrame
                for index, row in df_retrieved.iterrows():
                    # Create a dictionary for each row
                    row_dict = dict(zip(row.index, row.tolist()))
                    # Append the dictionary to the list
                    json_list.append(row_dict)
                collection_obj = self.create_collection(db_obj=self.arc_db)
                collection_obj.chunked_insert_many(documents=json_list,chunk_size=20,concurrency=20)
                logging.info(f"Inserted Documents into collection of Archived DB Successfully...")
                
                ## Deleting data from Main_db as it is already moved to archived
                for i in db_con.get_collections()["status"]["collections"]:
                    db_con.delete_collection(collection_name=i)

            except Exception as e:
                logging.info("Pull data from astra db failed ",e)
                raise customexception(e,sys)
            
    def create_database(self,database_name="Archived",passwd=None,connect_to_same_database=True):
        if passwd!=None:
            if self.exist_db(database_name):
                logging.info(database_name," DB already existed, so connecting to database...")
                db_obj = self.connect_to_database(database_name=database_name)
                return db_obj

            try:
                logging.info(database_name," DB not found , so creating...")
                database_definition = {
                    "name": database_name,
                    "tier": "serverless",
                    "cloudProvider": "GCP", # GCP, AZURE, or AWS
                    "keyspace": "default_keyspace",
                    "region": "us-east1",
                    "capacityUnits": 1,
                    "user": self.token.split(':')[1],
                    "password": passwd,
                    "dbType": "vector"}
                DB_response = self.client.create_database(database_definition=database_definition)   
                time.sleep(160)
                logging.info(database_name," DB created successfully...")
                if connect_to_same_database==True:
                    arc_db = self.connect_to_database(database_name=database_name)
                    return arc_db

                return DB_response 
            except Exception as e:
                logging.info(f"{database_name} Database creation failed",e)
                raise customexception(e,sys)
        else:
            print("Password Not provided")

              

    def create_collection(self,db_obj,collection_name = "Mushrooms"):
        try:
            timestamp_file = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            new_file_name = f"{collection_name}_{timestamp_file}"
            col_obj = db_obj.create_collection(collection_name=new_file_name)
            # time.sleep(35)
            logging.info(f"{new_file_name} collection created ")
            return col_obj
        except Exception as e:
            logging.info(f"Exception occurred in create_collection ",e)
            raise customexception(e,sys)

if __name__=="__main__":
    
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()

    config = read_params(parsed_args.config)
    data_path = config["astra_db_cred"]["raw_data_path"]
    passwd = config["astra_db_cred"]["passwd"]
    token = config["astra_db_cred"]["token"]
    database_name = config["astra_db_cred"]["database_name"]

    obj = cassandra_operation(token=token)
    obj.pull_latest_data(database_name=database_name,raw_data_path=data_path,passwd=passwd)