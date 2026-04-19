from flask import Flask, render_template, request, jsonify, send_file
from main import run_analysis, validate_ticker
from pdf_generator import generate_pdf, generate_comparison_pdf
import os
import threading
import time
from dotenv import load_dotenv
import requests as req  

load_dotenv()
def get_user_currency(request):
    """Detect user currency from their IP location."""
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip == '127.0.0.1':
            return 'INR'
        res      = req.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        data     = res.json()
        currency = data.get('currency', 'USD')
        return currency
    except:
        return 'USD'

app = Flask(__name__)

app = Flask(__name__)

# Store analysis results temporarily
analysis_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data   = request.json
    mode   = data.get('mode')
    ticker = data.get('ticker', '').upper().strip()
    user_currency = get_user_currency(request)

    if mode == 'single':
        if not ticker:
            return jsonify({'error': 'Please enter a stock ticker.'}), 400
        if not validate_ticker(ticker):
            return jsonify({'error': f"'{ticker}' is not a valid stock ticker."}), 400

        result   = run_analysis(ticker)
        pdf_path = generate_pdf(ticker, result, user_currency)


        analysis_store[ticker] = {
            'result':   result,
            'pdf_path': pdf_path
        }

        rec  = 'BUY' if 'BUY' in result.upper() else ('SELL' if 'SELL' in result.upper() else 'HOLD')
        risk = 'HIGH' if 'HIGH RISK' in result.upper() else ('LOW' if 'LOW RISK' in result.upper() else 'MEDIUM')

        return jsonify({
            'success':  True,
            'ticker':   ticker,
            'rec':      rec,
            'risk':     risk,
            'result':   result,
            'pdf_file': os.path.basename(pdf_path)
        })

    elif mode == 'comparison':
        tickers_raw = data.get('tickers', '')
        tickers     = [t.strip().upper() for t in tickers_raw.split(',') if t.strip()]

        if len(tickers) < 2:
            return jsonify({'error': 'Please enter at least 2 tickers.'}), 400

        valid_tickers = [t for t in tickers if validate_ticker(t)]
        if len(valid_tickers) < 2:
            return jsonify({'error': 'Need at least 2 valid tickers.'}), 400

        results = {}
        for i, ticker in enumerate(valid_tickers):
            results[ticker] = run_analysis(ticker)
            if i < len(valid_tickers) - 1:
                time.sleep(30)

        pdf_path = generate_comparison_pdf(results, user_currency)


        summary = {}
        for ticker, result in results.items():
            summary[ticker] = {
                'rec':  'BUY' if 'BUY' in result.upper() else ('SELL' if 'SELL' in result.upper() else 'HOLD'),
                'risk': 'HIGH' if 'HIGH RISK' in result.upper() else ('LOW' if 'LOW RISK' in result.upper() else 'MEDIUM')
            }

        return jsonify({
            'success':  True,
            'summary':  summary,
            'pdf_file': os.path.basename(pdf_path)
        })

    return jsonify({'error': 'Invalid mode.'}), 400

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join('output', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)