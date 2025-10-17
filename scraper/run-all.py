#!/usr/bin/env python3
"""
Main orchestrator for the price monitoring system.
Executes scrapers, analyzes data with AI, and sends notifications.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.app.scraper_base import ScraperOrchestrator
from scraper.ai.analyzer import AIAnalyzer
from scraper.notifier.telegram_bot import TelegramNotifier

async def main():
    """Main execution function"""
    print(f"[{datetime.now()}] Starting price monitoring system...")
    
    try:
        # Initialize components
        orchestrator = ScraperOrchestrator()
        ai_analyzer = AIAnalyzer()
        telegram_notifier = TelegramNotifier()
        
        # Run scrapers
        print("Running scrapers...")
        scraped_data = await orchestrator.run_all_scrapers()
        
        if not scraped_data:
            print("No data scraped. Exiting.")
            return
        
        # Analyze with AI
        print("Analyzing data with AI...")
        analyzed_deals = await ai_analyzer.analyze_deals(scraped_data)
        
        # Send notifications
        if analyzed_deals:
            print(f"Sending {len(analyzed_deals)} notifications...")
            await telegram_notifier.send_deals(analyzed_deals)
        
        print(f"[{datetime.now()}] Price monitoring completed successfully!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
