import hashlib
import secrets

def generate_secure_password(length=12):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    return ''.join(secrets.choice(characters) for _ in range(length))

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def main_with_password_input():
    password1 = input("Введите пароль: ")
    password2 = input("Введите пароль еще раз: ")

    if password1 != password2:
        print("Пароли не совпадают. Попробуйте еще раз.")
        return

    hashed_password = hash_password(password1)
    print(f"Хэш пароля: {hashed_password}\r\nСохрание значение в config.py -> ZPANEL_HASH_PASSWORD")

def main_with_password_generation():
    password = generate_secure_password()
    hashed_password = hash_password(password)
    print(f"Сгенерированный пароль: {password}")
    print(f"Хэш пароля: {hashed_password}")


if __name__ == '__main__':
    print('Enter you pass:')
    password = input()
    if password:
        encrypted_password_hash = hash_password(password)
        print(f'You hashed password {encrypted_password_hash}')
