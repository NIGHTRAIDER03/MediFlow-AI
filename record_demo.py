from playwright.sync_api import sync_playwright
import time
import os

print("Waiting for backend to initialize...")
time.sleep(15)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir="docs/",
        record_video_size={"width": 1280, "height": 800}
    )
    page = context.new_page()
    
    # 1. Login
    print("Navigating to login...")
    page.goto("http://localhost:5173/login")
    page.wait_for_selector("button:has-text('Sign In')", timeout=10000)
    time.sleep(1)
    page.click("button:has-text('Sign In')")
    
    # 2. Dashboard
    print("Waiting for Dashboard...")
    page.wait_for_selector("text=Recent Activity", timeout=15000)
    time.sleep(2)  # Show the dashboard for 2 seconds
    
    # 3. Navigate to AI Copilot
    print("Navigating to AI Copilot...")
    page.click("text=Log Interaction")
    page.wait_for_selector("text=AI Copilot", timeout=10000)
    page.click("text=AI Copilot")
    time.sleep(1)
    
    # 4. Type the interaction text slowly
    print("Typing interaction...")
    text_to_type = "Met with Dr. Sarah. She is interested in Cardiolex. Please send her the clinical trial data."
    page.focus("textarea")
    for char in text_to_type:
        page.keyboard.type(char)
        time.sleep(0.03)
    
    time.sleep(0.5)
    page.keyboard.press("Enter")
    
    # 5. Wait for the ACTUAL AI response to appear (not a fixed sleep!)
    print("Waiting for AI response...")
    try:
        # Wait for the "MediFlow AI is thinking..." spinner to disappear
        # and the actual response text to appear
        page.wait_for_selector(".whitespace-pre-wrap", timeout=60000)
        print("AI response received!")
        time.sleep(3)  # Show the response for 3 seconds
    except Exception as e:
        print(f"Timeout waiting for AI response: {e}")
        time.sleep(3)
    
    # 6. Navigate to History page
    print("Navigating to History...")
    page.click("text=History")
    page.wait_for_selector("text=Interaction History", timeout=10000)
    time.sleep(2)  # Show history for 2 seconds
    
    # Done - close and save
    video_path = page.video.path()
    context.close()
    browser.close()
    
    # Rename the video
    if os.path.exists("docs/demo.webm"):
        os.remove("docs/demo.webm")
    os.rename(video_path, "docs/demo.webm")
    print(f"Video saved to docs/demo.webm")
