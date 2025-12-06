import json
import base64
import hmac
import hashlib

def encode_urlsafe(raw_bytes):
    encoded = base64.urlsafe_b64encode(raw_bytes)
    return encoded.rstrip(b'=')

# JWT header
jwt_header = {"alg": "HS256", "typ": "JWT"}
encoded_header = encode_urlsafe(json.dumps(jwt_header).encode())

# JWT body
body = {
    "username": "admin",
    "role": "admin",
    "exp": 1893456000
}
encoded_body = encode_urlsafe(json.dumps(body).encode())

# Secret used for signing
key = b"str!k3b4nk@1009%sup3r!s3cr37"

# Generate signature
msg = encoded_header + b"." + encoded_body
signature = hmac.new(key, msg, hashlib.sha256).digest()
encoded_signature = encode_urlsafe(signature)

# Construct final JWT
token = f"{encoded_header.decode()}.{encoded_body.decode()}.{encoded_signature.decode()}"

print(token)
