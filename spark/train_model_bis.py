import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor

from sklearn.metrics import r2_score, mean_squared_error

from sklearn.model_selection import train_test_split

from sklearn import set_config

import mlflow


mlflow.set_tracking_uri(uri="http://mlflow:5000")
mlflow.set_experiment(experiment_name="ecobalyse_dst")

set_config(transform_output="pandas")

lst_header = [
    "ImpactScore", "ProductId", "MaterialId_1", "MaterialId_2", "MaterialId_1_share", "MaterialId_2_share",
    "CountryDyeingCode", "CountryFabricCode", "CountryMakingCode", "FabricProcess", "Mass", "AirTransportRatio",
]

str_label = "ImpactScore"
df = pd.read_csv("ecobalyse_data.csv", header=None, names=lst_header)
X_train, X_test, y_train, y_test = train_test_split(df.drop(columns=[str_label]), df[[str_label]], random_state=42)

# X_train.iloc[0].to_json('test.json')
# X_test.iloc[0].to_json('test2.json')
# X_test.iloc[1].to_json('test3.json')
# X_test.iloc[2].to_json('test4.json')

lst_cat = X_train.select_dtypes(include="object").columns
lst_num = X_train.select_dtypes(include="number").columns

cat_pipe = Pipeline(
    steps=[
        ("cat_imputer", SimpleImputer(strategy="most_frequent", fill_value="missing")),
        ("cat_encoding", OneHotEncoder(drop="first", handle_unknown="ignore", min_frequency=0.05, max_categories=10, sparse_output=False)),
    ]
)

num_pipe = Pipeline(
    steps=[
        ("num_imputer", SimpleImputer(strategy="median")),
        ("num_scaling", RobustScaler())
    ]
)

preprocess = ColumnTransformer(
    transformers=[
        ("cat_preprocessor", cat_pipe, lst_cat),
        ("num_preprocessor", num_pipe, lst_num),
    ],
    remainder="drop"
)

ml_pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocess),
        ("modeling", RandomForestRegressor())
    ]
)

ml_dummy = Pipeline(
    steps=[
        ("preprocessing", preprocess),
        ("modeling", DummyRegressor())
    ]
)

mlflow.autolog()

with mlflow.start_run(run_name="Ecobalyse Modèle de référence"):
    ml_dummy.fit(X_train, y_train)

    preds_dummy = ml_dummy.predict(X_test)

    rmse_dummy = mean_squared_error(y_true=y_test, y_pred=preds_dummy, squared=False)
    r2_dummy = r2_score(y_true=y_test, y_pred=preds_dummy)

    print(f"RMSE de reference {rmse_dummy:.02f}")
    print(f"R2 de reference {r2_dummy:.02f}")


with mlflow.start_run(run_name="Ecobalyse Modèle Random Forest"):
    ml_pipeline.fit(X_train, y_train)

    preds = ml_pipeline.predict(X_test)

    rmse = mean_squared_error(y_true=y_test, y_pred=preds, squared=False)
    r2 = r2_score(y_true=y_test, y_pred=preds)

    print(f"RMSE du modèle {rmse:.02f}")
    print(f"R2 du modèle {r2:.02f}")
