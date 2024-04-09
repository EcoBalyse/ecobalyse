from fastapi import Security, FastAPI, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os

from mongo_queries import *
from redis_queries import *

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_NAME = os.getenv('API_KEY_NAME')

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

api = FastAPI(
    title="Ecobalyse API",
    description="Ecobalyse: red thread project as part of the data engineer training course.",
    version="1.0.0")

# Définir le modèle de données pour les questions
class Material(BaseModel):
    id: str
    share: float
    country: str

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
    global mongo_uri

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    response = None

    try:
        response = requests.post('https://ecobalyse.beta.gouv.fr/api/textile/simulator/detailed', headers=headers, json=product.dict())
    except:
        HTTPException(status_code=400, detail='Failed contact ecobalyse gouv api')

    if response and response.status_code == 200:
        try:
            # Create a new client and connect to the server
            client = MongoClient(mongo_uri)

            # Ecobalyse database
            ecobalyse = client["ecobalyse"]

            result = ecobalyse["impacts"].insert_one(product.dict())

            return {'message': f'Product added {str(result.inserted_id)}'}
        except PyMongoError as e:
            HTTPException(status_code=400, detail=f'Mongodb atlas error: {str(e)}')
        finally:
            client.close()  # Ensure proper connection closure

    return {'message': 'Not possible'}