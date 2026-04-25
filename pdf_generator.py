from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import yfinance as yf
import requests as _req

DARK   = colors.HexColor('#0D1B2A')
ACCENT = colors.HexColor('#1F6FEB')
GREEN  = colors.HexColor('#1A7F4B')
RED    = colors.HexColor('#CF2B2B')
AMBER  = colors.HexColor('#D97706')
LIGHT  = colors.HexColor('#F4F6F9')
MUTED  = colors.HexColor('#6B7280')
WHITE  = colors.white

CHART_COLORS = ['#1F6FEB', '#F72585', '#4CC9F0', '#7209B7', '#3A0CA3']

LOCALE_CURRENCY_MAP = {
    'INR': '₹', 'KRW': '₩', 'USD': '$', 'GBP': '£',
    'EUR': '€', 'JPY': '¥', 'CNY': '¥', 'AUD': 'A$',
    'CAD': 'C$', 'SGD': 'S$',
}

CURRENCY_TEXT_MAP = {
    '₹': 'INR ', '₩': 'KRW ', '¥': 'JPY ', '£': 'GBP ',
    '€': 'EUR ', 'A$': 'AUD ', 'C$': 'CAD ', 'S$': 'SGD ', '$': '$',
}

def get_symbol(currency: str) -> str:
    return LOCALE_CURRENCY_MAP.get(currency, '$')

def pdf_symbol(symbol: str) -> str:
    return CURRENCY_TEXT_MAP.get(symbol, symbol)

def get_fx_rate(from_currency: str, to_currency: str) -> float:
    if not from_currency or from_currency == to_currency:
        return 1.0
    try:
        pair = f"{from_currency}{to_currency}=X"
        rate = yf.Ticker(pair).info.get('regularMarketPrice', None)
        if rate:
            return float(rate)
        return 1.0
    except:
        return 1.0

def fmt_currency(amount, symbol='$'):
    if not amount: return 'N/A'
    s = pdf_symbol(symbol)
    if amount >= 1e12: return f"{s}{amount/1e12:.2f}T"
    if amount >= 1e9:  return f"{s}{amount/1e9:.1f}B"
    if amount >= 1e6:  return f"{s}{amount/1e6:.1f}M"
    return f"{s}{amount:,.0f}"

def get_stock_metrics(ticker: str, user_currency: str = 'USD', prefetched_info=None):
    try:
        if prefetched_info:
            info = prefetched_info
        else:
            s = _req.Session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            info = yf.Ticker(ticker, session=s).info

        stock_currency = info.get('currency', 'USD')
        symbol         = get_symbol(user_currency)
        fx             = get_fx_rate(stock_currency, user_currency)

        def to_user(val):
            if not val: return 0
            return val * fx

        price         = to_user(info.get('currentPrice') or info.get('regularMarketPrice', 0))
        market_cap    = to_user(info.get('marketCap', 0))
        revenue       = to_user(info.get('totalRevenue', 0))
        week_high     = to_user(info.get('fiftyTwoWeekHigh', 0))
        week_low      = to_user(info.get('fiftyTwoWeekLow', 0))
        profit_margin = round((info.get('profitMargins', 0) or 0) * 100, 2)
        pe_ratio      = info.get('trailingPE', 0)

        return {
            'price':          price,
            'pe_ratio':       pe_ratio,
            'profit_margin':  profit_margin,
            'market_cap':     market_cap,
            'market_cap_fmt': fmt_currency(market_cap, symbol),
            'revenue':        revenue,
            'revenue_fmt':    fmt_currency(revenue, symbol),
            'revenue_b':      round(revenue / 1e9, 2) if revenue else 0,
            'market_cap_b':   round(market_cap / 1e9, 2) if market_cap else 0,
            '52w_high':       week_high,
            '52w_low':        week_low,
            'currency':       user_currency,
            'symbol':         symbol,
        }
    except:
        return {}

def extract_recommendation(text: str):
    t = text.upper()
    if 'STRONG BUY' in t: return 'STRONG BUY', GREEN
    if 'BUY'       in t: return 'BUY',        GREEN
    if 'SELL'      in t: return 'SELL',       RED
    if 'HOLD'      in t: return 'HOLD',       AMBER
    return 'N/A', MUTED

def extract_risk(text: str):
    t = text.upper()
    if 'HIGH RISK' in t or 'RISK: HIGH' in t: return 'HIGH', RED
    if 'LOW RISK'  in t or 'RISK: LOW'  in t: return 'LOW',  GREEN
    return 'MEDIUM', AMBER

def price_history_chart(ticker: str, width=6.5, height=2.8,
                        user_currency: str = 'USD', prefetched_hist=None):
    try:
        symbol = get_symbol(user_currency)

        if prefetched_hist is not None and not prefetched_hist.empty:
            hist = prefetched_hist
            fx   = get_fx_rate('USD', user_currency)
        else:
            s     = _req.Session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            stock          = yf.Ticker(ticker, session=s)
            hist           = stock.history(period="1y")
            stock_currency = stock.info.get('currency', 'USD')
            fx             = get_fx_rate(stock_currency, user_currency)

        if hist is None or hist.empty:
            return None

        dates  = hist.index
        prices = hist['Close'] * fx

        fig, ax = plt.subplots(figsize=(width, height))
        fig.patch.set_facecolor('#F4F6F9')
        ax.set_facecolor('#F4F6F9')

        ax.plot(dates, prices, color='#1F6FEB', linewidth=2)
        ax.fill_between(dates, prices, prices.min(), alpha=0.15, color='#1F6FEB')

        start_price = prices.iloc[0]
        end_price   = prices.iloc[-1]
        pct_change  = ((end_price - start_price) / start_price) * 100
        line_color  = '#1A7F4B' if pct_change >= 0 else '#CF2B2B'
        sign        = '+' if pct_change >= 0 else ''

        ax.set_title(f"{ticker} — 12 Month Price History  ({sign}{pct_change:.1f}%)",
                     fontsize=12, fontweight='bold', color='#0D1B2A', pad=10)
        ax.set_ylabel(f'Price ({user_currency})', fontsize=9, color='#6B7280')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')
        ax.tick_params(colors='#6B7280', labelsize=8)

        ax.annotate(f'{symbol}{start_price:.0f}',
                    xy=(dates[0], start_price), fontsize=8, color='#6B7280',
                    xytext=(10, 10), textcoords='offset points')
        ax.annotate(f'{symbol}{end_price:.0f}',
                    xy=(dates[-1], end_price), fontsize=9, fontweight='bold',
                    color=line_color, xytext=(-40, 10), textcoords='offset points')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=160, bbox_inches='tight', facecolor='#F4F6F9')
        plt.close()
        buf.seek(0)
        return buf

    except Exception as e:
        print(f"Chart error for {ticker}: {e}")
        return None

def price_gauge_img(price, low, high, ticker, symbol='$', width=5.5, height=1.8):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor('#F4F6F9')
    ax.set_facecolor('#F4F6F9')
    ax.barh([0], [high - low], left=low, height=0.3, color='#E5E7EB', edgecolor='white')
    pct        = (price - low) / (high - low) if (high - low) else 0.5
    fill_color = '#1A7F4B' if pct > 0.6 else ('#D97706' if pct > 0.35 else '#CF2B2B')
    ax.barh([0], [price - low], left=low, height=0.3, color=fill_color, edgecolor='white')
    ax.axvline(price, color='#0D1B2A', linewidth=2.5)
    ax.text(price, 0.22, f'  {symbol}{price:,.2f}', ha='left', fontsize=10,
            fontweight='bold', color='#0D1B2A')
    ax.text(low,  -0.32, f'52W Low: {symbol}{low:,.2f}',  ha='left',  fontsize=8.5, color='#6B7280')
    ax.text(high, -0.32, f'52W High: {symbol}{high:,.2f}', ha='right', fontsize=8.5, color='#6B7280')
    ax.set_title(f'{ticker} — 52-Week Price Range', fontsize=11,
                 fontweight='bold', color='#0D1B2A', pad=8)
    ax.set_xlim(low * 0.92, high * 1.08)
    ax.set_ylim(-0.65, 0.55)
    ax.axis('off')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=160, bbox_inches='tight', facecolor='#F4F6F9')
    plt.close()
    buf.seek(0)
    return buf

def bar_chart_img(labels, values, title, ylabel, color_list, width=5.2, height=2.6):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor('#F4F6F9')
    ax.set_facecolor('#F4F6F9')
    bars = ax.bar(labels, values, color=color_list, width=0.45, edgecolor='white', linewidth=1.2)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=8, color='#0D1B2A')
    ax.set_ylabel(ylabel, fontsize=9, color='#6B7280')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E5E7EB')
    ax.spines['bottom'].set_color('#E5E7EB')
    ax.tick_params(colors='#6B7280', labelsize=10)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.01 * max(values or [1]),
                f'{val:,.1f}', ha='center', va='bottom',
                fontsize=8.5, fontweight='bold', color='#0D1B2A')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=160, bbox_inches='tight', facecolor='#F4F6F9')
    plt.close()
    buf.seek(0)
    return buf

def get_styles():
    base = getSampleStyleSheet()
    return {
        'title':      ParagraphStyle('Ttl', parent=base['Title'],
                          fontSize=26, textColor=WHITE,
                          spaceAfter=4, alignment=TA_LEFT, fontName='Helvetica-Bold'),
        'subtitle':   ParagraphStyle('Sub', parent=base['Normal'],
                          fontSize=11, textColor=colors.HexColor('#A0AEC0'),
                          spaceAfter=0, alignment=TA_LEFT),
        'section':    ParagraphStyle('Sec', parent=base['Heading1'],
                          fontSize=13, textColor=WHITE,
                          spaceBefore=0, spaceAfter=0, fontName='Helvetica-Bold'),
        'body':       ParagraphStyle('Bod', parent=base['Normal'],
                          fontSize=10.5, textColor=colors.HexColor('#1F2937'),
                          spaceAfter=5, leading=17),
        'bullet':     ParagraphStyle('Bul', parent=base['Normal'],
                          fontSize=10.5, textColor=colors.HexColor('#1F2937'),
                          spaceAfter=4, leading=16, leftIndent=12),
        'numbered':   ParagraphStyle('Num', parent=base['Normal'],
                          fontSize=12, textColor=DARK,
                          spaceAfter=4, leading=18, fontName='Helvetica-Bold'),
        'label':      ParagraphStyle('Lbl', parent=base['Normal'],
                          fontSize=9, textColor=MUTED,
                          spaceAfter=1, fontName='Helvetica-Bold'),
        'metric':     ParagraphStyle('Met', parent=base['Normal'],
                          fontSize=15, textColor=DARK,
                          spaceAfter=0, fontName='Helvetica-Bold', alignment=TA_CENTER),
        'disclaimer': ParagraphStyle('Dis', parent=base['Normal'],
                          fontSize=8.5, textColor=MUTED, alignment=TA_CENTER),
    }

def section_header(title, styles):
    tbl = Table([[Paragraph(title, styles['section'])]], colWidths=[6.5*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [6,6,6,6]),
    ]))
    return tbl

def metric_card(label, value, styles):
    tbl = Table([
        [Paragraph(label, styles['label'])],
        [Paragraph(str(value), styles['metric'])],
    ], colWidths=[1.55*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ROUNDEDCORNERS', [6,6,6,6]),
    ]))
    return tbl

def render_body(text, story, styles):
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.07*inch))
            continue
        clean = line.replace('**', '').replace('##', '').replace('__', '')
        if len(clean) < 60 and clean and clean[0].isdigit() and '. ' in clean:
            story.append(Spacer(1, 0.08*inch))
            story.append(Paragraph(clean, styles['numbered']))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor('#E5E7EB')))
            story.append(Spacer(1, 0.05*inch))
        elif line.startswith(('* ', '- ', '• ', '+ ')):
            story.append(Paragraph(f"•  {clean.lstrip('*-•+ ')}", styles['bullet']))
        elif line.startswith('**') and line.endswith('**'):
            story.append(Paragraph(clean, styles['numbered']))
        elif line.startswith('#'):
            story.append(Paragraph(clean.lstrip('# '), styles['numbered']))
        else:
            story.append(Paragraph(clean, styles['body']))


def generate_pdf(ticker: str, analysis_result: str, user_currency: str = 'USD',
                 prefetched_info=None, prefetched_hist=None):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn     = f"{output_dir}/{ticker}_analysis_{ts}.pdf"
    symbol = get_symbol(user_currency)

    doc = SimpleDocTemplate(fn, pagesize=letter,
                            rightMargin=0.85*inch, leftMargin=0.85*inch,
                            topMargin=0.75*inch,   bottomMargin=0.75*inch)
    S   = get_styles()
    m   = get_stock_metrics(ticker, user_currency, prefetched_info=prefetched_info)
    rec,  rec_color  = extract_recommendation(analysis_result)
    risk, risk_color = extract_risk(analysis_result)

    story = []

    hdr = Table([[
        Paragraph(ticker, S['title']),
        Paragraph(f"Generated {datetime.now().strftime('%b %d, %Y')} | {user_currency}", S['subtitle']),
    ]], colWidths=[4*inch, 2.7*inch])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,0), (-1,-1), 18),
        ('LEFTPADDING',   (0,0), (-1,-1), 18),
        ('RIGHTPADDING',  (0,0), (-1,-1), 18),
        ('ALIGN',         (1,0), (1,0),   'RIGHT'),
        ('ROUNDEDCORNERS', [8,8,8,8]),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.15*inch))

    pills = Table([[
        Paragraph('RECOMMENDATION', S['label']),
        Paragraph('RISK LEVEL',     S['label']),
    ],[
        Paragraph(rec,  ParagraphStyle('Rp', parent=S['metric'], textColor=WHITE)),
        Paragraph(risk, ParagraphStyle('Rp', parent=S['metric'], textColor=WHITE)),
    ]], colWidths=[3.25*inch, 3.25*inch])
    pills.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), rec_color),
        ('BACKGROUND',    (1,0), (1,-1), risk_color),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR',     (0,0), (-1,-1), WHITE),
        ('ROUNDEDCORNERS', [8,8,8,8]),
    ]))
    story.append(pills)
    story.append(Spacer(1, 0.15*inch))

    if m:
        cards = [
            metric_card('Current Price',  f"{pdf_symbol(symbol)}{m.get('price',0):,.2f}", S),
            metric_card('Market Cap',     m.get('market_cap_fmt', 'N/A'),                  S),
            metric_card('P/E Ratio',      f"{m.get('pe_ratio',0):.1f}",                   S),
            metric_card('Profit Margin',  f"{m.get('profit_margin',0):.1f}%",             S),
        ]
        row_tbl = Table([cards], colWidths=[1.55*inch]*4, hAlign='CENTER')
        row_tbl.setStyle(TableStyle([
            ('LEFTPADDING',  (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(row_tbl)
        story.append(Spacer(1, 0.15*inch))

    if m and m.get('52w_high') and m.get('52w_low'):
        buf = price_gauge_img(m['price'], m['52w_low'], m['52w_high'], ticker, pdf_symbol(symbol))
        story.append(Image(buf, width=6.5*inch, height=1.9*inch))
        story.append(Spacer(1, 0.15*inch))

    hist_buf = price_history_chart(ticker, user_currency=user_currency,
                                   prefetched_hist=prefetched_hist)
    if hist_buf:
        story.append(section_header("📈  12 Month Price History", S))
        story.append(Spacer(1, 0.12*inch))
        story.append(Image(hist_buf, width=6.5*inch, height=2.8*inch))
        story.append(Spacer(1, 0.15*inch))

    story.append(section_header("📋  Full Analysis", S))
    story.append(Spacer(1, 0.12*inch))
    render_body(analysis_result, story, S)

    story.append(Spacer(1, 0.2*inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB')))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "This report is AI-generated for informational purposes only. "
        "Not financial advice. Always consult a qualified financial advisor.",
        S['disclaimer']))

    doc.build(story)
    print(f"\n✅ PDF saved -> {fn}")
    return fn


def generate_comparison_pdf(results: dict, user_currency: str = 'USD',
                             prefetched_data: dict = None):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    tickers = list(results.keys())
    fn      = f"{output_dir}/{'_vs_'.join(tickers)}_comparison_{ts}.pdf"
    symbol  = get_symbol(user_currency)

    doc = SimpleDocTemplate(fn, pagesize=letter,
                            rightMargin=0.85*inch, leftMargin=0.85*inch,
                            topMargin=0.75*inch,   bottomMargin=0.75*inch)
    S = get_styles()

    metrics = {}
    for t in tickers:
        pre_info = prefetched_data[t]['info'] if prefetched_data and t in prefetched_data else None
        metrics[t] = get_stock_metrics(t, user_currency, prefetched_info=pre_info)

    story = []

    hdr = Table([[
        Paragraph("Stock Comparison", S['title']),
        Paragraph(f"{' vs '.join(tickers)} | {user_currency}\n{datetime.now().strftime('%b %d, %Y')}", S['subtitle']),
    ]], colWidths=[4*inch, 2.7*inch])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,0), (-1,-1), 18),
        ('LEFTPADDING',   (0,0), (-1,-1), 18),
        ('RIGHTPADDING',  (0,0), (-1,-1), 18),
        ('ALIGN',         (1,0), (1,0),   'RIGHT'),
        ('ROUNDEDCORNERS', [8,8,8,8]),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.2*inch))

    story.append(section_header("📋  Summary at a Glance", S))
    story.append(Spacer(1, 0.12*inch))

    col_w   = 6.5 / (len(tickers) + 1)
    hdr_row = ['Metric'] + tickers
    rows = [
        ['Price']          + [f"{pdf_symbol(symbol)}{metrics[t].get('price',0):,.2f}" for t in tickers],
        ['Market Cap']     + [metrics[t].get('market_cap_fmt','N/A')                   for t in tickers],
        ['P/E Ratio']      + [f"{metrics[t].get('pe_ratio',0):.1f}"                   for t in tickers],
        ['Profit Margin']  + [f"{metrics[t].get('profit_margin',0):.1f}%"             for t in tickers],
        ['Revenue']        + [metrics[t].get('revenue_fmt','N/A')                     for t in tickers],
        ['Recommendation'] + [extract_recommendation(results[t])[0]                   for t in tickers],
        ['Risk Level']     + [extract_risk(results[t])[0]                             for t in tickers],
    ]

    tbl_styles = [
        ('BACKGROUND',     (0,0), (-1,0),  DARK),
        ('TEXTCOLOR',      (0,0), (-1,0),  WHITE),
        ('FONTNAME',       (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0,0), (-1,-1), 10),
        ('ALIGN',          (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',           (0,0), (-1,-1), 0.4, colors.HexColor('#E5E7EB')),
        ('FONTNAME',       (0,1), (0,-1),  'Helvetica-Bold'),
        ('TEXTCOLOR',      (0,1), (0,-1),  DARK),
        ('TOPPADDING',     (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT, WHITE]),
    ]
    rec_row  = len(rows)
    risk_row = len(rows) + 1
    for i, t in enumerate(tickers):
        _, rc = extract_recommendation(results[t])
        _, rk = extract_risk(results[t])
        col = i + 1
        tbl_styles += [
            ('BACKGROUND', (col, rec_row),  (col, rec_row),  rc),
            ('TEXTCOLOR',  (col, rec_row),  (col, rec_row),  WHITE),
            ('BACKGROUND', (col, risk_row), (col, risk_row), rk),
            ('TEXTCOLOR',  (col, risk_row), (col, risk_row), WHITE),
        ]

    sum_tbl = Table([hdr_row] + rows, colWidths=[col_w*inch]*(len(tickers)+1))
    sum_tbl.setStyle(TableStyle(tbl_styles))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.25*inch))

    story.append(section_header("📊  Visual Comparison", S))
    story.append(Spacer(1, 0.15*inch))
    chart_c = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(tickers))]

    def add_chart(field, title, ylabel):
        vals = [metrics[t].get(field, 0) or 0 for t in tickers]
        if any(v > 0 for v in vals):
            buf = bar_chart_img(tickers, vals, title, ylabel, chart_c)
            story.append(Image(buf, width=6*inch, height=2.7*inch))
            story.append(Spacer(1, 0.15*inch))

    add_chart('pe_ratio',      'P/E Ratio Comparison',                      'P/E Ratio')
    add_chart('profit_margin', 'Profit Margin Comparison (%)',               'Profit Margin (%)')
    add_chart('revenue_b',     f'Revenue Comparison ({user_currency} B)',    f'Revenue ({pdf_symbol(symbol)}B)')
    add_chart('market_cap_b',  f'Market Cap Comparison ({user_currency} B)', f'Market Cap ({pdf_symbol(symbol)}B)')

    story.append(section_header("📈  12 Month Price History", S))
    story.append(Spacer(1, 0.15*inch))
    for ticker in tickers:
        pre_hist = prefetched_data[ticker]['hist'] if prefetched_data and ticker in prefetched_data else None
        hist_buf = price_history_chart(ticker, user_currency=user_currency, prefetched_hist=pre_hist)
        if hist_buf:
            story.append(Image(hist_buf, width=6.5*inch, height=2.8*inch))
            story.append(Spacer(1, 0.12*inch))

    story.append(section_header("📄  Detailed Analysis Per Stock", S))
    story.append(Spacer(1, 0.15*inch))

    for ticker, analysis in results.items():
        rec, rc  = extract_recommendation(analysis)
        risk, rk = extract_risk(analysis)

        pill = Table([[
            Paragraph(ticker, ParagraphStyle('TP', parent=S['title'], fontSize=18)),
            Paragraph(f"{rec}  |  {risk} RISK",
                      ParagraphStyle('PP', parent=S['subtitle'], fontSize=11, alignment=TA_RIGHT)),
        ]], colWidths=[3.5*inch, 3*inch])
        pill.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), ACCENT),
            ('TOPPADDING',    (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING',   (0,0), (-1,-1), 14),
            ('RIGHTPADDING',  (0,0), (-1,-1), 14),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [6,6,6,6]),
        ]))
        story.append(pill)
        story.append(Spacer(1, 0.1*inch))
        render_body(analysis, story, S)
        story.append(Spacer(1, 0.15*inch))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor('#E5E7EB')))
        story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(
        "This report is AI-generated for informational purposes only. "
        "Not financial advice. Always consult a qualified financial advisor.",
        S['disclaimer']))

    doc.build(story)
    print(f"\n✅ Comparison PDF saved -> {fn}")
    return fn
