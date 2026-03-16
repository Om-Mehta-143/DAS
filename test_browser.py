import asyncio
from core.browser import BrowserManager

async def test_browser():
    print("Initializing Browser Manager...")
    browser = BrowserManager(headless=True)
    
    try:
        print("\n[Test 1] Simple Navigation:")
        content = await browser.get_page_content("https://example.com")
        if "Example Domain" in content:
            print("  > Result: SUCCESS (Page loaded)")
        else:
            print("  > Result: FAILED (Content mismatch)")
            
    except Exception as e:
        print(f"  > Result: FAILED ({str(e)})")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_browser())
