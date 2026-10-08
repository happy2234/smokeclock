from src.data.openaq_client import find_delhi_locations


locations = find_delhi_locations()

print("Delhi PM2.5 locations found:", len(locations))
print()

if not locations.empty:
    print(
        locations[
            [
                "id",
                "name",
                "locality",
                "country",
                "latitude",
                "longitude",
            ]
        ].to_string(index=False)
    )
