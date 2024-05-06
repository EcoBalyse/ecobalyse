from fastapi import Security, FastAPI, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader, APIKey
import os
import json
import hashlib
import requests

from mongo_queries import *
from redis_queries import *

import pandas as pd
import mlflow

from data_models import Product
from data_models import ClothingItemInput

API_KEY = os.environ.get('API_KEY')
API_KEY_NAME = os.environ.get('API_KEY_NAME')

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

api = FastAPI(
    title="Ecobalyse API",
    description="Ecobalyse: red thread project as part of the data engineer training course.",
    version="1.0.0")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validate API key provided in the request header.
    Raise an HTTPException with status code 403 if the API key is not valid.
    """
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

@api.get('/', name="Check health API")
def check_api():
    """
    Check if the API is working.
    Return a message if the API is working.
    """
    return {'message': 'API is working'}

@api.get('/cache/clear', name="Clear Redis cache")
def check_api():
    """
    Clear the Redis cache.
    Raise an HTTPException with status code 404 if there is an error clearing the cache.
    """
    try:
        clear_cache()
    except:
        raise HTTPException(status_code=404, detail="Error clear cache")

    return {'message': 'Redis cache cleared'}

@api.get("/product", name="Get Product ID list")
def get_product(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get the list of product IDs.
    """
    return get_product_id()

@api.get("/product/{id}", name="Get Product")
def get_product(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    Get the details of a product by its ID.
    Raise an HTTPException with status code 404 if the product is not found.
    """
    results = get_product_list(id, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/good_product", name="Get Product")
def get_product_good(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    Get the details of a 'good' product by its ID.
    Raise an HTTPException with status code 404 if the product is not found.
    """
    results = get_avg_product_list(id, 1, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/bad_product", name="Get Product")
def get_product_bad(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    Get the details of a 'bad' product by its ID.
    Raise an HTTPException with status code 404 if the product is not found.
    """
    results = get_avg_product_list(id, -1, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/{country}", name="Get Product for country")
def get_product_country(id: str, country: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    Get the details of a product by its ID and country.
    Raise an HTTPException with status code 404 if the product is not found.
    """
    results = get_product_list_country(id, country, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.post('/product', name="Add new product")
def create_product(product: Product, api_key_header: APIKey = Depends(get_api_key)):
    """
    Create a new product.
    Calculate the MD5 hash of the product data structure.
    Check if the product already exists in the MongoDB database.
    Send a POST request to the Ecobalyse government API to create the product.
    Add the product to the MongoDB database.
    Raise an HTTPException with status code 400 if there is an error.
    """
    # Calculation of the MD5 hash of the data structure
    md5_id = None
    try:
        json_str = json.dumps(product.dict(), sort_keys=True)
        md5_id = hashlib.md5(json_str.encode()).hexdigest()
    except:
        HTTPException(status_code=400, detail='The string does not contain a valid JSON.')

    if not md5_id:
        HTTPException(status_code=400, detail='Error in md5 id calculation.')

    if search_product_md5_id_mongo(md5_id) <= 0:
        headers = {
                    'accept': 'application/json',
                    'content-type': 'application/json'
                }

        response = None

        try:
            response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator/detailed', headers=headers, json=product.dict())
        except Exception as e:
            HTTPException(status_code=400, detail=f'Failed contact ecobalyse gouv api : {e}')
        else:
            if response.status_code == 200:
                # Add "md5_id" field to JSON response
                response_json = response.json()
                response_json['md5_id'] = md5_id

                # Add "product_id" field to JSON response
                product_id = response_json.get("inputs", {}).get("product", {}).get("id")        
                response_json["product_id"] = product_id

                if insert_product_mongo(response_json) == True:
                    return {'message': f'Product added {md5_id}'}

            return {'message': 'Not possible'}
    else:
        return {'message': 'Product already exist'}

@api.delete('/product', name="Delete product")
def delete_product(md5_id: str, api_key_header: APIKey = Depends(get_api_key)):
    """
    Delete a product by its MD5 ID.
    Raise an HTTPException with status code 404 if the product is not found.
    """
    delete_result = delete_product_mongo(md5_id)

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}

@api.get("/stats/countries")
def get_countries_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get statistics related to countries.
    Raise an HTTPException with status code 404 if the document is not found.
    """
    results = get_stats_countries()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/days_of_wear")
def get_days_of_wear_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get statistics related to days of wear.
    Raise an HTTPException with status code 404 if the document is not found.
    """
    results = get_stats_days_of_wear()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/impacts")
def get_impacts_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get statistics related to impacts.
    Raise an HTTPException with status code 404 if the document is not found.
    """
    results = get_stats_impacts()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/outliers")
def get_outliers_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get statistics related to outliers.
    Raise an HTTPException with status code 404 if the document is not found.
    """
    results = get_stats_outliers()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/ranking")
def get_ranking_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    Get statistics related to ranking.
    Raise an HTTPException with status code 404 if the document is not found.
    """
    results = get_stats_ranking()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.post("/predict")
async def predict_impact(input: ClothingItemInput, api_key_header: APIKey = Depends(get_api_key)):
    """
    Return prediction impact (load MLFlow model)
    Raise an HTTPException with status code 404 if the model is not found.
    """
    try:
        mlflow.set_tracking_uri("http://mlflow:5000/")

        MODEL_NAME = "ecobalyse_model"
        MODEL_VERSION = "production"
        MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_VERSION}"
        MODEL = mlflow.sklearn.load_model(MODEL_URI)
    except:
        raise HTTPException(status_code=404, detail="MLFlow Models error")

    df = pd.json_normalize(input.__dict__)

    pred = MODEL.predict(df)

    return {"prediction_impact": pred[0]}