#!/usr/bin/env python3
"""Prepare ARAP WeatherDaily JSONL from historique-meteo.net CSV exports.

Expected input filenames, for each available year (e.g. 2024, 2025, 2026):
  historique-meteo-durbuy-YYYY.csv
  historique-meteo-eupen-parc-naturel-hautes-fagnes-eifel-YYYY.csv
  historique-meteo-houffalize-YYYY.csv
  historique-meteo-malmedy-YYYY.csv
  historique-meteo-seraing-YYYY.csv
  historique-meteo-verviers-YYYY.csv

The script preserves the source column names and real values. It does not
impute, simulate, or derive meteorological measurements.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

SOURCE_URL = "https://www.historique-meteo.net"
STATIONS = {
    "durbuy": {
        "station_id": "AM_DURBUY",
        "station_name": "Durbuy",
        "filename_stem": "historique-meteo-durbuy",
    },
    "eupen-parc-naturel-hautes-fagnes-eifel": {
        "station_id": "AM_EUPEN",
        "station_name": "Eupen Parc Naturel Hautes Fagnes Eifel",
        "filename_stem": "historique-meteo-eupen-parc-naturel-hautes-fagnes-eifel",
    },
    "houffalize": {
        "station_id": "AM_HOUFFALIZE",
        "station_name": "Houffalize",
        "filename_stem": "historique-meteo-houffalize",
    },
    "malmedy": {
        "station_id": "AM_MALMEDY",
        "station_name": "Malmedy",
        "filename_stem": "historique-meteo-malmedy",
    },
    "seraing": {
        "station_id": "AM_SERAING",
        "station_name": "Seraing",
        "filename_stem": "historique-meteo-seraing",
    },
    "verviers": {
        "station_id": "AM_VERVIERS",
        "station_name": "Verviers",
        "filename_stem": "historique-meteo-verviers",
    },
}

HEADER_LOCATION_RE = re.compile(
    r'EXPORT\s+DONN[ÉE]ES\s+M[ÉE]T[ÉE]O\s+POUR\s+"(?P<name>.+?)"\s*'
    r'\(LAT/LON\s*:\s*(?P<lat>-?\d+(?:\.\d+)?)\s*/\s*(?P<lon>-?\d+(?:\.\d+)?)\)',
    re.IGNORECASE,
)


def parse_scalar(value: str) -> Any:
    """Convert numeric CSV cells to numbers; preserve empty and text cells."""
    value = value.strip()
    if value == "":
        return None
    # Integers first; retain codes like 001 as strings if leading zeros exist.
    if re.fullmatch(r"-?(?:0|[1-9]\d*)", value):
        try:
            return int(value)
        except ValueError:
            pass
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?", value):
        try:
            return float(value)
        except ValueError:
            pass
    return value


def read_header_metadata(path: Path) -> tuple[str | None, float | None, float | None, list[str]]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for _ in range(10):
            line = f.readline()
            if not line:
                break
            lines.append(line.rstrip("\r\n"))
            if line.strip() and not line.lstrip().startswith("#"):
                break
    for line in lines:
        match = HEADER_LOCATION_RE.search(line)
        if match:
            return match.group("name"), float(match.group("lat")), float(match.group("lon")), lines
    return None, None, None, lines


def infer_station(path: Path) -> dict[str, str] | None:
    name = path.name.lower()
    for item in STATIONS.values():
        if name.startswith(item["filename_stem"] + "-") and name.endswith(".csv"):
            return item
    return None


def process_file(path: Path, schema: list[str] | None, seen: set[tuple[str, str]]) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    station = infer_station(path)
    if station is None:
        raise ValueError(f"No se reconoce la ubicación a partir del nombre: {path.name}")

    year_match = re.search(r"-(20\d{2})\.csv$", path.name, re.IGNORECASE)
    filename_year = int(year_match.group(1)) if year_match else None
    header_name, latitude, longitude, header_lines = read_header_metadata(path)
    if latitude is not None and not (-90 <= latitude <= 90):
        raise ValueError(f"Latitud fuera de rango en {path.name}: {latitude}")
    if longitude is not None and not (-180 <= longitude <= 180):
        raise ValueError(f"Longitud fuera de rango en {path.name}: {longitude}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        # Skip descriptive comment lines before the CSV header.
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                raise ValueError(f"No se encontró la cabecera CSV en {path.name}")
            if line.strip() and not line.lstrip().startswith("#"):
                f.seek(pos)
                break
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Cabecera vacía en {path.name}")
        columns = [c.strip().lstrip("\ufeff") for c in reader.fieldnames]
        if "DATE" not in columns:
            raise ValueError(f"No existe la columna DATE en {path.name}; columnas: {columns}")
        if len(columns) != len(set(columns)):
            raise ValueError(f"Hay nombres de columna duplicados en {path.name}")
        if schema is not None and columns != schema:
            missing = sorted(set(schema) - set(columns))
            extra = sorted(set(columns) - set(schema))
            raise ValueError(
                f"Esquema distinto en {path.name}. Columnas ausentes: {missing}; nuevas: {extra}. "
                "No se mezclaron automáticamente."
            )
        schema = schema or columns
        reader.fieldnames = columns
        docs: list[dict[str, Any]] = []
        duplicate_dates = 0
        invalid_dates = 0
        wrong_year = 0
        row_count = 0
        for row_number, row in enumerate(reader, start=1):
            if not row or all(v is None or not str(v).strip() for v in row.values()):
                continue
            row_count += 1
            clean = {str(k).strip().lstrip("\ufeff"): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k is not None}
            raw_date = clean.get("DATE", "")
            try:
                parsed_date = date.fromisoformat(str(raw_date))
            except (TypeError, ValueError):
                invalid_dates += 1
                continue
            if filename_year is not None and parsed_date.year != filename_year:
                wrong_year += 1
            key = (station["station_id"], parsed_date.isoformat())
            if key in seen:
                duplicate_dates += 1
                continue
            seen.add(key)
            measurements = {k: parse_scalar(clean.get(k, "")) for k in columns if k != "DATE"}
            doc = {
                "station_id": station["station_id"],
                "station_name": station["station_name"],
                "source": "historique-meteo.net",
                "source_url": SOURCE_URL,
                "source_file": path.name,
                "observation_date": parsed_date.isoformat(),
                "year": parsed_date.year,
                "location": {
                    "country": "BE",
                    "latitude": latitude,
                    "longitude": longitude,
                    "source_name": header_name,
                },
                "measurements": measurements,
                "source_attribution": "Données provenant de https://www.historique-meteo.net; utilisation libre à condition de mentionner leur provenance.",
            }
            docs.append(doc)

    report = {
        "file": path.name,
        "station_id": station["station_id"],
        "station_name_from_file_header": header_name,
        "filename_year": filename_year,
        "rows_seen": row_count,
        "documents_written": len(docs),
        "invalid_dates_skipped": invalid_dates,
        "duplicate_station_dates_skipped": duplicate_dates,
        "dates_not_matching_filename_year": wrong_year,
        "column_count": len(schema or []),
        "latitude": latitude,
        "longitude": longitude,
        "header_notes": header_lines[:4],
    }
    return docs, schema or [], report


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare CSV weather history for ARAP WeatherDaily as JSONL.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Folder containing the historique-meteo-*.csv files")
    parser.add_argument("--output-dir", type=Path, default=Path("data/mongo/seeds"), help="Output folder (default: data/mongo/seeds)")
    parser.add_argument("--output-name", default="WeatherDaily.jsonl", help="Output JSONL filename")
    parser.add_argument("--manifest-name", default="WeatherDaily_manifest.json", help="Validation report filename")
    args = parser.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    if not input_dir.is_dir():
        print(f"ERROR: input folder does not exist: {input_dir}", file=sys.stderr)
        return 2
    files = sorted(input_dir.glob("historique-meteo-*.csv"))
    if not files:
        print(f"ERROR: no historique-meteo-*.csv files found in {input_dir}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / args.output_name
    manifest_path = args.output_dir / args.manifest_name
    all_reports: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    schema: list[str] | None = None
    total_written = 0
    # Write to a temporary file first, so schema errors don't leave a partial final output.
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        with temp_path.open("w", encoding="utf-8", newline="\n") as out:
            for path in files:
                docs, schema, report = process_file(path, schema, seen)
                for doc in docs:
                    out.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
                all_reports.append(report)
                total_written += len(docs)
                print(f"OK {path.name}: {len(docs)} documents -> {report['station_id']}")
        temp_path.replace(output_path)
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink()
        print(f"ERROR: {exc}", file=sys.stderr)
        print("No se publicó un JSONL final parcial.", file=sys.stderr)
        return 1

    expected_station_ids = sorted({r["station_id"] for r in all_reports})
    manifest = {
        "project": "ARAP - Ardennes Racing Automotive Plan",
        "collection_target": "WeatherDaily",
        "source": "historique-meteo.net",
        "source_url": SOURCE_URL,
        "source_attribution": "Données provenant de https://www.historique-meteo.net; utilisation libre à condition de mentionner leur provenance.",
        "generated_by": Path(__file__).name,
        "output_file": output_path.name,
        "input_directory": str(input_dir),
        "input_file_count": len(files),
        "document_count": total_written,
        "station_ids": expected_station_ids,
        "columns_preserved_under_measurements": schema,
        "measurement_values_simulated_or_imputed": False,
        "files": all_reports,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nFinished.")
    print(f"Files processed: {len(files)}")
    print(f"Documents written: {total_written}")
    print(f"JSONL: {output_path}")
    print(f"Manifest: {manifest_path}")
    print("Note: the source file's weather-code meanings are preserved as numeric codes; they are not decoded by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
