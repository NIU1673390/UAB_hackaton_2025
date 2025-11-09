import json, os
from pyproj import Transformer

hospitals_path = "static/data/hospitals.json"
educacio_path = "static/data/educacio.json"
output_path = "static/data/serveis.geojson"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

transformer = Transformer.from_crs("EPSG:25831", "EPSG:4326", always_xy=True)

def extract_features(data, category_name):
    features = []
    for item in data:
        name = item.get("name")
        addresses = item.get("addresses", [])
        found = False
        for addr in addresses:
            loc = addr.get("location")
            if not loc:
                continue
            geoms = loc.get("geometries") or []
            for g in geoms:
                if g.get("type") == "Point":
                    coords = g.get("coordinates")
                    if not coords or len(coords) < 2:
                        continue
                    x, y = coords[0], coords[1]
                    # Si parecen coordenadas en metros (UTM)
                    if abs(x) > 10000 and abs(y) > 10000:
                        lon, lat = transformer.transform(x, y)
                    else:
                        lon, lat = x, y
                    features.append({
                        "type": "Feature",
                        "properties": {"name": name, "category": category_name},
                        "geometry": {"type": "Point", "coordinates": [lon, lat]}
                    })
                    found = True
                    break
            if found:
                break
        if not found:
            print(f"⚠️ No se encontró Point para: {name}")
    return features

features = []
if os.path.exists(hospitals_path):
    hospitals = load_json(hospitals_path)
    features += extract_features(hospitals, "hospital")
else:
    print(f"⚠️ Falta: {hospitals_path}")

if os.path.exists(educacio_path):
    educacio = load_json(educacio_path)
    features += extract_features(educacio, "educacio")
else:
    print(f"⚠️ Falta: {educacio_path}")

geojson_output = {"type":"FeatureCollection", "features": features}
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geojson_output, f, indent=2, ensure_ascii=False)

print(f"✅ Generado: {output_path} con {len(features)} features")
