FEATURES = [
    {"label": "Bid Size", "value": "bidSz"},
    {"label": "Bid Price", "value": "bidPx"},
    {"label": "Ask Size", "value": "askSz"},
    {"label": "Ask Price", "value": "askPx"},
    {"label": "Spread", "value": "spread"},
]

TIME_RANGES = {
    'hour': {'min': 0, 'max': 24},
    'minute': {'min': 0, 'max': 60},
    'second': {'min': 0, 'max': 60},
    'microsecond': {'min': 0, 'max': 1000000}
}

COLUMNS_FOR_DATA_TABLE = ['time', 'date', 'bidSz', 'bidPx', 'askPx', 'askSz', 'tradePx', 'tradeSz', 'direction']

APP_INPUTS = ['file_path', 'date', 'msuk', 'use_cache', 'hour', 'minute', 'second', 'micros']