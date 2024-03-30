import pandas as pd
import sys
import argparse
import joblib
from sklearn.preprocessing import OrdinalEncoder
from sklearn.feature_selection import mutual_info_classif,SelectPercentile


#parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.insert(0, parent_dir)

# custom class
from src.logger.logging import logging
from src.exception.exception import customexception
from src.utils.utils import save_object , read_params , save_csv


def get_data_transformation(config_path):
    
    try:
        logging.info('Data Transformation phase started')
        
        config = read_params(config_path)
        raw_data_path = config["load_data"]["raw_dataset_csv"]
        preprocessed_data_store_path = config["split_data"]["preprocessed_data_path"]
        ord_enc_path = config["ord_encoder_path"]
        TARGET_COL = config["base"]["target_col"]
        featuer_selector_path = config['Feature_selector_path']
        df = pd.read_csv(raw_data_path, sep=",")

        ## Missing values handle
        if len(df.columns[df.isna().any()])>0:
            for i in df.columns[df.isna().any()]:
                df[i].fillna(df[i].mode().loc[0],inplace=True)

        ## encoding Categorical columns 
        enc = OrdinalEncoder()
        df_ord = pd.DataFrame(enc.fit_transform(df),columns=df.columns) 
        logging.info('Successfully encoded categorical data fields')

        selector = SelectPercentile(mutual_info_classif, percentile=80)  # Adjust percentile as needed
        selector.fit_transform(df_ord.drop(TARGET_COL, axis=1), df_ord[TARGET_COL])
        selected_features = df_ord.columns[1:][selector.get_support()]
        df_sel = pd.concat([df_ord[selected_features],df_ord[TARGET_COL]],axis=1)
        logging.info('Data Transformation ended')

        save_object(ord_enc_path,enc)
        save_object(featuer_selector_path,selector)
        logging.info('Ordinal encoder and feature Selector object saved successfully')

        # joblib.dump(enc,ord_enc_path)
        # df_sel.to_csv(preprocessed_data_store_path, sep=",", index=False, header=df_sel.columns)
        save_csv(file_path=preprocessed_data_store_path,sep=",", index=False, header=df_sel.columns,df_obj=df_sel)
        logging.info('Transformed Data Stored successfully')
        logging.info("Data transformation phase ended successfully ... ")

    except Exception as e:
        logging.info(f"Exception occured in the data transformation phase -> ({e})")
        raise customexception(e,sys)
            
    
if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    get_data_transformation(config_path=parsed_args.config)
