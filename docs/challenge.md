# Part I comments and approach


### Selecting the model

After reading the "exploration.ipynb" notebook, and cheking that there is no difference in performance when using either model, I decided to use the __Logistic Regression__ model, with __Feature Importance, and Balance__ because it is less resource demanding, and requires less hyper parameter tuning than XGBoost.


### Global approach for the app

I will use a trained model which I will save in a new folder named "ml_models". This model will be the one that will do the predictions when they are requested. This model was savedm and will be loeaded using two new methods I created in the __Delay_Model__ class.

In the __api.py__ file, I modified the __post__ method to raise exceptions if no data is passed, or if an unknown column is passed to the model for predictions.