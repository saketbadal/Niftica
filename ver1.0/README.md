# 🚀 Nifty Options AI Recommendation System

An advanced AI-powered system that analyzes Nifty options using SuperTrend indicators, Open Interest dynamics, market sentiment analysis, and Google's Vertex AI to provide intelligent Buy/Sell/Hold recommendations via Telegram.

## 🌟 Features

- **Dual SuperTrend Analysis**: Monitors both ST(10,1) and ST(10,3) for trend confirmation
- **Open Interest Analytics**: 
  - PCR (Put-Call Ratio) analysis
  - Support/Resistance identification
  - OI buildup detection
- **AI-Powered Recommendations**: Uses Google's Vertex AI for intelligent signal generation
- **Market Sentiment Analysis**: Processes news and market breadth data
- **Real-time Notifications**: Instant Telegram alerts for trading signals
- **Performance Tracking**: Automatic feedback loop for continuous improvement
- **Risk Management**: Dynamic risk assessment based on VIX and market conditions

## 🏗️ Architecture
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Kite Connect │────▶│ Scanner Loop │────▶│ Signal │
│ (Market Data) │ │ (5-min cycle) │ │ Processor │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
┌────────────────────────────┴───┐
│ │
┌─────────▼────────┐ ┌─────────▼────────┐
│ Market Analyst │ │ Sentiment │
│ (OI, VIX, etc) │ │ Analyzer │
└─────────┬────────┘ └─────────┬────────┘
│ │
└────────────┬───────────────────┘
│
┌─────────▼─────────┐
│ Strategy Agent │
│ (Vertex AI) │
└─────────┬─────────┘
│
┌─────────────────┴─────────────────┐
│ │
┌─────────▼─────────┐ ┌──────────▼────────┐
│ Telegram Bot │ │ Feedback Loop │
│ (Notifications) │ │ (Learning) │
└───────────────────┘ └───────────────────┘


## 📋 Prerequisites

- Python 3.10+
- GCP Account with billing enabled
- Kite Connect API subscription
- Telegram Bot created via @BotFather
- Basic knowledge of options trading

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/niftica.git
cd niftica

### 2. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. Configure Credentials
```bash
cp .env .env
# Edit .env with your credentials

### 4. Run Locally
```bash
python app.py





🌐 Deployment to Google Cloud Run
1. Build and Deploy
bash
chmod +x deploy.sh
./deploy.sh
2. Set Telegram Webhook
bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-service-url.run.app/telegram-webhook"
📱 Telegram Commands
/status - System status and today's performance
/performance - Detailed performance metrics
/analysis - Trigger immediate market analysis
/help - Show available commands
🔧 Configuration
SuperTrend Parameters
ST Period 1: 10 (default)
ST Multiplier 1: 1.0
ST Period 2: 10 (default)
ST Multiplier 2: 3.0
AI Parameters
Model: Gemini 1.5 Pro
Temperature: 0.3 (conservative)
Confidence Threshold: 0.6
Risk Management
Signal Cooldown: 30 minutes
Max VIX for Entry: 25
Min ADX for Trend: 20
📊 Performance Metrics
The system tracks:

Win Rate
Average Confidence vs Actual Accuracy
Per-recommendation type performance
Risk-adjusted returns
🔐 Security
All credentials stored in GCP Secret Manager
Telegram webhook authentication
Authorized users whitelist
No actual trading - recommendations only


🧪 Testing
bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
📈 Monitoring
Logs: GCP Cloud Logging
Metrics: Custom dashboard in Cloud Monitoring
Alerts: Configured for system errors and anomalies
🤝 Contributing
Fork the repository
Create feature branch (git checkout -b feature/AmazingFeature)
Commit changes (git commit -m 'Add AmazingFeature')
Push to branch (git push origin feature/AmazingFeature)
Open Pull Request
⚖️ Disclaimer
IMPORTANT: This system provides trading recommendations only. No actual trades are executed. Always do your own research and consult with financial advisors before making trading decisions. Trading in options involves significant risk and can result in substantial losses.

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Zerodha Kite Connect for market data API
Google Cloud Platform for infrastructure
The open-source community for various libraries used
📞 Support
For issues and questions:

Create an issue in GitHub
Contact via Telegram group (if applicable)
Remember: This is a tool to assist in decision making, not a guarantee of profits. Trade responsibly! 📊🎯