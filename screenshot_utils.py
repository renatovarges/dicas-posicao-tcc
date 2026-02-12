"""
Utilitário de Screenshot Server-Side usando Playwright (via subprocess).

O Playwright roda em um processo separado para evitar conflito de
event loop asyncio com o Streamlit.
"""
import os
import sys
import tempfile
import subprocess

def capture_html_to_image(html_content, scale=3.0, base_width=1200):
    """
    Renderiza o HTML e captura um screenshot de alta resolução.
    
    Args:
        html_content: String HTML completa.
        scale: Fator de escala (2.0 = Retina, 3.0 = 3x, 4.0 = 4K).
        base_width: Largura base do container em CSS pixels.
    Returns:
        bytes: Conteúdo PNG ou None em caso de erro.
    """
    temp_html = None
    temp_png = None
    
    try:
        # 1. Salvar HTML em arquivo temporário
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.html', encoding='utf-8'
        ) as f:
            f.write(html_content)
            temp_html = f.name
        
        # 2. Definir caminho de saída PNG
        temp_png = temp_html.replace('.html', '.png')
        
        # 3. Chamar o script Playwright como SUBPROCESS
        # Isso evita o conflito asyncio com Streamlit
        script_dir = os.path.dirname(os.path.abspath(__file__))
        capture_script = os.path.join(script_dir, "pw_capture.py")
        
        result = subprocess.run(
            [sys.executable, capture_script, temp_html, temp_png, str(scale), str(base_width)],
            capture_output=True,
            text=True,
            timeout=60  # Timeout de 60 segundos
        )
        
        if result.returncode != 0:
            print(f"Erro no subprocess Playwright: {result.stderr}")
            return None
        
        # 4. Ler o PNG gerado
        if os.path.exists(temp_png):
            with open(temp_png, 'rb') as f:
                return f.read()
        else:
            print("Arquivo PNG não foi gerado.")
            return None
            
    except subprocess.TimeoutExpired:
        print("Timeout: Playwright demorou mais de 60 segundos.")
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None
    finally:
        # Limpar temporários
        for path in [temp_html, temp_png]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
