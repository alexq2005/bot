# Professional IOL Trading Bot v2.0 - Installation Guide

## Quick Install

```bash
# 1. Install main dependencies
pip install -r requirements.txt

# 2. Install pandas-ta from GitHub (not available in PyPI)
pip install git+https://github.com/twopirllc/pandas-ta.git

# 3. Verify installation
python -c "import pandas_ta; print('pandas-ta installed successfully')"
```

## Alternative: Install All at Once

```bash
pip install -r requirements.txt && pip install git+https://github.com/twopirllc/pandas-ta.git
```

## Docker Installation

If using Docker, the Dockerfile will handle all installations automatically:

```bash
docker-compose up -d
```

## Troubleshooting

### pandas-ta not found

```bash
pip install git+https://github.com/twopirllc/pandas-ta.git
```

### PyTorch installation issues

For CPU-only (smaller download):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Transformers/HuggingFace issues

```bash
pip install transformers --upgrade
```

## Verify Installation

```bash
python -c "
import pandas
import numpy
import torch
import transformers
import stable_baselines3
import gymnasium
import streamlit
import pandas_ta
print('All dependencies installed successfully!')
"
```
