import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# 1. Download historical data
ticker = "PANW"
from datetime import datetime, timedelta

# Get the current date
end_date = datetime.today().strftime('%Y-%m-%d')
# Calculate the date one year before the current date
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

# Fetch data for the last year
data = yf.download(ticker, start=start_date, end=end_date)
data.dropna(inplace=True)

# 2. Detect key price points (peaks and troughs)
def detect_key_points(prices):
    peaks, _ = find_peaks(prices, distance=10)  # Local maxima
    troughs, _ = find_peaks(-prices, distance=10)  # Local minima
    key_points = sorted(np.concatenate([peaks, troughs]))
    return key_points

key_points = detect_key_points(data['Close'].values)

# Restrict to the 5 most recent key points
if len(key_points) >= 5:
    key_points = key_points[-5:]
    key_prices = data['Close'].values[key_points]
else:
    print("Not enough data points for harmonic analysis.")
    key_points, key_prices = [], []

# 3. Detect harmonic patterns
def detect_harmonic_pattern(prices):
    """
    Detect specific harmonic patterns using Fibonacci ratios.
    Returns the detected pattern name or None.
    """
    if len(prices) < 5:
        return None

    # Calculate price swings
    XA = prices[1] - prices[0]
    AB = prices[2] - prices[1]
    BC = prices[3] - prices[2]
    CD = prices[4] - prices[3]

    # Calculate Fibonacci ratios
    ratios = {
        "AB/XA": abs(AB / XA),
        "BC/AB": abs(BC / AB),
        "CD/BC": abs(CD / BC)
    }

    # Check for Gartley pattern
    if 0.618 <= ratios["AB/XA"] <= 0.786 and 0.382 <= ratios["BC/AB"] <= 0.886 and 1.27 <= ratios["CD/BC"] <= 1.618:
        return "Bullish Gartley"
    # Check for Butterfly pattern
    elif 0.786 <= ratios["AB/XA"] <= 0.786 and 0.382 <= ratios["BC/AB"] <= 0.886 and 1.618 <= ratios["CD/BC"] <= 2.618:
        return "Bullish Butterfly"
    # Check for Bat pattern
    elif 0.382 <= ratios["AB/XA"] <= 0.5 and 0.382 <= ratios["BC/AB"] <= 0.886 and 1.618 <= ratios["CD/BC"] <= 2.618:
        return "Bullish Bat"
    # Check for Crab pattern
    elif 0.382 <= ratios["AB/XA"] <= 0.618 and 0.382 <= ratios["BC/AB"] <= 0.886 and 2.618 <= ratios["CD/BC"] <= 3.618:
        return "Bullish Crab"

    return None

# Identify the pattern
pattern = detect_harmonic_pattern(key_prices)

# 4. Suggest an action based on the pattern
def suggest_action(pattern):
    if pattern:
        if "Bullish" in pattern:
            return "BUY"
        elif "Bearish" in pattern:
            return "SELL"
    return "HOLD"

action = suggest_action(pattern)

# Print pattern and action
if pattern:
    print(f"Harmonic Pattern Detected: {pattern}")
    print(f"Suggested Action: {action}")
else:
    print("No harmonic pattern detected.")
    print("Suggested Action: HOLD")

# 5. Plot the price data with key points
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Close'], label="Close Price", color='blue')
if key_points:
    plt.scatter(data.index[key_points], data['Close'].values[key_points], color='red', label="Key Points", zorder=5)
plt.title(f"{ticker} Price Analysis with Harmonic Patterns")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.show()
