FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# build-essential for compiling libs
# libgomp1 for PyTorch/Transformers optimizations
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
# Note: Installing torch/transformers in a slim image can be heavy.
# For production, consider using a pre-built ML image (e.g., pytorch/pytorch).
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables (Defaults, override in docker-compose)
ENV PYTHONPATH=/app
ENV MOCK_MODE=True

# Expose ports (Streamlit)
EXPOSE 8501

# Command to run the bot by default
CMD ["python", "-m", "src.bot"]
