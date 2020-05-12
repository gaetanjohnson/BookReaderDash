

HOVER_TEMPLATES = {
    'depth_figure': "<b>Click for volume details</b><br><br>" +
        "Time: %{x}<br>" +
        "Trade Price: %{y}<br>" +
        "Cum Volume: %{z}" +
        "<extra></extra>",
    'trade_volume_detail':
        "Trade Price: %{x}<br>" +
        "Volume: %{y}" +
        "<extra></extra>",
    'line':
        "Time: %{x}<br>" +
        "Price: %{y}"
}

EMPTY_TEMPLATE = dict(
                name="draft watermark",
                text="Click on figure for volume details",
                opacity=0.1,
                font=dict(color="black", size=50),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )