import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from .iife import IIFE
import os
from pathlib import Path

key = {}

@IIFE(key)
def __install__(key):
    PrivateKeyFile = Path("./assets/keys/Private.pem")
    PublicKeyFile = Path("./assets/keys/Public.pem")
    if not PrivateKeyFile.exists():
        PrivateKey = RSA.generate(4096)
        PublicKey = PrivateKey.publickey()
        PrivateKeyFile.write_text(PrivateKey.exportKey().decode("utf-8"), 'utf-8')
        PublicKeyFile.write_text(PublicKey.exportKey().decode("utf-8"))
    else:
        PrivateKey = RSA.importKey(PrivateKeyFile.read_text('utf-8'))
        if not PublicKeyFile.exists():
            PublicKey = PrivateKey.publickey()
            PublicKeyFile.write_text(PublicKey.exportKey().decode("utf-8"), 'utf-8')
        else:
            PublicKey = RSA.importKey(PublicKeyFile.read_text('utf-8'))
    key.update({
        "private": PrivateKey,
        "public": PublicKey,
        "__private_text": PrivateKey.exportKey().decode("utf-8"),
        "__public_text": PublicKey.exportKey().decode("utf-8")
    })

def Signature(data: str):
    signer = Signature_pkcs1_v1_5.new(key['private'])
    digest = SHA.new()
    digest.update(data.encode("utf-8"))
    sign = signer.sign(digest)
    return base64.b64encode(sign).decode("utf-8")