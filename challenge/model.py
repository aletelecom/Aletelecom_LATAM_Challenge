import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import pickle

from sklearn.linear_model import LogisticRegression

from typing import Tuple, Union, List

# This block of code creates a variable "complete_features"
# That allows me to get all the original columns. This will
# help me rule out any unknown that could be passed to the model
BASE_DIR = Path(__file__).resolve(strict=True).parent
data_path = BASE_DIR.joinpath('..', 'data', 'data.csv')
data = pd.read_csv(data_path)
complete_features = pd.concat([
                pd.get_dummies(data['OPERA'], prefix='OPERA'),
                pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'), 
                pd.get_dummies(data['MES'], prefix='MES')],
                axis=1
            ).columns.tolist()

class DelayModel:

    def __init__(
        self,
        model = LogisticRegression(),
        all_features = complete_features
    ):
        self._model = model
        self._target_col = None
        self.all_features = all_features
        

    def preprocess(
            self,
            data: pd.DataFrame,
            target_column: str = None
        ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        
        # These blocks of code mainly follow the "exploration.ipynb" notebook to
        # preprcess the raw data
        def get_min_diff(row):
            fecha_o = datetime.strptime(row['Fecha-O'], '%Y-%m-%d %H:%M:%S')
            fecha_i = datetime.strptime(row['Fecha-I'], '%Y-%m-%d %H:%M:%S')
            min_diff = ((fecha_o - fecha_i).total_seconds())/60
            return min_diff
        
        self._target_col = target_column
        
        top_10_features = [
            "OPERA_Latin American Wings", 
            "MES_7",
            "MES_10",
            "OPERA_Grupo LATAM",
            "MES_12",
            "TIPOVUELO_I",
            "MES_4",
            "MES_11",
            "OPERA_Sky Airline",
            "OPERA_Copa Air"
        ]
        
        # The first branch of the if statement will output only the features
        # because no target column was passed, this is normally needed when
        # the model will be used for predictions
        if target_column is None:

            features = pd.concat([
                pd.get_dummies(data['OPERA'], prefix='OPERA'),
                pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'), 
                pd.get_dummies(data['MES'], prefix='MES')],
                axis=1
            )

            # This will check if any unknown column is passed, and if so
            # an exception in raised.
            for col in features.columns:
                if col not in self.all_features:
                    raise ValueError(f'Unknown column passed: {col}')

            
            missing_features = set(top_10_features) - set(features.columns)
            if missing_features:
                for col in missing_features:
                    features[col] = 0
            
            return features[top_10_features]
        
        # The second branch of the if statement will output the features
        #  and the target variable, this is normally needed when
        # the model will be trained.
        else:
            data['min_diff'] = data.apply(get_min_diff, axis=1)
            data[target_column] = np.where(data['min_diff'] > 15, 1, 0)
            
            features = pd.concat([
                pd.get_dummies(data['OPERA'], prefix='OPERA'),
                pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'), 
                pd.get_dummies(data['MES'], prefix='MES')],
                axis=1
            )

            for col in features.columns:
                if col not in self.all_features:
                    raise ValueError(f'Unknown column passed: {col}')
            
            return features[top_10_features], data[[target_column]]


    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """

        # Change the model params to take into account the unbalance in the target variable.
        n_y0 = target[target[self._target_col]==0].shape[0]
        n_y1 = target[target[self._target_col]==1].shape[0]
        lr_params = {1: n_y0/target[self._target_col].shape[0], 0: n_y1/target[self._target_col].shape[0]}
        self._model.set_params(class_weight=lr_params)

        self._model.fit(features, target.values.ravel())

        return

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        
        model_y_preds = self._model.predict(features)

        return [int(x) for x in model_y_preds.tolist()]

    
    def save_model(
            self,
            model_name: str
    ) -> None:
        BASE_DIR = Path(__file__).resolve(strict=True).parent
        ML_FOLDER = 'ml_models'
        path_to_save = BASE_DIR.joinpath('..', ML_FOLDER, model_name)
        with open(path_to_save, 'wb') as f:
            pickle.dump(self._model, f)
        
        return
    
    def load_model(
            self,
            model_path: str
    ) -> None:

        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)

        self._model = loaded_model

        return 