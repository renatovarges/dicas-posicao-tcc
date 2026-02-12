"""
Script executado como SUBPROCESS para capturar screenshot via Playwright.
Isso evita conflito de event loop asyncio com o Streamlit.

Uso: python pw_capture.py <arquivo_html> <arquivo_png_saida> <scale> <largura_base>
"""
import sys
import os
from playwright.sync_api import sync_playwright

def main():
    if len(sys.argv) < 5:
        print("Uso: python pw_capture.py <html_path> <output_png_path> <scale> <base_width>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    scale = float(sys.argv[3])
    base_width = int(sys.argv[4])
    
    file_url = "file:///" + html_path.replace("\\", "/")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            viewport={"width": base_width + 80, "height": 800},
            device_scale_factor=scale,
        )
        
        page = context.new_page()
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        # Esconder controles de UI
        page.evaluate("""
            () => {
                const el = document.getElementById('ui-controls');
                if (el) el.style.display = 'none';
            }
        """)
        
        # Capturar o elemento #capture (report-container)
        element = page.locator("#capture")
        
        if element.count() == 0:
            element = page.locator(".report-container")
        
        if element.count() > 0:
            element.screenshot(path=output_path, type="png")
        else:
            page.screenshot(path=output_path, type="png", full_page=True)
        
        browser.close()
    
    print("OK")

if __name__ == "__main__":
    main()
