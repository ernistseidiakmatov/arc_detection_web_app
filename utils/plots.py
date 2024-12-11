import pandas as pd
import plotly.graph_objs as go
import numpy as np

def generate_signal_plot(signals, signal_length, color):
    t = np.arange(signal_length)
    trace_signal = go.Scatter(x=t, y=signals[:signal_length], mode='lines', name='Signal', line=dict(color=color))
    layout = go.Layout(title=dict(text="Real-time Signal Plot | No Arc was detected" if color == "blue" else "Real-time Signal Plot | Arc was detected",
        font=dict(color="red" if color == "red" else "black")), 
        xaxis_title="Samples", yaxis_title="Amplitude", font=dict(family="Arial"))
    fig = go.Figure(data=[trace_signal], layout=layout)
    graph_json = fig.to_json()
    return graph_json


def generate_lower_plot(timestamps, predictions):
    if not timestamps or not predictions:
        return {"error": "No data available for the specified time range"}

    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Prediction': predictions
    })

    df['Color'] = df['Prediction'].apply(lambda pred: 'red' if pred == 1 else 'blue')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Timestamp'],
        y=df['Prediction'],
        mode='markers',
        marker=dict(color=df['Color']),
        name='Arc Predictions'
    ))

    fig.update_layout(
        title="Arc Predictions Over Time",
        xaxis_title="Timestamp",
        yaxis=dict(
            title="Prediction",
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Non-Arc', 'Arc']
        ),
        xaxis=dict(tickangle=45),
        showlegend=False,
        template='plotly_white'
    )
    return fig.to_json()

    