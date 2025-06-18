import os
import pandas as pd
from pathlib import Path
import requests
from datetime import datetime, timedelta

try:
    from entsoe import EntsoePandasClient
except ImportError:
    EntsoePandasClient = None

try:
    import holidays
except ImportError:
    holidays = None

BASE_URL = "https://www.swissgrid.ch/dam/swissgrid/current/Data/excel/balancingenergy/"

# Swissgrid data download (as in notebook)
def download_monthly_price(year: int, month: int, folder: Path = Path('data')) -> Path:
    folder.mkdir(exist_ok=True)
    filename = folder / f"{year}_{month:02d}_balancing_energy_prices.xlsx"
    url = f"{BASE_URL}{year}/{month:02d}/balancing_energy_prices_{year}_{month:02d}.xlsx"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        filename.write_bytes(r.content)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Could not download {url}: {e}. Generating dummy data")
        dummy = pd.DataFrame({
            'Time': pd.date_range(f"{year}-{month:02d}-01", periods=96, freq='15min'),
            'PositivePrice': 0.0,
            'NegativePrice': 0.0
        })
        dummy.to_excel(filename, index=False)
    return filename

# ENTSO-E load and generation data
def fetch_entsoe_load(start: datetime, end: datetime, token: str) -> pd.DataFrame:
    if EntsoePandasClient is None:
        raise RuntimeError("entsoe-py not installed")
    client = EntsoePandasClient(api_key=token)
    try:
        load = client.query_load(country_code='CH', start=start, end=end)
        load = load.rename('load')
        return load.to_frame()
    except Exception as e:
        print(f"Could not download ENTSO-E data: {e}. Returning dummy data")
        idx = pd.date_range(start, end, freq='H', inclusive='left')
        return pd.DataFrame({'load': 0.0}, index=idx)

# MeteoSchweiz (Open Meteo) weather data
def fetch_weather(start: datetime, end: datetime, lat: float, lon: float) -> pd.DataFrame:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&hourly=temperature_2m,wind_speed_10m"
        f"&start_date={start.date()}&end_date={end.date()}&timezone=UTC"
    )
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        times = pd.to_datetime(data['hourly']['time'])
        df = pd.DataFrame({'temperature': data['hourly']['temperature_2m'],
                           'wind_speed': data['hourly']['wind_speed_10m']},
                          index=times)
        return df
    except Exception as e:
        print(f"Could not download weather data: {e}. Returning dummy data")
        idx = pd.date_range(start, end, freq='H', inclusive='left')
        return pd.DataFrame({'temperature': 0.0, 'wind_speed': 0.0}, index=idx)

# Swiss holidays
def fetch_holidays(start: datetime, end: datetime) -> pd.DataFrame:
    if holidays is None:
        raise RuntimeError("holidays library not installed")
    ch_holidays = holidays.CH(years=range(start.year, end.year + 1))
    idx = pd.date_range(start, end, freq='D')
    flags = [1 if day.date() in ch_holidays else 0 for day in idx]
    return pd.DataFrame({'holiday': flags}, index=idx)

if __name__ == "__main__":
    start = datetime.utcnow() - timedelta(days=7)
    end = datetime.utcnow()
    token = os.getenv('ENTSOE_TOKEN', '')

    price_file = download_monthly_price(start.year, start.month)
    prices = pd.read_excel(price_file, parse_dates=['Time']).set_index('Time')

    if token:
        load = fetch_entsoe_load(start, end, token)
    else:
        print("ENTSOE_TOKEN not set. Using dummy load data")
        load = fetch_entsoe_load(start, end, token)

    weather = fetch_weather(start, end, lat=46.8, lon=8.3)
    holidays_df = fetch_holidays(start, end)

    # merge to hourly for simplicity
    prices_h = prices.resample('H').mean()
    data = prices_h.join(load, how='left').join(weather, how='left')
    data = data.join(holidays_df, how='left')
    data.to_csv('merged_data.csv')
    print("Merged data written to merged_data.csv")

