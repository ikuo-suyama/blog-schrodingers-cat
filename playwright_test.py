#!/usr/bin/env python3
import asyncio
import subprocess
import time
import os
import signal
from playwright.async_api import async_playwright

SERVER_PORT = 8080
SERVER_URL = f"http://localhost:{SERVER_PORT}"

async def main():
    # Start the HTTP server as a subprocess
    print("Starting HTTP server...")
    server_process = subprocess.Popen(
        ["python", "server.py", str(SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    # Give the server time to start
    time.sleep(2)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to the server root
            print(f"Navigating to {SERVER_URL}...")
            await page.goto(SERVER_URL)
            
            # Take a screenshot
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            await page.screenshot(path=f"{screenshots_dir}/homepage.png")
            print(f"Screenshot saved to {screenshots_dir}/homepage.png")
            
            # Print the page title
            title = await page.title()
            print(f"Page title: {title}")
            
            # Wait for user input to continue
            input("Press Enter to continue browsing or Ctrl+C to exit...\n")
            
            # You can add more test cases here, such as:
            # - Navigate to specific pages
            # - Check if elements exist
            # - Test if assets are loaded correctly
            
            await browser.close()
    
    except KeyboardInterrupt:
        print("Test interrupted by user")
    
    finally:
        # Stop the server
        print("Stopping HTTP server...")
        if server_process:
            server_process.send_signal(signal.SIGINT)
            server_process.wait()
            stdout, stderr = server_process.communicate()
            if stdout:
                print("Server stdout:", stdout)
            if stderr:
                print("Server stderr:", stderr)
        print("Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 