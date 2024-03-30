# split the raw data 
# save it in data/processed folder
import os
import argparse
import pandas as pd
import sys
from sklearn.model_selection import train_test_split

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

# custom class
from src.logger.logging import logging
from src.exception.exception import customexception
from src.utils.utils import read_params,save_csv

def split_and_saved_data(config_path):
    try:
        config = read_params(config_path)
        test_data_path = config["split_data"]["test_path"] 
        train_data_path = config["split_data"]["train_path"]
        preprocessed_data_path = config["split_data"]["preprocessed_data_path"]
        split_ratio = config["split_data"]["test_size"]
        random_state = config["base"]["random_state"]

        df = pd.read_csv(preprocessed_data_path, sep=",")
        logging.info("Train test split of preprocessed data phase started ... ")
        train, test = train_test_split(
            df, 
            test_size=split_ratio, 
            random_state=random_state
            )
        save_csv(file_path=train_data_path,sep=",", index=False, header=train.columns,df_obj=train)
        save_csv(file_path=test_data_path,sep=",", index=False, header=test.columns,df_obj=test)
        #train.to_csv(train_data_path, sep=",", index=False, encoding="utf-8")
        #test.to_csv(test_data_path, sep=",", index=False, encoding="utf-8")
        logging.info("Train test split phase ended successfully ...")
        
    except Exception as e:
        logging.info(f"Exception occured in the train test split data phase -> ({e})")
        raise customexception(e,sys)
    

if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    split_and_saved_data(config_path=parsed_args.config)

