import os
import base64

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py') and f != 'fix_base64.py':
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                content = fh.read().strip()
            try:
                decoded = base64.b64decode(content, validate=True)
                if decoded and b'\x00' not in decoded:
                    with open(path, 'wb') as fh:
                        fh.write(decoded)
                    print(f'Fixed: {path}')
            except Exception:
                pass
