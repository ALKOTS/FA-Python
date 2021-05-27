import hashlib
passwd='1234'
key = hashlib.md5(passwd.encode() + b'salt').hexdigest()
print(key)