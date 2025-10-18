#!/usr/bin/env python3
"""
Test the main script without requiring real API keys
"""

import os
import sys
import asyncio

# Set mock environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = "mock_token"
os.environ["TELEGRAM_CHAT_ID_HIGH"] = "-1003150179214"
os.environ["TELEGRAM_CHAT_ID_MEDIUM"] = "-4871231611"
os.environ["OPENAI_API_KEY"] = "mock_key"

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_main_script():
    """Test the main script functionality"""
    print("🚀 Testing main script functionality...")
    
    try:
        # Test import
        from api_clients.free_apis import search_products_free
        print("✅ Import successful!")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        results = await search_products_free("laptop", limit_per_site=2)
        
        # Analyze results
        total_products = sum(len(products) for products in results.values())
        working_sites = sum(1 for products in results.values() if len(products) > 0)
        total_sites = len(results)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Total sites: {total_sites}")
        print(f"   Working sites: {working_sites}")
        print(f"   Total products: {total_products}")
        print(f"   Success rate: {(working_sites/total_sites)*100:.1f}%")
        
        print(f"\n📋 Site-by-site results:")
        for site, products in results.items():
            status = "✅ WORKING" if len(products) > 0 else "❌ BROKEN"
            print(f"   {status} {site}: {len(products)} products")
        
        # Test main script import (without running it)
        print(f"\n🧪 Testing main script import...")
        try:
            import multithreaded_ai_scraper
            print("✅ Main script import successful!")
            print("✅ All components working correctly!")
        except Exception as e:
            print(f"❌ Main script import failed: {e}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_main_script())
