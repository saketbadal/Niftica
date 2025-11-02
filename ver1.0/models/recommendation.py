# models/recommendation.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Recommendation:
    symbol: str
    timestamp: datetime
    recommendation: str  # BUY/SELL/HOLD
    confidence: float
    option_type: Optional[str] = None  # CE/PE
    strike_suggestion: Optional[str] = None
    reasoning: str = ""
    risk_level: str = "medium"
    target_levels: List[float] = None
    stop_loss: Optional[float] = None
    market_snapshot: dict = None
    
    def to_telegram_message(self):
        """Convert recommendation to formatted Telegram message"""
        # Emoji based on recommendation
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        }
        emoji = emoji_map.get(self.recommendation, '⚪')
        
        message = f"{emoji} <b>{self.recommendation} Signal for {self.symbol}</b> {emoji}\n\n"
        message += f"📊 <b>Confidence:</b> {self.confidence:.1%}\n"
        
        if self.option_type and self.strike_suggestion:
            message += f"📌 <b>Suggestion:</b> {self.strike_suggestion} {self.option_type}\n"
        
        message += f"⚠️ <b>Risk Level:</b> {self.risk_level.upper()}\n\n"
        
        message += f"💭 <b>Reasoning:</b>\n{self.reasoning}\n\n"
        
        if self.target_levels:
            message += f"🎯 <b>Targets:</b> {', '.join(map(str, self.target_levels))}\n"
        
        if self.stop_loss:
            message += f"🛑 <b>Stop Loss:</b> {self.stop_loss}\n"
        
        message += f"\n⏰ <b>Time:</b> {self.timestamp.strftime('%d-%b-%Y %H:%M:%S')} IST"
        
        return message
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'option_type': self.option_type,
            'strike_suggestion': self.strike_suggestion,
            'reasoning': self.reasoning,
            'risk_level': self.risk_level,
            'target_levels': self.target_levels,
            'stop_loss': self.stop_loss,
            'market_snapshot': self.market_snapshot
        }