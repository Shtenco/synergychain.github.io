#!/usr/bin/env python3
import base64
import hashlib
import io
import tarfile
from pathlib import Path

PAYLOAD_SHA256 = '5a0168d66556ec799a4425ceffd670b7f97e97ec7b3e756c5bc7b4e1dfa0f2d9'


def apply_wallet_v2(app: Path) -> None:
    root = Path(__file__).resolve().parent
    encoded = ''.join(p.read_text(encoding='ascii').strip() for p in sorted(root.glob('wallet-payload.part*')))
    data = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(data).hexdigest() != PAYLOAD_SHA256:
        raise RuntimeError('Wallet payload checksum mismatch')
    www = app / 'src/main/assets/www'
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        archive.extractall(www, filter='data')
    print('WALLET_V2_OK evm_networks=20 watch_networks=13 builtin_tokens=48 provider=FREE2EX,BYNEX,NBRB')
