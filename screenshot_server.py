"""
Screenshot Server usando Selenium + Chrome Headless
Solução robusta que funciona no Streamlit Cloud
"""
import base64
import tempfile
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def capture_html_to_png(html_content: str, scale: float = 3.0, width: int = 1200) -> bytes:
    """
    Captura HTML como PNG usando Selenium + Chrome Headless
    
    Args:
        html_content: String HTML completa
        scale: Escala de resolução (2.0, 3.0, 4.0, etc)
        width: Largura base em pixels (padrão 1200)
    
    Returns:
        bytes: Conteúdo do PNG gerado
    """
    
    # Criar arquivo HTML temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        html_path = f.name
    
    try:
        # Configurar Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument(f'--window-size={width},2000')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--hide-scrollbars')
        
        # Inicializar driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Carregar HTML
            driver.get(f'file://{html_path}')
            
            # Aguardar carregamento completo
            time.sleep(2)
            
            # Obter altura real do conteúdo
            total_height = driver.execute_script("""
                return Math.max(
                    document.body.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.clientHeight,
                    document.documentElement.scrollHeight,
                    document.documentElement.offsetHeight
                );
            """)
            
            # Adicionar buffer de segurança
            total_height += 100
            
            # Ajustar tamanho da janela para capturar tudo
            driver.set_window_size(width, total_height)
            time.sleep(1)
            
            # Capturar screenshot
            png_bytes = driver.get_screenshot_as_png()
            
            # Se scale > 1.0, redimensionar usando PIL
            if scale != 1.0:
                from PIL import Image
                import io
                
                img = Image.open(io.BytesIO(png_bytes))
                new_width = int(img.width * scale)
                new_height = int(img.height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img_resized.save(output, format='PNG', optimize=True)
                png_bytes = output.getvalue()
            
            return png_bytes
            
        finally:
            driver.quit()
            
    finally:
        # Limpar arquivo temporário
        if os.path.exists(html_path):
            os.unlink(html_path)


if __name__ == "__main__":
    # Teste básico
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                margin: 0; 
                padding: 20px; 
                background: white;
                font-family: Arial;
            }
            .box {
                width: 1200px;
                background: #0d3b2a;
                color: white;
                padding: 40px;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Teste de Screenshot</h1>
            <p>Este é um teste do módulo de screenshot.</p>
        </div>
    </body>
    </html>
    """
    
    print("Gerando screenshot de teste...")
    png = capture_html_to_png(test_html, scale=2.0)
    
    with open('/tmp/test_screenshot.png', 'wb') as f:
        f.write(png)
    
    print(f"Screenshot gerado: {len(png)} bytes")
    print("Salvo em: /tmp/test_screenshot.png")
