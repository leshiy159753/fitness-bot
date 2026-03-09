FROM python:3.11-slim
WORKDIR /app
RUN pip install aiogram==3.7.0 anthropic python-dotenv aiohttp
COPY . .
RUN python3 fix_base64.py
CMD ["python", "main.py"]
