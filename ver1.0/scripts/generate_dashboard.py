# scripts/generate_dashboard.py
#!/usr/bin/env python3
"""
Generate performance dashboard HTML report
"""
import pandas as pd
from datetime import datetime, timedelta
from agents.feedback_loop import FeedbackLoop
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_dashboard():
    """Generate performance dashboard"""
    feedback = FeedbackLoop()
    
    # Get metrics for different periods
    daily_metrics = feedback.get_performance_metrics(days=1)
    weekly_metrics = feedback.get_performance_metrics(days=7)
    monthly_metrics = feedback.get_performance_metrics(days=30)
    
    # Create dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Accuracy Trend', 'Recommendation Distribution', 
                       'Confidence vs Accuracy', 'Daily Performance'),
        specs=[[{'type': 'scatter'}, {'type': 'pie'}],
               [{'type': 'scatter'}, {'type': 'bar'}]]
    )
    
    # Add plots (simplified example)
    # Plot 1: Accuracy Trend
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    accuracy_values = [0.6 + 0.1 * np.random.randn() for _ in range(30)]
    
    fig.add_trace(
        go.Scatter(x=dates, y=accuracy_values, name='Accuracy'),
        row=1, col=1
    )
    
    # Plot 2: Recommendation Distribution
    if monthly_metrics:
        labels = ['BUY', 'SELL', 'HOLD']
        values = [
            monthly_metrics['by_recommendation']['BUY']['total'],
            monthly_metrics['by_recommendation']['SELL']['total'],
            monthly_metrics['by_recommendation']['HOLD']['total']
        ]
        
        fig.add_trace(
            go.Pie(labels=labels, values=values),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title_text="Nifty Options AI Recommender - Performance Dashboard",
        showlegend=False,
        height=800
    )
    
    # Save to HTML
    filename = f"dashboard_{datetime.now().strftime('%Y%m%d')}.html"
    fig.write_html(filename)
    print(f"Dashboard saved to: {filename}")
    
    return filename

if __name__ == "__main__":
    generate_dashboard()