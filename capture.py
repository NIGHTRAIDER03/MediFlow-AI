from playwright.sync_api import sync_playwright
import time
import os

os.makedirs("docs/screenshots", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    
    print("Navigating to login page...")
    page.goto("http://localhost:5173/login")
    
    # Login
    print("Logging in...")
    page.click("button:has-text('Sign In')")
    
    # Dashboard
    print("Waiting for Dashboard...")
    page.wait_for_selector("text=Recent Activity", timeout=10000)
    time.sleep(2)  # Let animations finish
    page.screenshot(path="docs/screenshots/dashboard.png")
    print("Saved dashboard.png")
    
    # AI Copilot
    print("Navigating to AI Copilot...")
    page.click("text=Log Interaction")
    page.wait_for_selector("text=AI Copilot", timeout=10000)
    page.click("text=AI Copilot")
    time.sleep(1)
    page.fill("textarea", "Met with Dr. Sarah. She is interested in Cardiolex. Please send her the clinical trial data.")
    page.screenshot(path="docs/screenshots/copilot.png")
    print("Saved copilot.png")
    
    # Submit interaction and wait for timeline
    print("Submitting interaction...")
    page.keyboard.press("Enter")
    time.sleep(5) # wait for AI to process
    
    # Timeline
    print("Navigating to Timeline...")
    page.goto("http://localhost:5173/history")
    page.wait_for_selector("text=Interaction History", timeout=10000)
    time.sleep(2)
    page.screenshot(path="docs/screenshots/timeline.png")
    print("Saved timeline.png")
    
    # Analytics / Meeting Brief
    print("Navigating to Analytics...")
    page.goto("http://localhost:5173/analytics")
    page.wait_for_selector("text=Analytics", timeout=10000)
    time.sleep(2)
    page.screenshot(path="docs/screenshots/brief.png")
    print("Saved brief.png")
    
    browser.close()
    print("Done!")
