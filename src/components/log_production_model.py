import argparse
import mlflow
import sys
from mlflow.tracking import MlflowClient
from pprint import pprint

#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

# custom class  
from src.logger.logging import logging
#from src.get_data import read_params
from src.exception.exception import customexception
from src.utils.utils import save_object, read_params



def log_production_model(config_path):
    try:
        logging.info("Log production model phase started")
        config = read_params(config_path)
        mlflow_config = config["mlflow_config"] 
        model_name = mlflow_config["registered_model_name"]
        remote_server_uri = mlflow_config["remote_server_uri"]

        mlflow.set_tracking_uri(remote_server_uri)
        
        logging.info('MLflow searching runs started ... ')
        all_experiments = [exp.experiment_id for exp in mlflow.list_experiments()]
#        all_experiments = [exp.experiment_id for exp in MlflowClient().list_experiments()]
        runs = mlflow.search_runs(experiment_ids=all_experiments)
#        print(type(runs),"\n",runs)
#        runs = mlflow.search_runs(experiment_ids='2')
        lowest = runs["metrics.f1_score_"].sort_values(ascending=False)[0]
        lowest_run_id = runs[runs["metrics.f1_score_"] == lowest]["run_id"][0]
        
        logging.info('MLflow Segregating model started ... ')
        client = MlflowClient()

        for mv in client.search_model_versions(f"name='{model_name}'"):
            mv = dict(mv)
            
            if mv["run_id"] == lowest_run_id:
                current_version = mv["version"]
                logged_model = mv["source"]
                pprint(mv, indent=4)
                client.transition_model_version_stage(
                    name=model_name,
                    version=current_version,
                    stage="Production"
                )
            else:
                current_version = mv["version"]
                client.transition_model_version_stage(
                    name=model_name,
                    version=current_version,
                    stage="Staging"
                )        


        loaded_model = mlflow.pyfunc.load_model(logged_model)
        
        model_path = config["webapp_model_dir"] #"prediction_service/model"

        # joblib.dump(loaded_model, model_path)
        save_object(file_path=model_path, obj=loaded_model)
        logging.info('Best Model saved for prediction use ... ')
        logging.info('Log production model phase ended successfully  ..')
        
    except Exception as e:
        logging.info(f"Exception occured in the log production model build phase -> ({e})")
        raise customexception(e,sys)        



if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    log_production_model(config_path=parsed_args.config)

