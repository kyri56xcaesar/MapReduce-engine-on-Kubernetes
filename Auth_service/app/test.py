from Crypto.PublicKey import RSA
import jwt

key = RSA.generate(2048)
PRIVATE_KEY = key.export_key()
PUBLIC_KEY = key.publickey().export_key()
print(PRIVATE_KEY)
print(PUBLIC_KEY)

payload = {
    'username': 'admin',
}

token = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
print(token)
