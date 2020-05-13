FEATURES = [
    {"label": "Bid Size", "value": "bidSz"},
    {"label": "Bid Price", "value": "bidPx"},
    {"label": "Ask Size", "value": "askSz"},
    {"label": "Ask Price", "value": "askPx"},
    {"label": "Spread", "value": "spread"},
]

TIME_RANGES = {
    'hour': [0, 24],
    'minute': [0, 60],
    'second': [0, 60],
    'microsecond': [0, 1000000]
}

COLUMNS_FOR_DATA_TABLE = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'direction']
