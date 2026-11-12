# Prepared for a single-GPU Runpod Pod behind HTTPS; not a Runpod serverless handler.
FROM pytorch/pytorch:2.11.0-cuda12.8-cudnn9-runtime
WORKDIR /app
COPY requirements-api.txt /app/
RUN pip install --no-cache-dir -r requirements-api.txt transformers==5.19.0 peft==0.21.2 bitsandbytes==0.50.2 accelerate==1.15.0 tokenizers==0.23.3 mistral-common==1.13.1 jinja2==3.1.6 sentence-transformers chromadb openai sentencepiece protobuf tiktoken==0.14.0
COPY backend /app/backend
COPY config /app/config
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
