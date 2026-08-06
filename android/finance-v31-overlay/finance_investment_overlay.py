#!/usr/bin/env python3
import base64
import hashlib
import io
import tarfile
from pathlib import Path

PAYLOAD_SHA256 = '80ad790ddcd3c2405deacf9773eff5ddb25b914d52e55458925033d31469eef6'


def _payload() -> bytes:
    root = Path(__file__).resolve().parent
    encoded = ''.join(p.read_text(encoding='ascii').strip() for p in sorted(root.glob('investment-payload.part*')))
    data = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(data).hexdigest() != PAYLOAD_SHA256:
        raise RuntimeError('Investment payload checksum mismatch')
    return data


def apply_investment_overlay(www: Path) -> None:
    index = www / 'index.html'
    if not index.exists():
        raise RuntimeError(f'index.html not found: {index}')
    with tarfile.open(fileobj=io.BytesIO(_payload()), mode='r:gz') as tf:
        tf.extractall(www, filter='data')
    html = index.read_text(encoding='utf-8')
    html = html.replace('<link rel="stylesheet" href="css/investments-v4.css">', '')
    html = html.replace('<script src="js/investments-v4.js"></script>', '')
    html = html.replace('</head>', '  <link rel="stylesheet" href="css/investments-v4.css">\n</head>', 1)
    html = html.replace('</body>', '  <script src="js/investments-v4.js"></script>\n</body>', 1)
    index.write_text(html, encoding='utf-8')
    print('INVESTMENT_TRACKER_V4_OK providers=MOEX_ISS,KASE_API,EODHD assets=stocks,bonds,etf,funds')
