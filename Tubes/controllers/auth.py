# controllers/auth.py

# Data akun
accounts = {
    "admin": {"password": "admin123", "role": "admin"},
    "vincent": {"password": "user123", "role": "user"},
    "faza": {"password": "faza123", "role": "user"},
    "feysha": {"password": "feysha123", "role": "user"},
    "hafshah": {"password": "hafshah123", "role": "user"}
}

def check_login(username, password):
    """
    Mengembalikan:
    - 'admin' jika login admin
    - 'user' jika login user
    - None jika gagal
    """
    if username in accounts:
        if password == accounts[username]["password"]:
            return accounts[username]["role"]
    return None
