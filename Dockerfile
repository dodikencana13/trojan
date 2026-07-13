FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the RPC server
COPY trojan_rpc_sqlite.py .

# Hugging Face Spaces uses port 7860 by default
ENV PORT=7860

# Start the server on 0.0.0.0:7860
CMD ["python", "trojan_rpc_sqlite.py"]
