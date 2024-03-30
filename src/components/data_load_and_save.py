import pandas as pd
import os
import sys
import argparse
from pathlib import Path

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

#custom class
#from src.get_data import read_params
from src.logger.logging import logging
from src.exception.exception import customexception
from src.utils.utils import read_params , save_csv


def load_and_save(config_path):
    config = read_params(config_path)
    data_path = config["astra_db_cred"]["raw_data_path"]
    raw_data_path = config["load_data"]["raw_dataset_csv"]

    logging.info("data load and save started")
    try:
        logging.info(" reading a df from source path")
        df = pd.read_csv(data_path, sep=",", encoding='utf-8')

        new_cols = [col.replace("-", "_") for col in df.columns]
        save_csv(file_path=raw_data_path,sep=",", index=False, header=new_cols,df_obj=df)
        # df.to_csv(raw_data_path, sep=",", index=False, header=new_cols)  
        logging.info(" Successfully saved the raw dataset in artifact folder")
        logging.info("Data load and save phase ended successfully ... ")
        
        return df

    except Exception as e:
        logging.info(f"Exception occurred in data load and save phase -> ({e})")
        raise customexception(e,sys)

if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    data = load_and_save(config_path=parsed_args.config)