import redis
from mongo_queries import *

redis_client = redis.Redis(
    host="redis",
    port=6379,
    health_check_interval=30,
    # needed to decode redis response to utf-8 because redis returns bytes objects
    charset="utf-8",
    decode_responses=True
)

def get_product_id():
    product_id = redis_client.json().get("product:id")
    if (product_id == None):
        product_id = get_product_id_mongo()
        redis_client.json().set("product:id", '$', product_id)

    return product_id

def get_product_list(product_id: str, nb_doc: int):
    product_list = redis_client.json().get(f"product:list:{product_id}:{nb_doc}")
    if (product_list == None):
        product_list = get_product_list_mongo(product_id, nb_doc)
        redis_client.json().set(f"product:list:{product_id}:{nb_doc}", '$', product_list)

    return product_list

def get_product_list_country(product_id: str, country: str, nb_doc: int):
    product_country = redis_client.json().get(f"product:country:{product_id}:{country}:{nb_doc}")
    if (product_country == None):
        product_country = get_product_list_country_mongo(product_id, country, nb_doc)
        redis_client.json().set(f"product:country:{product_id}:{country}:{nb_doc}", '$', product_country)

    return product_country