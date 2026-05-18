from fastapi import Header
from geopy.geocoders import Nominatim


def location_middleware(
    latitude: str | None = Header(None), longitude: str | None = Header(None)
):
    if not latitude or not longitude:
        return None

    try:
        geolocator = Nominatim(user_agent="kwenda_geolocation_app")
        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        if location and location.raw.get("address"):
            address = location.raw["address"]
            # Return province or state
            province = address.get("state", address.get("province", None))
            print(province)
            return province
    except Exception as e:
        print(f"Error resolving location: {e}")
        return None

    return None
