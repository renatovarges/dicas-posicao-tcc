#!/bin/bash
# Script de pós-instalação para Streamlit Cloud
# Instala os browsers do Playwright

playwright install chromium
playwright install-deps chromium
