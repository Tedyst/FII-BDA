import argparse
import os
from pathlib import Path
import sys
import pandas as pd


def convert_csv_to_parquet(
    input_dir: Path, output_dir: Path, pattern: str = "*.csv"
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob(pattern))
    if not csv_files:
        print(f"No CSV files found in {input_dir} matching '{pattern}'.")
        return

    print(f"Found {len(csv_files)} CSV file(s) in {input_dir}.")
    for idx, csv_path in enumerate(csv_files, start=1):
        out_path = output_dir / (csv_path.stem + ".parquet")
        try:
            print(f"[{idx}/{len(csv_files)}] Reading {csv_path.name} …", flush=True)
            df = pd.read_csv(csv_path, low_memory=False)

            # Ensure pyarrow engine is used
            print(f"    Writing {out_path.name} …", flush=True)
            df.to_parquet(out_path, engine="pyarrow", index=False)
        except Exception as e:
            print(f"    ERROR converting {csv_path.name}: {e}", file=sys.stderr)

    print(f"Done. Parquet files are in: {output_dir}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert CSV files to Parquet using pandas (pyarrow engine)."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("dataset"),
        help="Directory containing CSV files (default: dataset)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("converted-dataset"),
        help="Directory to write Parquet files (default: converted-dataset)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.csv",
        help="Glob pattern to match CSV files (default: *.csv)",
    )

    args = parser.parse_args(argv)

    if not args.input_dir.exists() or not args.input_dir.is_dir():
        print(
            f"Input directory does not exist or is not a directory: {args.input_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    convert_csv_to_parquet(args.input_dir, args.output_dir, args.pattern)


if __name__ == "__main__":
    main()
