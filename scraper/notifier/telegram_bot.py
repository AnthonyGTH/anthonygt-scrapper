"""
Telegram bot client for sending price monitoring notifications.
"""

import os
import asyncio
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging

class TelegramNotifier:
    """Telegram bot client for notifications"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.logger = logging.getLogger("telegram.notifier")
        
    async def send_deals(self, deals: List[Dict[str, Any]]) -> bool:
        """Send deal notifications to Telegram"""
        if not deals:
            return True
        
        self.logger.info(f"Sending {len(deals)} deals to Telegram...")
        
        for deal in deals:
            try:
                await self._send_single_deal(deal)
                # Rate limiting - wait between messages
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to send deal notification: {e}")
                continue
        
        return True
    
    async def _send_single_deal(self, deal: Dict[str, Any]) -> bool:
        """Send a single deal notification"""
        try:
            message = self._format_deal_message(deal)
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Successfully sent deal notification for {deal.get('product', {}).get('name', 'Unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def _format_deal_message(self, deal: Dict[str, Any]) -> str:
        """Format deal data into Telegram message"""
        product = deal.get("product", {})
        
        message = f"🔥 *Oferta Detectada*\n\n"
        message += f"📱 *{product.get('name', 'Producto')}*\n"
        message += f"🏪 {product.get('site', 'Sitio')}\n"
        message += f"💰 Precio: ${product.get('price', 0):,.2f}\n"
        
        if product.get('original_price'):
            message += f"💸 Precio original: ${product.get('original_price', 0):,.2f}\n"
            message += f"📉 Descuento: {product.get('discount_percentage', 0):.1f}%\n"
        
        message += f"✅ Disponibilidad: {product.get('availability', 'N/A')}\n"
        message += f"🔗 [Ver producto]({product.get('url', '#')})\n\n"
        message += f"🤖 Confianza: {deal.get('confidence_score', 0):.1%}\n"
        message += f"💭 {deal.get('reasoning', 'Análisis automático')}"
        
        return message
