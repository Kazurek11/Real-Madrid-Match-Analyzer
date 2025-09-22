# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# docs/source/conf.py
import os
import sys
# Dodaj główny folder projektu do ścieżki (dla importów `from src...`)
sys.path.insert(0, os.path.abspath('../..'))
# Dodaj folder src do ścieżki (dla plików .rst wygenerowanych przez apidoc)
sys.path.insert(0, os.path.abspath('../../src'))
project = 'REAL MADRID MATCH ANALYZER - DOCS'
copyright = '2025, Kacper Figura'
author = 'Kacper Figura'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Najważniejsze! Importuje moduły i pobiera docstringi.
    'sphinx.ext.napoleon',     # Pozwala Sphinxowi rozumieć docstringi w stylu Google i NumPy.
    'sphinx.ext.viewcode',     # Dodaje linki do podświetlonego kodu źródłowego.
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['../../src/RM/RM_preparation_files.py']

language = 'pl'


html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
