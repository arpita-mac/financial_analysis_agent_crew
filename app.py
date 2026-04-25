from flask import Flask, render_template, request, jsonify, send_file
from main import run_analysis, validate_ticker
from pdf_generator import generate_pdf, generate_comparison_pdf
import os
import time
import base64
import requests as req
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

os.makedirs('output', exist_ok=True)

def get_user_currency(req_obj):
    try:
        ip = req_obj.headers.get('X-Forwarded-For', req_obj.remote_addr)
        if ip == '127.0.0.1':
            return 'INR'
        res      = req.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        data     = res.json()
        currency = data.get('currency', 'USD')
        return currency
    except:
        return 'USD'

def fetch_stock_data(ticker: str):
    try:
        s = req.Session()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        stock = yf.Ticker(ticker, session=s)
        info  = stock.info
        hist  = stock.history(period="1y")
        print(f"✅ Fetched data for {ticker}: price={info.get('currentPrice')}, hist_rows={len(hist)}")
        return info, hist
    except Exception as e:
        print(f"❌ fetch_stock_data failed for {ticker}: {str(e)}")
        return {}, None

app = Flask(__name__)
analysis_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data          = request.json
    mode          = data.get('mode')
    ticker        = data.get('ticker', '').upper().strip()
    user_currency = get_user_currency(request)

    if mode == 'single':
        if not ticker:
            return jsonify({'error': 'Please enter a stock ticker.'}), 400
        if not validate_ticker(ticker):
            return jsonify({'error': f"'{ticker}' is not a valid stock ticker."}), 400

        result              = run_analysis(ticker)
        info, hist          = fetch_stock_data(ticker)
        pdf_path            = generate_pdf(ticker, result, user_currency,
                                           prefetched_info=info,
                                           prefetched_hist=hist)

        analysis_store[ticker] = {'result': result, 'pdf_path': pdf_path}

        rec  = 'BUY' if 'BUY' in result.upper() else ('SELL' if 'SELL' in result.upper() else 'HOLD')
        risk = 'HIGH' if 'HIGH RISK' in result.upper() else ('LOW' if 'LOW RISK' in result.upper() else 'MEDIUM')

        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'success':  True,
            'ticker':   ticker,
            'rec':      rec,
            'risk':     risk,
            'result':   result,
            'pdf_file': os.path.basename(pdf_path),
            'pdf_data': pdf_data
        })

    elif mode == 'comparison':
        tickers_raw   = data.get('tickers', '')
        tickers       = [t.strip().upper() for t in tickers_raw.split(',') if t.strip()]

        if len(tickers) < 2:
            return jsonify({'error': 'Please enter at least 2 tickers.'}), 400

        valid_tickers = [t for t in tickers if validate_ticker(t)]
        if len(valid_tickers) < 2:
            return jsonify({'error': 'Need at least 2 valid tickers.'}), 400

        results      = {}
        prefetched   = {}
        for i, ticker in enumerate(valid_tickers):
            results[ticker]    = run_analysis(ticker)
            info, hist         = fetch_stock_data(ticker)
            prefetched[ticker] = {'info': info, 'hist': hist}
            if i < len(valid_tickers) - 1:
                time.sleep(30)

        pdf_path = generate_comparison_pdf(results, user_currency,
                                           prefetched_data=prefetched)

        summary = {}
        for ticker, result in results.items():
            summary[ticker] = {
                'rec':  'BUY' if 'BUY' in result.upper() else ('SELL' if 'SELL' in result.upper() else 'HOLD'),
                'risk': 'HIGH' if 'HIGH RISK' in result.upper() else ('LOW' if 'LOW RISK' in result.upper() else 'MEDIUM')
            }

        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            'success':  True,
            'summary':  summary,
            'pdf_file': os.path.basename(pdf_path),
            'pdf_data': pdf_data
        })

    return jsonify({'error': 'Invalid mode.'}), 400

@app.route('/watchlist', methods=['POST'])
def save_watchlist():
    try:
        from models import db, Watchlist
        from email_sender import send_confirmation_email
        data    = request.json
        email   = data.get('email', '').strip()
        tickers = data.get('tickers', '').strip()
        if not email or not tickers:
            return jsonify({'error': 'Email and tickers are required.'}), 400
        existing = Watchlist.query.filter_by(email=email).first()
        if existing:
            existing.tickers = tickers
            message = f'Watchlist updated! Now tracking: {tickers}'
        else:
            db.session.add(Watchlist(email=email, tickers=tickers))
            message = 'Watchlist saved! You will receive reports every Sunday.'
        db.session.commit()
        ticker_list = [t.strip().upper() for t in tickers.split(',') if t.strip()]
        send_confirmation_email(email, ticker_list, request.host_url)
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watchlist/<email>', methods=['GET'])
def get_watchlist(email):
    try:
        from models import Watchlist
        watchlist = Watchlist.query.filter_by(email=email).first()
        if watchlist:
            return jsonify({'tickers': watchlist.tickers})
        return jsonify({'tickers': ''})
    except:
        return jsonify({'tickers': ''})

@app.route('/watchlist/analyze', methods=['POST'])
def analyze_watchlist():
    try:
        from models import Watchlist
        from email_sender import send_report_email
        data          = request.json
        email         = data.get('email', '').strip()
        user_currency = get_user_currency(request)
        watchlist     = Watchlist.query.filter_by(email=email).first()
        if not watchlist:
            return jsonify({'error': 'No watchlist found for this email.'}), 404
        tickers = watchlist.get_tickers()
        if not tickers:
            return jsonify({'error': 'Your watchlist is empty.'}), 400
        results    = {}
        prefetched = {}
        for i, ticker in enumerate(tickers):
            results[ticker]    = run_analysis(ticker)
            info, hist         = fetch_stock_data(ticker)
            prefetched[ticker] = {'info': info, 'hist': hist}
            if i < len(tickers) - 1:
                time.sleep(30)
        pdf_path = generate_comparison_pdf(results, user_currency,
                                           prefetched_data=prefetched)
        send_report_email(email, tickers, pdf_path)
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        summary = {}
        for ticker, result in results.items():
            summary[ticker] = {
                'rec':  'BUY' if 'BUY' in result.upper() else ('SELL' if 'SELL' in result.upper() else 'HOLD'),
                'risk': 'HIGH' if 'HIGH RISK' in result.upper() else ('LOW' if 'LOW RISK' in result.upper() else 'MEDIUM')
            }
        return jsonify({
            'success':  True,
            'summary':  summary,
            'pdf_file': os.path.basename(pdf_path),
            'pdf_data': pdf_data,
            'message':  f'Report sent to {email}!'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join('output', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=filename)
    return "File not found — please run the analysis again.", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
