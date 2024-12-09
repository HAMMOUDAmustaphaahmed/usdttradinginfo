from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# Function to fetch candlestick data from Binance API
def fetch_candlestick_data(time_frame):
    url = 'https://api.binance.com/api/v3/exchangeInfo'
    response = requests.get(url)
    exchange_data = response.json()

    symbols = [symbol for symbol in exchange_data['symbols'] if symbol['quoteAsset'] == 'USDT']
    
    trading_pairs = []
    for symbol in symbols:
        symbol_name = symbol['symbol']
        klines_url = f'https://api.binance.com/api/v3/klines?symbol={symbol_name}&interval={time_frame}&limit=10'
        klines_response = requests.get(klines_url)
        candlestick_data = klines_response.json()

        candlesticks = [
            {
                'openTime': item[0],
                'open': float(item[1]),
                'high': float(item[2]),
                'low': float(item[3]),
                'close': float(item[4]),
                'volume': float(item[5]),
                'closeTime': item[6]
            }
            for item in candlestick_data
        ]
        
        chandelier_of_reference = max(candlesticks, key=lambda x: x['high'])
        filtered_candlesticks = [candlestick for candlestick in candlesticks if candlestick['low'] >= chandelier_of_reference['low'] / 2]
        last_chandelier_97 = next((candlestick for candlestick in filtered_candlesticks if candlestick['high'] >= chandelier_of_reference['high'] * 0.97), None)
        
        trading_pairs.append({
            'symbol': f"{symbol_name[:len(symbol_name)//2]}-USDT",  # Assuming base asset is first half
            'chandelierOfReferenceHigh': chandelier_of_reference['high'],
            'lastChandelier97High': last_chandelier_97['high'] if last_chandelier_97 else None
        })

    return trading_pairs

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch the data when the "Start" button is pressed
@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    time_frame = request.form.get('timeFrame', '1h')  # Get the selected time frame from the form
    trading_pairs = fetch_candlestick_data(time_frame)
    
    # Filter out pairs that don't have a valid lastChandelier97High
    filtered_pairs = [pair for pair in trading_pairs if pair['lastChandelier97High'] is not None]
    
    return jsonify(filtered_pairs)

if __name__ == '__main__':
    app.run(debug=True)

