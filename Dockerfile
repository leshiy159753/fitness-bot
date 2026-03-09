FROM python:3.11-slim
WORKDIR /app
RUN pip install aiogram==3.7.0 anthropic python-dotenv aiohttp
COPY . .
RUN python3 -c "
import os, base64
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                content = fh.read().strip()
            try:
                decoded = base64.b64decode(content)
                if decoded and b'\x00' not in decoded:
                    with open(path, 'wb') as fh:
                        fh.write(decoded)
                    print(f'Fixed: {path}')
            except Exception:
                pass
"
CMD ["python", "main.py"]