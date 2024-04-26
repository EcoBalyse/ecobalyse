from fastapi import Security, FastAPI, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import hashlib
import requests

from mongo_queries import *
from redis_queries import *

API_KEY = os.environ.get('API_KEY')
API_KEY_NAME = os.environ.get('API_KEY_NAME')

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

api = FastAPI(
    title="Ecobalyse API",
    description="Ecobalyse: red thread project as part of the data engineer training course.",
    version="1.0.0")

# Définir le modèle de données pour les questions
class Material(BaseModel):
    id: str
    share: float
    country: Optional[str] = None

class Product(BaseModel):
    mass: float
    materials: List[Material]
    product: str
    countrySpinning: str
    countryFabric: str
    countryDyeing: str
    countryMaking: str
    fabricProcess: str

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )

# Route pour vérifier que l'API est fonctionnelle
@api.get('/', name="Check health API")
def check_api():
    """Check health API
    """
    return {'message': 'API is working'}

@api.get('/cache/clear', name="Clear Redis cache")
def check_api():
    """Clear Redis cache
    """
    try:
        clear_cache()
    except:
        raise HTTPException(status_code=404, detail="Error clear cache")

    return {'message': 'Redis cache cleared'}

@api.get("/product", name="Get Product ID list")
def get_product(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    return get_product_id()

@api.get("/product/{id}", name="Get Product")
def get_product(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_product_list(id, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/good_product", name="Get Product")
def get_product_good(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_avg_product_list(id, 1, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/bad_product", name="Get Product")
def get_product_bad(id: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_avg_product_list(id, -1, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@api.get("/product/{id}/{country}", name="Get Product for country")
def get_product_country(id: str, country: str, nb_doc: int = 5, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_product_list_country(id, country, nb_doc)
    
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")

# Route pour créer un nouveau produit
@api.post('/product', name="Add new product")
def create_product(product: Product, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """

    # Calcul du hash MD5 de la structure de données
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
                # Ajout du champ "md5_id" à la réponse JSON
                response_json = response.json()
                response_json['md5_id'] = md5_id

                product_id = response_json.get("inputs", {}).get("product", {}).get("id")        
                response_json["product_id"] = product_id

                if insert_product_mongo(response_json) == True:
                    return {'message': f'Product added {md5_id}'}

            return {'message': 'Not possible'}
    else:
        return {'message': 'Product already exist'}

# Route pour supprimer un produit
@api.delete('/product', name="Delete product")
def delete_product(md5_id: str, api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """

    delete_result = delete_product_mongo(md5_id)

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}

@api.get("/stats/countries")
def get_countries_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_stats_countries()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/days_of_wear")
def get_days_of_wear_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_stats_days_of_wear()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/impacts")
def get_impacts_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_stats_impacts()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/outliers")
def get_outliers_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_stats_outliers()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")
    
@api.get("/stats/ranking")
def get_ranking_stats(api_key_header: APIKey = Depends(get_api_key)):
    """
    TODO
    """
    results = get_stats_ranking()
   
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Document not found")