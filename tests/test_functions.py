import sys
from pathlib import Path
import pandas as pd
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bepp import download_monthly_price, load_price_file, add_basic_features

class DummyResponse:
    def __init__(self, content=b"data", status_code=200):
        self.content = content
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("error")


def test_download_monthly_price(monkeypatch, tmp_path):
    def fake_get(url):
        return DummyResponse(b"dummy")
    monkeypatch.setattr("requests.get", fake_get)
    path = download_monthly_price(2024, 1, folder=tmp_path)
    assert path.exists()
    assert path.read_bytes() == b"dummy"

def test_load_price_file(tmp_path):
    df = pd.DataFrame({
        "Time": pd.date_range("2024-01-01", periods=2, freq="H"),
        "PositivePrice": [1.0, 2.0],
        "NegativePrice": [3.0, 4.0],
    })
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    loaded = load_price_file(file_path)
    assert isinstance(loaded.index, pd.DatetimeIndex)
    assert loaded.loc[pd.Timestamp("2024-01-01 01:00")] ["PositivePrice"] == 2.0

def test_add_basic_features():
    idx = pd.date_range("2024-01-01", periods=25, freq="H")
    df = pd.DataFrame({"PositivePrice": range(25)}, index=idx)
    enriched = add_basic_features(df)
    assert "hour" in enriched.columns
    assert enriched.loc[idx[1], "lag_price"] == 0
    assert enriched.loc[idx[24], "rolling_mean_24h"] == sum(range(1,25))/24
