# load the train and test
# train algo
# save the metrices, params
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from urllib.parse import urlparse
import argparse
import mlflow

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

# custom class
#from src.get_data import read_params
from src.logger.logging import logging
from src.exception.exception import customexception
from src.utils.utils import read_params


def eval_metrics(actual, pred):
    actual,pred = np.array(actual).flatten(), np.array(pred).flatten()
    f1_score_ = f1_score(actual,pred, average='macro')
    accuracy_score_ = accuracy_score(actual,pred)
    return accuracy_score_,f1_score_

def train_and_evaluate(config_path):
    try:
        
        logging.info("Model train and evaluate phase started")
        config = read_params(config_path)
        test_data_path = config["split_data"]["test_path"]
        train_data_path = config["split_data"]["train_path"]
        random_state = config["base"]["random_state"]
        # model_dir = config["model_dir"]

        # model hyper parameters
        n_estimators = config["estimators"]["Adaboost"]["params"]["n_estimators"]
        learning_rate = config["estimators"]["Adaboost"]["params"]["learning_rate"]
        algorithm = config["estimators"]["Adaboost"]["params"]["algorithm"]

        target = [config["base"]["target_col"]]

        train = pd.read_csv(train_data_path, sep=",")
        test = pd.read_csv(test_data_path, sep=",")

        train_y = train[target]
        test_y = test[target]

        train_x = train.drop(target, axis=1)
        test_x = test.drop(target, axis=1)

        logging.info("Train and test data fetch successfully completed for train and evaluate phase")

    ################### MLFLOW ###############################
        mlflow_config = config["mlflow_config"]
        remote_server_uri = mlflow_config["remote_server_uri"]

#        mlflow.set_tracking_uri(remote_server_uri)
        mlflow.set_tracking_uri("mysql")

        mlflow.set_experiment(mlflow_config["experiment_name"])

        logging.info("MLflow experiment run started.. ")
        with mlflow.start_run(run_name=mlflow_config["run_name"]) as mlops_run:
            lr = AdaBoostClassifier(
                n_estimators=n_estimators, 
                learning_rate=learning_rate,
                algorithm=algorithm, 
                random_state=random_state)
            lr.fit(train_x, train_y)

            predicted_qualities = lr.predict(test_x)
            
            (accuracy_score_,f1_score_) = eval_metrics(test_y, predicted_qualities)


    # Log params into mlflow platform
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("learning_rate", learning_rate)
            mlflow.log_param("algorithm", algorithm)

    # log metrics value as per experiment for comparison  for mlflow
            mlflow.log_metric("accuracy_score_", accuracy_score_)
            mlflow.log_metric("f1_score_", f1_score_)
            mlflow.sklearn.log_model(lr, "model")
            tracking_url_type_store = urlparse(mlflow.get_artifact_uri()).scheme

            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(lr, "model",registered_model_name=mlflow_config["registered_model_name"])
            else:
                mlflow.sklearn.log_model(lr, "model")

        logging.info("MLflow experiment Successfully completed .. ")
        logging.info("Model train and evaluate phase ended successfully ... ")


    except Exception as e:
        logging.info(f"Exception occured in the train and evaluate model phase -> ({e})")
        raise customexception(e,sys)

if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    train_and_evaluate(config_path=parsed_args.config)
