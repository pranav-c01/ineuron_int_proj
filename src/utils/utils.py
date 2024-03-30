import os
import sys
import pickle
import joblib
import yaml
from datetime import datetime

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

from src.logger.logging import logging
from src.exception.exception import customexception

import shutil

def read_params(config_path):
    try:
        with open(config_path) as yaml_file:
            config = yaml.safe_load(yaml_file)
        return config
    except Exception as e:
        logging.info('Exception Occured in reading params util method')
        raise customexception(e, sys)

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path, exist_ok=True)

        if os.path.exists(file_path):
                os.remove(file_path)

        joblib.dump(obj,file_path)

        # saving copy in archived folder
        archived_folder_path = os.path.join(dir_path,"Archived")
        os.makedirs(archived_folder_path, exist_ok=True)
        timestamp_file = datetime.now().strftime("%Y_%m_%d_%H")

        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        new_file_name = f"{file_name}_{timestamp_file}{file_extension}"
        archived_file_path = os.path.join(archived_folder_path, new_file_name)
        shutil.copyfile(file_path, archived_file_path)

    except Exception as e:
        logging.info('Exception Occured in saving object function utils')
        raise customexception(e, sys)
    
def save_csv(file_path,sep=",",index=False,header=None,df_obj=None):
    try:
        if True:
            dir_path = os.path.dirname(file_path)

            os.makedirs(dir_path, exist_ok=True)

            if os.path.exists(file_path):
                os.remove(file_path)

            df_obj.to_csv(file_path, sep=sep, index=index, header=header)

            # saving copy in archived folder
            archived_folder_path = os.path.join(dir_path,"Archived")
            os.makedirs(archived_folder_path, exist_ok=True)
            timestamp_file = datetime.now().strftime("%Y_%m_%d_%H")

            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            new_file_name = f"{file_name}_{timestamp_file}{file_extension}"
            archived_file_path = os.path.join(archived_folder_path, new_file_name)
            shutil.copyfile(file_path, archived_file_path)
        else:
            logging.info('Cannot save csv file as either header or df_obj is None')
            raise Exception("Header and df_obj Should be not None ")
    except Exception as e:
        logging.info('Exception Occured in saving csv file function utils')
        raise customexception(e, sys)
    
def evaluate_model(X_train,y_train,X_test,y_test,models):
    try:
        report = {}
        for i in range(len(models)):
            model = list(models.values())[i]
            # Train model
            model.fit(X_train,y_train)

            

            # Predict Testing data
            y_test_pred =model.predict(X_test)

            # Get R2 scores for train and test data
            #train_model_score = r2_score(ytrain,y_train_pred)
            test_model_score = r2_score(y_test,y_test_pred)

            report[list(models.keys())[i]] =  test_model_score

        return report

    except Exception as e:
        logging.info('Exception occured during model training')
        raise customexception(e,sys)
    
def load_object(file_path):
    try:
        with open(file_path,'rb') as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        logging.info('Exception Occured in load_object function utils')
        raise customexception(e,sys)

    