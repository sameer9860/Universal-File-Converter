import pandas as pd
import json
import yaml
from pathlib import Path

def convert(input_path: Path, output_path: Path) -> None:
    """Converts data formats (CSV, JSON, XLSX, YAML, XML) using pandas and stdlib."""
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower()

    # Step 1: Read into pandas DataFrame
    df = _read_data(input_path, in_ext)

    # Step 2: Write from pandas DataFrame to output format
    _write_data(df, output_path, out_ext)

def _read_data(path: Path, ext: str) -> pd.DataFrame:
    try:
        if ext == ".csv":
            return pd.read_csv(path)
        elif ext == ".json":
            # Assume records format for tabular JSON
            return pd.read_json(path, orient="records")
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(path, engine="openpyxl")
        elif ext == ".xml":
            return pd.read_xml(path)
        elif ext == ".yaml" or ext == ".yml":
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            # Try to convert yaml list of dicts to dataframe
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Input format {ext} not supported for data conversion")
    except Exception as e:
        raise RuntimeError(f"Failed to read {ext} data: {e}")

def _write_data(df: pd.DataFrame, path: Path, ext: str) -> None:
    try:
        if ext == ".csv":
            df.to_csv(path, index=False)
        elif ext == ".json":
            df.to_json(path, orient="records", indent=2)
        elif ext == ".xlsx":
            df.to_excel(path, index=False, engine="openpyxl")
        elif ext == ".xml":
            df.to_xml(path, index=False)
        elif ext == ".yaml" or ext == ".yml":
            # Convert DF to list of dicts, then dump
            data = df.to_dict(orient="records")
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            raise ValueError(f"Output format {ext} not supported for data conversion")
    except Exception as e:
        raise RuntimeError(f"Failed to write {ext} data: {e}")
