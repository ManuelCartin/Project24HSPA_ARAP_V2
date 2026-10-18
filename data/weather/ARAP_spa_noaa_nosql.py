#!/usr/bin/env python3
"""Download real NOAA GHCNh period-of-record observations for Spa-la-Sauveniere, Belgium.

Station: BEI0000EBSP (50.4833, 5.9167, elevation 482 m; SPA/LA SAUVENIERE)
Outputs: raw PSV, row-preserving JSONL for MongoDB, and a manifest.
No synthetic observations are generated.

Usage:
    python waila_spa_noaa_nosql.py
    python waila_spa_noaa_nosql.py --outdir data_spa
    python waila_spa_noaa_nosql.py --timeout 180

Dependencies: Python 3.9+ and requests (pip install requests)
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

STATION = {
    "station_id": "BEI0000EBSP",
    "latitude": 50.4833,
    "longitude": 5.9167,
    "elevation_m": 482.0,
    "station_name": "SPA/LA SAUVENIERE",
    "country_code": "BE",
}
BASE_URL = "https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-station/"
FILENAME = f"GHCNh_{STATION['station_id']}_por.psv"
URL = BASE_URL + FILENAME


def session_with_retries() -> requests.Session:
    retry = Retry(
        total=5, connect=5, read=5, status=5,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    sess = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    sess.headers.update({"User-Agent": "WAILA-NoSQL-Student-Project/1.0 (NOAA GHCNh data retrieval)"})
    return sess


def download(url: str, target: Path, timeout: int) -> Dict[str, Any]:
    sess = session_with_retries()
    partial = target.with_suffix(target.suffix + ".part")
    start = time.time()
    with sess.get(url, stream=True, timeout=(30, timeout)) as response:
        if response.status_code == 404:
            raise RuntimeError(
                f"NOAA returned 404 for {url}. Check the station ID and current GHCNh access path; "
                "the script has not created any fake data."
            )
        response.raise_for_status()
        total = int(response.headers.get("Content-Length", "0") or 0)
        received = 0
        with open(partial, "wb") as out:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    out.write(chunk)
                    received += len(chunk)
                    if total:
                        pct = received * 100 / total
                        print(f"\rDescargando: {received:,}/{total:,} bytes ({pct:.1f}%)", end="", flush=True)
                    else:
                        print(f"\rDescargando: {received:,} bytes", end="", flush=True)
    print()
    if received == 0:
        partial.unlink(missing_ok=True)
        raise RuntimeError("NOAA respondió sin contenido; no se generó un archivo de observaciones.")
    partial.replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {
        "url": url,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": 200,
        "bytes": received,
        "sha256": digest,
        "seconds": round(time.time() - start, 2),
        "content_type": response.headers.get("Content-Type"),
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }


def convert_psv_to_jsonl(psv_path: Path, jsonl_path: Path) -> Dict[str, Any]:
    """Keep every NOAA source column and code in each JSON document.

    This is deliberately row-preserving: GHCNh uses many element/code columns and
    this script does not guess units or discard quality/source fields. The raw PSV
    remains the authoritative source file.
    """
    row_count = 0
    with psv_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as src, \
         jsonl_path.open("w", encoding="utf-8", newline="\n") as dst:
        reader = csv.DictReader(src, delimiter="|")
        if not reader.fieldnames:
            raise RuntimeError("El PSV no tiene encabezados; no parece un archivo de datos GHCNh válido.")
        fields = [f.strip() if f else f for f in reader.fieldnames]
        # DictReader keys must match original header spelling, so map each row explicitly.
        for row in reader:
            if not row or not any(v not in (None, "") for v in row.values()):
                continue
            doc: Dict[str, Any] = {}
            for original_key, value in row.items():
                key = (original_key or "").strip()
                if not key:
                    continue
                doc[key] = value.strip() if isinstance(value, str) else value
            doc["_metadata"] = {
                "dataset": "NOAA GHCNh",
                "source_file": psv_path.name,
                "station_id_requested": STATION["station_id"],
                "station_reference": STATION,
                "source_url": URL,
                "retrieved_by": "waila_spa_noaa_nosql.py",
            }
            dst.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n")
            row_count += 1
    if row_count == 0:
        raise RuntimeError("El archivo se descargó, pero no se encontraron filas de observaciones.")
    return {"jsonl_rows": row_count, "jsonl_file": jsonl_path.name, "source_columns": len(fields)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="waila_spa_noaa_data", help="Carpeta para los archivos de salida")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout de lectura en segundos")
    parser.add_argument("--url", default=URL, help="URL de NOAA; útil si NOAA cambia la ruta")
    args = parser.parse_args()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    psv_path = outdir / FILENAME
    jsonl_path = outdir / f"GHCNh_{STATION['station_id']}_por.jsonl"
    manifest_path = outdir / f"GHCNh_{STATION['station_id']}_manifest.json"

    print("NOAA GHCNh — descarga de observaciones meteorológicas reales")
    print(f"Estación: {STATION['station_id']} | {STATION['station_name']} | Bélgica")
    print(f"Coordenadas: {STATION['latitude']}, {STATION['longitude']} | elevación {STATION['elevation_m']} m")
    print(f"Origen: {args.url}")
    print("No se generarán ni imputarán mediciones sintéticas.\n")

    try:
        if psv_path.exists() and psv_path.stat().st_size > 0:
            print(f"Ya existe el PSV ({psv_path.stat().st_size:,} bytes); se reutiliza. Usa otra carpeta para descargarlo de nuevo.")
            download_meta = {"reused_existing_file": True, "bytes": psv_path.stat().st_size,
                             "sha256": hashlib.sha256(psv_path.read_bytes()).hexdigest(), "url": args.url}
        else:
            download_meta = download(args.url, psv_path, args.timeout)
        print(f"Archivo original guardado: {psv_path}")
        conversion_meta = convert_psv_to_jsonl(psv_path, jsonl_path)
        manifest = {
            "dataset": "NOAA Global Historical Climatology Network hourly (GHCNh)",
            "station": STATION,
            "period": "period of record available from NOAA; exact range is in the source rows",
            "download": download_meta,
            "conversion": conversion_meta,
            "raw_psv": str(psv_path),
            "mongodb_jsonl": str(jsonl_path),
            "quality_note": "Original NOAA fields/codes are preserved as strings; consult NOAA documentation before interpreting codes or converting units.",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\nCOMPLETADO")
        print(f"PSV original : {psv_path}")
        print(f"JSONL MongoDB: {jsonl_path} ({conversion_meta['jsonl_rows']:,} filas)")
        print(f"Manifiesto   : {manifest_path}")
        print("Importación MongoDB sugerida:")
        print(f'  mongoimport --db waila --collection weather_observation --file "{jsonl_path}" --type json')
        print("Nota: cada documento conserva una fila original completa; no se convierten unidades ni se descartan códigos de calidad.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Si la descarga falló, verifica la conexión y consulta el acceso oficial de NOAA; no se creó información meteorológica ficticia.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
