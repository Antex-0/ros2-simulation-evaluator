import os
import sys

# Point to /workspace (two levels up from docs/source)
sys.path.insert(0, os.path.abspath('../..'))

project = 'ROS2 Evaluator'
copyright = '2025, Developer'
author = 'Developer'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
]

html_theme = 'sphinx_rtd_theme'
