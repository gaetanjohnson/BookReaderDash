import plotly.graph_objects as go

from settings import HOVER_TEMPLATES, EMPTY_TEMPLATE
from utils import generate_colors
import functools
import time


def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def figure_generator(func):
    """Generates a figure from traces, layout and xaxis layout"""
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        fig = go.Figure()
        traces, layout, x_axes = func(*args, **kwargs)
        fig.add_traces(traces)
        template = layout.pop('template', 'plotly_white')
        fig.update_layout(template=template, **layout)
        fig.update_xaxes(rangeslider_visible=False, **x_axes)
        return fig

    return wrapper_decorator


class FigureGenerator:

    @classmethod
    @figure_generator
    def figure(cls, relevant_df, feature):
        traces = go.Scatter(x=relevant_df['datetime'], y=relevant_df[feature], mode='lines', name=feature, line_width=2)
        return [traces], dict(), dict()

    # TODO: generate lines for different levels (not just best)
    @classmethod
    @figure_generator
    def size_imbalance_figure(cls, relevant_df):
        traces = go.Scatter(x=relevant_df['datetime'], y=relevant_df['size_imbalance'], mode='lines',
                            name='size_imbalance', line_width=2)
        layout = dict(title_text="Size Imbalance on best Bid/Ask", )
        return [traces], layout, dict()

    @classmethod
    @figure_generator
    def bid_ask_figure(cls, relevant_df):
        dt = relevant_df["datetime"]
        traces = [
            go.Scatter(x=dt, y=relevant_df["bidPx"], name='Bid', mode='lines', line_color='green', line_width=2),
            go.Scatter(x=dt, y=relevant_df["askPx"], name='Ask', fill='tonexty', mode='lines', line_color='red',
                       line_width=2, yaxis='y'),
            go.Scatter(x=dt, y=relevant_df["bidSz"], name='Bid Volume', mode='lines', line_color='green', yaxis='y2',
                       line_width=2),
            go.Scatter(x=dt, y=relevant_df["askSz"], name='Ask Volume', mode='lines', line_color='red', yaxis='y2',
                       line_width=2),
        ]

        layout = dict(title_text="Bid Ask and Volumes", legend_orientation="h", hovermode='x unified',
                      yaxis=dict(domain=[0.3, 1]), yaxis2=dict(domain=[0, 0.2]))
        return traces, layout, dict()

    @classmethod
    @figure_generator
    def depth_cum_figure(cls, df):
        try:
            data = df[['datetime', 'cumulative_trade_volume', 'tradePx']].set_index(['tradePx', 'datetime']).unstack()
        except:
            return [], dict(), dict()
        x = df['datetime'].drop_duplicates()
        y = data.index
        z = data.values
        best_df = df.drop_duplicates('datetime')
        bid, ask = best_df['bidPx'], best_df['askPx']

        traces = [
            go.Heatmap(z=z, x=x, y=y, hovertemplate=HOVER_TEMPLATES['depth_figure']),
            go.Scatter(x=x, y=bid, name='Bid', mode='lines', line_color='green', hovertemplate=HOVER_TEMPLATES['line'],
                       line_width=2),
            go.Scatter(x=x, y=ask, name='Ask', mode='lines', line_color='red', hovertemplate=HOVER_TEMPLATES['line'],
                       line_width=2)
        ]

        layout = dict(title_text="Cumulative volumes per price")
        x_axes = dict(showspikes=True, spikemode="across")

        return traces, layout, x_axes

    @classmethod
    @figure_generator
    def depth_non_cum_figure(cls, df, scale):
        try:
            data = df[['datetime', 'tradeSz', 'tradePx']].set_index(['tradePx', 'datetime']).unstack()
        # TODO: show different layout when data is just top of the book. For now, just return empty Figures
        except:
            return [], dict(), dict()
        x = df['datetime'].drop_duplicates()
        y = data.index
        z = data.values
        colorscale = generate_colors(scale)
        best_df = df.drop_duplicates('datetime')
        bid, ask = best_df['bidPx'], best_df['askPx']

        traces = [
            go.Heatmap(z=z, x=x, y=y, hovertemplate=HOVER_TEMPLATES['depth_figure'], colorscale=colorscale),
            go.Scatter(x=x, y=bid, name='Bid', mode='lines', line_color='green', hovertemplate=HOVER_TEMPLATES['line'],
                       line_width=2),
            go.Scatter(x=x, y=ask, name='Ask', mode='lines', line_color='red', hovertemplate=HOVER_TEMPLATES['line'],
                       line_width=2)
        ]

        layout = dict(title_text="Volumes per price")
        x_axes = dict(showspikes=True, spikemode="across")
        return traces, layout, x_axes

    @classmethod
    @figure_generator
    def trade_volume_detail(cls, ctx, df):
        datetime = handle_ctx(ctx.triggered)
        if not datetime:
            draft_template = go.layout.Template()
            draft_template.layout.annotations = [EMPTY_TEMPLATE]
            return [], dict(template=draft_template), dict()
        else:
            filtered_df = df[df['datetime'] == datetime][['direction', 'tradeSz', 'tradePx']]
            ask, bid = filtered_df[filtered_df['direction'] == 'Sell'], filtered_df[filtered_df['direction'] == 'Buy']
            ask_prices, ask_sizes = ask['tradePx'], ask['tradeSz']
            bid_prices, bid_sizes = bid['tradePx'], bid['tradeSz']

            traces = [
                go.Bar(name='Ask', x=ask_prices, y=ask_sizes, marker_color='red',
                       hovertemplate=HOVER_TEMPLATES['trade_volume_detail']),
                go.Bar(name='Bid', x=bid_prices, y=bid_sizes, marker_color='green',
                       hovertemplate=HOVER_TEMPLATES['trade_volume_detail'])
            ]

            layout = dict(title=f'Trade Volumes for: {datetime}')

            return traces, layout, dict()

def handle_ctx(ctx):
    """
    Tries to get a datetime in click or hover Data. If not found, return None
    """
    try:
        datetime = ctx[0]['value']['points'][0].get('x', None)
        return datetime
    except:
        return None
