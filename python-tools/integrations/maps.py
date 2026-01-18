import requests
import os


def geocode_nominatim(q: str):
    """Query OpenStreetMap Nominatim (public) for geocoding."""
    url = os.environ.get('NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search')
    params = {'q': q, 'format': 'json', 'limit': 1}
    resp = requests.get(url, params=params, headers={'User-Agent': 'verity-maps/1.0'}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


def osm_tile_url(z: int, x: int, y: int):
    """Return a URL for OSM tile (no API key required for standard tile usage; respect tile usage policy)."""
    server = os.environ.get('OSM_TILE_SERVER', 'https://tile.openstreetmap.org')
    return f"{server}/{z}/{x}/{y}.png"
