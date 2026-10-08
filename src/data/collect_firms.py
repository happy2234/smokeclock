from pathlib import Path

from firms_client import fetch_fires


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "firms"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    df = fetch_fires(
        west=73.5,
        south=27.5,
        east=78.5,
        north=32.5,
        source="VIIRS_NOAA21_NRT",
        days=1,
    )

    output_file = OUTPUT_DIR / "fires_latest.csv"
    df.to_csv(output_file, index=False)

    print(f"Saved {len(df):,} detections")
    print(f"File: {output_file}")


if __name__ == "__main__":
    main()
