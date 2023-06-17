def xor_encrypt_decrypt(data, key=42):
    encrypted = ''.join(chr(ord(c) ^ key) for c in data)
    return encrypted
