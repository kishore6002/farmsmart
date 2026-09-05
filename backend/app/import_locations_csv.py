from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "id",
    "state",
    "district",
    "mandal",
    "name",
    "latitude",
    "longitude",
    "soil_type",
    "major_crops",
}


def import_locations(csv_path: Path, output_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

        rows = []
        for row in reader:
            rows.append(
                {
                    "id": row["id"].strip(),
                    "state": row["state"].strip(),
                    "district": row["district"].strip(),
                    "mandal": row["mandal"].strip(),
                    "name": row["name"].strip(),
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "soil_type": row["soil_type"].strip(),
                    "major_crops": [crop.strip() for crop in row["major_crops"].split("|") if crop.strip()],
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return len(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m app.import_locations_csv <locations.csv> <locations.json>")

    count = import_locations(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Imported {count} locations")
