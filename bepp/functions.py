from pathlib import Path
import pandas as pd
import requests

BASE_URL = "https://www.swissgrid.ch/dam/swissgrid/current/Data/excel/balancingenergy/"

def download_monthly_price(year: int, month: int, folder: Path = Path('data')) -> Path:
    """Download monthly balancing energy price Excel file.

    If download fails, generate a placeholder file with zero prices.
    Returns the path to the downloaded or generated file.
    """
    folder.mkdir(exist_ok=True)
    filename = folder / f"{year}_{month:02d}_balancing_energy_prices.xlsx"
    url = f"{BASE_URL}{year}/{month:02d}/balancing_energy_prices_{year}_{month:02d}.xlsx"
    try:
        r = requests.get(url)
        r.raise_for_status()
        filename.write_bytes(r.content)
    except Exception as e:  # pragma: no cover - network or other failure
        dummy = pd.DataFrame({
            'Time': pd.date_range(f"{year}-{month:02d}-01", periods=96, freq='15min'),
            'PositivePrice': 0.0,
            'NegativePrice': 0.0,
        })
        dummy.to_excel(filename, index=False)
    return filename

def load_price_file(path: Path) -> pd.DataFrame:
    """Load a balancing price Excel file into a DataFrame indexed by time."""
    df = pd.read_excel(path)
    df = df.rename(columns=str.strip)
    df['Time'] = pd.to_datetime(df['Time'])
    return df.set_index('Time')

def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple time based features to a price DataFrame."""
    df = df.copy()
    df['hour'] = df.index.hour
    df['weekday'] = df.index.weekday
    df['month'] = df.index.month
    df['dayofyear'] = df.index.dayofyear
    df['lag_price'] = df['PositivePrice'].shift(1)
    df['rolling_mean_24h'] = df['PositivePrice'].rolling(window=24).mean()
    df['rolling_std_24h'] = df['PositivePrice'].rolling(window=24).std()
    return df

def merge_additional_data(
    prices: pd.DataFrame,
    load: pd.DataFrame | None = None,
    weather: pd.DataFrame | None = None,
    holidays: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Merge price data with optional load, weather and holiday information."""
    df = prices.resample("H").mean()
    if load is not None:
        df = df.join(load, how="left")
    if weather is not None:
        df = df.join(weather, how="left")
    if holidays is not None:
        df = df.join(holidays, how="left")
    return df
