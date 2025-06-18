import os
from datetime import datetime, timedelta
import pandas as pd
from bepp import (
    download_monthly_price,
    load_price_file,
    add_basic_features,
    merge_additional_data,
)
from fetch_additional_data import fetch_entsoe_load, fetch_weather, fetch_holidays
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

start = datetime.utcnow() - timedelta(days=7)
end = datetime.utcnow()

price_file = download_monthly_price(start.year, start.month)
prices = load_price_file(price_file)

entsoe_token = os.getenv("ENTSOE_TOKEN", "")
load = fetch_entsoe_load(start, end, entsoe_token)
weather = fetch_weather(start, end, lat=46.8, lon=8.3)
holidays_df = fetch_holidays(start, end)

merged = merge_additional_data(prices, load, weather, holidays_df)
features = add_basic_features(merged).join(merged[["load", "temperature", "wind_speed", "holiday"]])

X = features.dropna()[[
    "hour", "weekday", "month", "dayofyear", "lag_price",
    "rolling_mean_24h", "rolling_std_24h", "load", "temperature",
    "wind_speed", "holiday",
]]
y = features.loc[X.index, "PositivePrice"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
model = GradientBoostingRegressor()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
