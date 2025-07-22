import httpx
import asyncio
import os
from math import radians, cos, sin, asin, sqrt

from config import settings

POSTCODES_IO_URL = "https://api.postcodes.io/postcodes/"

async def get_lat_lon_postcodes_io(postcode: str):
    async with httpx.AsyncClient() as client:
        url = f"{POSTCODES_IO_URL}{postcode.replace(' ', '')}"
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json()
            if data["status"] == 200 and data["result"]:
                return data["result"]["latitude"], data["result"]["longitude"]
    return None, None

async def get_lat_lon_google(postcode: str):
    async with httpx.AsyncClient() as client:
        params = {
            "address": postcode,
            "key": settings.GOOGLE_API_KEY
        }
        r = await client.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
        if r.status_code == 200:
            results = r.json().get("results")
            if results:
                location = results[0]["geometry"]["location"]
                return location["lat"], location["lng"]
    return None, None

async def get_lat_lon(postcode: str):
    lat, lon = await get_lat_lon_postcodes_io(postcode)
    if lat is not None and lon is not None:
        return lat, lon
    return await get_lat_lon_google(postcode)

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000 # Radius of earth in meters
    return c * r
