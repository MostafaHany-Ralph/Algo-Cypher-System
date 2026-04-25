from customtkinter import *
import io
import random
import uuid
from tkinter import filedialog
import re
import string
import numpy as np
from sympy import symbols, diff, integrate, sympify
from collections import deque
import pyodbc
import subprocess
# Set the appearance mode    DATABASE
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

# ΔCipher functions
x = symbols('x')

def encrypt_obfuscated(text):
    encrypted = ''
    for i, c in enumerate(text):
        ascii_val = ord(c)
        power = i + 1
        f = ascii_val * x**power
        f_prime = diff(f, x)
        part = str(f_prime).replace('**', '^').replace(' ', '')
        if power == 2 and part.endswith('x'):
            part += '^1'
        encrypted += part
    display_encrypted = encrypted.replace('*', '').replace('^', '')
    return display_encrypted

def decrypt_obfuscated(obf_text):
    decrypted = ''
    pos = 0
    if len(obf_text) == 0:
        return ''
    try:
        if obf_text[0] == '1' and len(obf_text) >= 3:
            num = obf_text[:3]
            if not num.isdigit():
                raise ValueError("Expected 3-digit number for first character")
            ascii_val = int(num)
            pos = 3
        else:
            if len(obf_text) >= 2:
                num = obf_text[:2]
                if not num.isdigit():
                    raise ValueError("Expected 2-digit number for first character")
                ascii_val = int(num)
                pos = 2
            else:
                raise ValueError("Insufficient characters for first character")
        if not (0 <= ascii_val <= 255):
            raise ValueError(f"ASCII value {ascii_val} out of valid range")
        decrypted += chr(ascii_val)
    except Exception as e:
        raise ValueError(f"Failed to parse first character: {str(e)}")
    parts = []
    current_part = ''
    power_index = 1
    while pos < len(obf_text):
        if obf_text[pos] == 'x':
            if current_part:
                parts.append(current_part)
            parts.append('x')
            current_part = ''
            pos += 1
            if pos < len(obf_text) and obf_text[pos].isdigit():
                if power_index == 1:
                    if obf_text[pos] != '1':
                        raise ValueError(f"Expected exponent '1' for second letter at position {pos}")
                    parts.append('1')
                    pos += 1
                else:
                    expected_power = str(power_index)
                    if pos + len(expected_power) > len(obf_text) or obf_text[pos:pos+len(expected_power)] != expected_power:
                        raise ValueError(f"Expected exponent '{expected_power}' at position {pos}")
                    parts.append(expected_power)
                    pos += len(expected_power)
                power_index += 1
        else:
            current_part += obf_text[pos]
            pos += 1
    if current_part:
        parts.append(current_part)
    i = 0
    part_position = 1
    while i < len(parts):
        if parts[i] == 'x' and i+1 < len(parts) and parts[i+1].isdigit():
            if i-1 < 0 or not parts[i-1].isdigit():
                raise ValueError(f"Missing or invalid coefficient before 'x' at part position {part_position}")
            coefficient = int(parts[i-1])
            power = int(parts[i+1])
            integrated_coeff = coefficient // (power + 1)
            if not (0 <= integrated_coeff <= 255):
                raise ValueError(f"Computed ASCII value {integrated_coeff} out of valid range at part position {part_position}")
            decrypted += chr(integrated_coeff)
            i += 2
            part_position += 1
        else:
            i += 1
    return decrypted

# Egyptian Hieroglyph Cipher functions
english_to_hieroglyph = {
    'a': '𓄿', 'b': '𓃀', 'c': '𓈜', 'd': '𓂧', 'e': '𓇋', 'f': '𓆑', 'g': '𓎼', 'h': '𓉔',
    'i': '𓇑', 'j': '𓆓', 'k': '𓎡', 'l': '𓃭', 'm': '𓅓', 'n': '𓈖', 'o': '𓂝', 'p': '𓊪',
    'q': '𓈎', 'r': '𓂋', 's': '𓋴', 't': '𓏏', 'u': '𓅱', 'v': '𓆰', 'w': '𓏲', 'x': '𓐍',
    'y': '𓇳', 'z': '𓊃', ' ': ' '
}
hieroglyph_to_english = {v: k for k, v in english_to_hieroglyph.items()}

def fibonacci(n):
    if n <= 0:
        return 0
    fib = [1, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[n-1] if n <= len(fib) else fib[-1]

def caesar_fibonacci_encrypt(text):
    result = []
    for p, char in enumerate(text.lower(), 1):
        if char.isalpha():
            a = ord(char) - ord('a')
            shifted = (a + fibonacci(p)) % 26
            result.append(chr(shifted + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def caesar_fibonacci_decrypt(text):
    result = []
    for p, char in enumerate(text.lower(), 1):
        if char.isalpha():
            e = ord(char) - ord('a')
            shifted = (e - fibonacci(p)) % 26
            result.append(chr(shifted + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def hieroglyph_encrypt(text):
    fib_encrypted = caesar_fibonacci_encrypt(text)
    result = []
    for char in fib_encrypted:
        result.append(english_to_hieroglyph.get(char, '?'))
    return ''.join(result)

def hieroglyph_decrypt(hieroglyphs):
    result = []
    i = 0
    while i < len(hieroglyphs):
        if i+1 < len(hieroglyphs):
            double_glyph = hieroglyphs[i] + hieroglyphs[i+1]
            if double_glyph in hieroglyph_to_english:
                result.append(hieroglyph_to_english[double_glyph])
                i += 2
                continue
        result.append(hieroglyph_to_english.get(hieroglyphs[i], '?'))
        i += 1
    return caesar_fibonacci_decrypt(''.join(result))

# X-OR Cipher function
def xor_operation(text, key):
    result = ''
    for char in text:
        result += chr(ord(char) ^ key)
    return result


def caesar_cipher(text: str, key: int, mode: str) -> dict:
    try:
        if not isinstance(text, str):
            raise ValueError("Text must be a string.")
        if not text.strip():
            raise ValueError("Text cannot be empty.")
        if not isinstance(key, int):
            raise ValueError("Key must be an integer.")
        if mode.lower() not in ("encrypt", "decrypt"):
            raise ValueError("Mode must be either 'encrypt' or 'decrypt'.")
        if len(text) > 1000:
            raise ValueError("Text is too long. Maximum allowed is 1000 characters.")
        key = key % 26
        if mode.lower() == "decrypt":
            key = -key
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base + key) % 26 + base
                result.append(chr(shifted))
            else:
                result.append(char)
        return {
            "cipher_name": "Caesar Cipher",
            "mode": mode.lower(),
            "cipher_text": ''.join(result)
        }
    except Exception as e:
        return {"error": str(e)}

def encrypt_rail_fence(text, key):
    try:
        text = text.upper().replace(" ", "")
        if not text:
            raise ValueError("Text cannot be empty.")
        rail = [['\n' for _ in range(len(text))] for _ in range(key)]
        dir_down = False
        row, col = 0, 0
        for char in text:
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False
            rail[row][col] = char
            col += 1
            if dir_down:
                row += 1
            else:
                row -= 1
        result = ''
        for i in range(key):
            for j in range(len(text)):
                if rail[i][j] != '\n':
                    result += rail[i][j]
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def decrypt_rail_fence(cipher, key):
    try:
        cipher = cipher.upper().replace(" ", "")
        if not cipher:
            raise ValueError("Ciphertext cannot be empty.")
        rail = [['\n' for _ in range(len(cipher))] for _ in range(key)]
        dir_down = None
        row, col = 0, 0
        for _ in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False
            rail[row][col] = '*'
            col += 1
            if dir_down:
                row += 1
            else:
                row -= 1
        index = 0
        for i in range(key):
            for j in range(len(cipher)):
                if rail[i][j] == '*' and index < len(cipher):
                    rail[i][j] = cipher[index]
                    index += 1
        result = ''
        row, col = 0, 0
        for _ in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False
            if rail[row][col] != '\n':
                result += rail[row][col]
            col += 1
            if dir_down:
                row += 1
            else:
                row -= 1
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def rot13(text):
    try:
        result = ""
        for char in text:
            if 'a' <= char.lower() <= 'z':
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + 13) % 26 + base)
            else:
                result += char
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def reverse_cipher(text, operation):
    try:
        if operation not in ['encrypt', 'decrypt']:
            raise ValueError("Invalid operation")
        return text[::-1]
    except Exception as e:
        return f"Error: {str(e)}"

def substitution_cipher(text, operation, key, preserve_case=False):
    try:
        if operation not in ['encrypt', 'decrypt']:
            raise ValueError("Operation must be 'encrypt' or 'decrypt'")
        if not key:
            raise ValueError("Key must be provided (26 unique letters)")
        if len(key) != 26 or not all(k in string.ascii_letters for k in key.values()):
            raise ValueError("Key must contain exactly 26 unique letters")
        reversed_key = {v.lower(): k.lower() for k, v in key.items()} if operation == 'decrypt' else {}
        result = []
        for char in text:
            is_upper = char.isupper()
            c = char.lower()
            if c in string.ascii_lowercase:
                if operation == 'encrypt':
                    mapped_char = key.get(c, c)
                else:
                    mapped_char = reversed_key.get(c, c)
                if preserve_case and is_upper:
                    mapped_char = mapped_char.upper()
                result.append(mapped_char)
            else:
                result.append(char)
        return ''.join(result)
    except Exception as e:
        return f"Error: {str(e)}"

def hill_cipher(text, operation, key=None):
    try:
        if key is None:
            key = np.array([[5, 8], [17, 3]])
        text = text.lower().replace(" ", "")
        if not text:
            raise ValueError("Text cannot be empty.")
        n = len(key)
        if len(text) % n != 0:
            text += 'x' * (n - len(text) % n)
        numbers = [ord(c) - ord('a') for c in text]
        chunks = [numbers[i:i+n] for i in range(0, len(numbers), n)]
        result = []
        if operation == 'encrypt':
            for chunk in chunks:
                encrypted = np.dot(key, chunk) % 26
                result.extend(encrypted)
        elif operation == 'decrypt':
            det = int(np.round(np.linalg.det(key)))
            try:
                det_inv = pow(det, -1, 26)
            except ValueError:
                return "Error: Cannot decrypt with this key (no modular inverse exists)"
            key_inv = np.round(det_inv * np.linalg.inv(key) * np.linalg.det(key)) % 26
            key_inv = key_inv.astype(int)
            for chunk in chunks:
                decrypted = np.dot(key_inv, chunk) % 26
                result.extend(decrypted)
        else:
            return "Error: Invalid operation"
        return ''.join([chr(num + ord('a')) for num in result])
    except Exception as e:
        return f"Error: {str(e)}"

def generate_key(text, key):
    try:
        key = list(key)
        if len(key) == len(text):
            return "".join(key)
        else:
            for i in range(len(text) - len(key)):
                key.append(key[i % len(key)])
        return "".join(key)
    except Exception as e:
        return f"Error: {str(e)}"

def vigenere_encrypt(text, key):
    try:
        cipher_text = ''
        for i in range(len(text)):
            x = (ord(text[i]) + ord(key[i])) % 26
            x += ord('A')
            cipher_text += chr(x)
        return cipher_text
    except Exception as e:
        return f"Error: {str(e)}"

def vigenere_decrypt(cipher_text, key):
    try:
        original_text = ''
        for i in range(len(cipher_text)):
            x = (ord(cipher_text[i]) - ord(key[i]) + 26) % 26
            x += ord('A')
            original_text += chr(x)
        return original_text
    except Exception as e:
        return f"Error: {str(e)}"

def is_valid_vigenere_text(text):
    return bool(text.strip()) and text.replace(" ", "").isalpha()



#efsifushdofiuhsdoiugeosogdsiug         update_content

def prepare_key_matrix(key: str) -> list:
    key = key.upper().replace("J", "I")
    seen = set()
    matrix = []

    for char in key:
        if char.isalpha() and char not in seen:
            seen.add(char)
            matrix.append(char)

    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in seen:
            matrix.append(char)

    return [matrix[i:i+5] for i in range(0, 25, 5)]

def format_plaintext(plaintext: str) -> str:
    plaintext = plaintext.upper().replace("J", "I")
    formatted = ''
    i = 0
    while i < len(plaintext):
        char1 = plaintext[i]
        char2 = plaintext[i+1] if i+1 < len(plaintext) else 'X'
        if char1 == char2:
            formatted += char1 + 'X'
            i += 1
        else:
            formatted += char1 + char2
            i += 2
    if len(formatted) % 2 != 0:
        formatted += 'X'
    return formatted

def find_position(matrix, char):
    for row in range(5):
        for col in range(5):
            if matrix[row][col] == char:
                return row, col

def playfair_cipher(text: str, key: str, mode: str) -> dict:
    if not text.strip():
        raise ValueError("Text cannot be empty.")
    if not key.strip():
        raise ValueError("Key cannot be empty.")
    if not re.fullmatch(r"[A-Za-z\s]+", text):
        raise ValueError("Text must contain only English letters and spaces.")
    if not re.fullmatch(r"[A-Za-z]+", key):
        raise ValueError("Key must contain only English letters.")
    if mode.lower() not in ("encrypt", "decrypt"):
        raise ValueError("Mode must be either 'encrypt' or 'decrypt'.")

    matrix = prepare_key_matrix(key)
    text = text.replace(" ", "")
    text = format_plaintext(text)

    result = ''
    shift = 1 if mode == "encrypt" else -1

    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        row1, col1 = find_position(matrix, a)
        row2, col2 = find_position(matrix, b)

        if row1 == row2:
            result += matrix[row1][(col1 + shift) % 5]
            result += matrix[row2][(col2 + shift) % 5]
        elif col1 == col2:
            result += matrix[(row1 + shift) % 5][col1]
            result += matrix[(row2 + shift) % 5][col2]
        else:
            result += matrix[row1][col2]
            result += matrix[row2][col1]

    return {
        "cipher_name": "Playfair Cipher",
        "mode": mode.lower(),
        "cipher_text": result
    }






def validate_transposition_key(key: str) -> list:
    if not key.strip():
        raise ValueError("Key cannot be empty.")
    # Convert letter-based key to numeric order
    if not key.isdigit():
        if not key.isalpha():
            raise ValueError("Key must contain only letters or digits.")
        # Map letters to their order (e.g., abcz -> [1,2,3,4], iteam -> [3,5,2,1,4])
        unique_chars = sorted(set(key))
        if len(unique_chars) != len(key):
            raise ValueError("Key must not contain repeated characters.")
        key_order = [unique_chars.index(c) + 1 for c in key]
    else:
        key_order = [int(k) for k in key]
        if len(set(key_order)) != len(key_order):
            raise ValueError("Key must not contain repeated digits.")
    return key_order

def prepare_transposition_text(text: str) -> str:
    try:
        if not text.strip():
            raise ValueError("Text cannot be empty.")
        return text.upper().replace(" ", "")
    except Exception as e:
        return f"Error: {str(e)}"

def row_transposition_encrypt(text: str, key: str) -> str:
    try:
        key_order = validate_transposition_key(key)
        if isinstance(key_order, str) and key_order.startswith("Error"):
            raise ValueError(key_order)
        keylen = len(key_order)
        text = prepare_transposition_text(text)
        if isinstance(text, str) and text.startswith("Error"):
            raise ValueError(text)
        columns = {k: "" for k in key_order}
        for i, char in enumerate(text):
            columns[key_order[i % keylen]] += char
        ciphertext = "".join(columns[k] for k in sorted(columns.keys()))
        return ciphertext
    except Exception as e:
        return f"Error: {str(e)}"

def row_transposition_decrypt(ciphertext: str, key: str) -> str:
    try:
        key_order = validate_transposition_key(key)
        if isinstance(key_order, str) and key_order.startswith("Error"):
            raise ValueError(key_order)
        keylen = len(key_order)
        ciphertext = prepare_transposition_text(ciphertext)
        if isinstance(ciphertext, str) and ciphertext.startswith("Error"):
            raise ValueError(ciphertext)
        length = len(ciphertext)
        columns = {k: "" for k in key_order}
        for i in range(length):
            columns[key_order[i % keylen]] += "X"
        column_sizes = {k: len(v) for k, v in columns.items()}
        sorted_keys = sorted(columns.keys())
        cipher_columns = {}
        start = 0
        for k in sorted_keys:
            cipher_columns[k] = ciphertext[start:start + column_sizes[k]]
            start += column_sizes[k]
        decrypted_text = []
        column_pointers = {k: 0 for k in sorted_keys}
        for i in range(length):
            current_key = key_order[i % keylen]
            decrypted_text.append(cipher_columns[current_key][column_pointers[current_key]])
            column_pointers[current_key] += 1
        return "".join(decrypted_text)
    except Exception as e:
        return f"Error: {str(e)}"



def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def affine_encrypt(text, a, b):
    try:
        result = ''
        for char in text:
            if char.isalpha():
                x = ord(char.upper()) - ord('A')
                enc = (a * x + b) % 26
                result += chr(enc + ord('A'))
            else:
                result += char
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def affine_decrypt(cipher_text, a, b):
    try:
        result = ''
        a_inv = mod_inverse(a, 26)
        if a_inv is None:
            raise ValueError("Invalid 'a' key. No modular inverse exists.")
        for char in cipher_text:
            if char.isalpha():
                x = ord(char.upper()) - ord('A')
                dec = (a_inv * (x - b)) % 26
                result += chr(dec + ord('A'))
            else:
                result += char
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def is_valid_affine_text(text):
    return bool(text.strip())

def power(base, expo, m):
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1:
            res = (res * base) % m
        base = (base * base) % m
        expo = expo // 2
    return res

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def modInverse(e, phi):
    g, x, _ = extended_gcd(e, phi)
    if g != 1:
        return -1
    return (x % phi + phi) % phi

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def encrypt_rsa(m, e, n):
    return power(m, e, n)

def decrypt_rsa(c, d, n):
    return power(c, d, n)

DIGITS = "0123456789"
SPECIAL = "!@#%^&*()/ ${}[]=+-_"
C = 26 + len(DIGITS) + len(SPECIAL)

def encryptt(plain: str) -> str:
    n = len(plain)
    occurrences = [[] for _ in range(C)]

    for i, c in enumerate(plain):
        if c.isalpha():
            idx = ord(c.lower()) - ord('a')
            flag = 1 if c.isupper() else 0
            occurrences[idx].append((i, flag))
        elif c.isdigit():
            idx = 26 + int(c)
            occurrences[idx].append((i, 0))
        else:
            pos = SPECIAL.find(c)
            if pos == -1:
                raise ValueError(f"Unsupported character: {c}")
            idx = 26 + len(DIGITS) + pos
            occurrences[idx].append((i, 0))

    tokens = [str(n)]
    for group in occurrences:
        tokens.append(str(len(group)))
        for pos, flag in group:
            tokens.extend([str(pos), str(flag)])

    return '#'.join(tokens)

def decryptt(cipher: str) -> str:
    tokens = cipher.split('#')
    idx = 0
    n = int(tokens[idx])
    idx += 1
    result = [' '] * n

    for cat in range(C):
        freq = int(tokens[idx])
        idx += 1
        for _ in range(freq):
            pos = int(tokens[idx])
            flag = int(tokens[idx + 1])
            idx += 2
            if cat < 26:
                base = chr(ord('a') + cat)
                result[pos] = base.upper() if flag else base
            elif cat < 26 + len(DIGITS):
                result[pos] = DIGITS[cat - 26]
            else:
                result[pos] = SPECIAL[cat - 26 - len(DIGITS)]
    return ''.join(result)

class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def build_tree(text: str) -> TreeNode:
    if not text:
        return None
    root = TreeNode(text[0])
    q = deque([root])
    i = 1
    while i < len(text):
        curr = q.popleft()
        if i < len(text):
            curr.left = TreeNode(text[i])
            q.append(curr.left)
            i += 1
        if i < len(text):
            curr.right = TreeNode(text[i])
            q.append(curr.right)
            i += 1
    return root

def shuffle_tree(node: TreeNode):
    if not node:
        return
    node.left, node.right = node.right, node.left
    shuffle_tree(node.left)
    shuffle_tree(node.right)

def level_order(root: TreeNode) -> str:
    if not root:
        return ""
    q = deque([root])
    result = []
    while q:
        curr = q.popleft()
        result.append(curr.data)
        if curr.left:
            q.append(curr.left)
        if curr.right:
            q.append(curr.right)
    return ''.join(result)

def encrypt(text: str) -> str:
    root = build_tree(text)
    shuffle_tree(root)
    shuffled = level_order(root)
    return encryptt(shuffled)

def decrypt(cipher: str) -> str:
    shuffled = decryptt(cipher)
    root = build_tree(shuffled)
    shuffle_tree(root)
    return level_order(root)

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - CyberVault")
        self.geometry("1024x768")
        self.configure(fg_color="#0A0F23")
        self.bg_canvas = CTkCanvas(self, bg="#0A0F23", highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame = CTkFrame(self, fg_color="#1E2A44", corner_radius=20, border_width=2, border_color="#00FFA3")
        self.frame.pack(pady=100, padx=250, fill="both", expand=True)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.animate_background()
        self.font = CTkFont(family="Orbitron", size=36, weight="bold")
        self.lbl = CTkLabel(self.frame, text="CYBERVAULT", text_color="#00FFA3", font=self.font)
        self.lbl.grid(row=0, column=0, padx=10, pady=30)
        
        # Initialize login frame
        self.init_login_frame()

    def init_login_frame(self):
        self.input_frame = CTkFrame(self.frame, fg_color="#2A3655", corner_radius=15)
        self.input_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.username_frame = CTkFrame(self.input_frame, fg_color="#3B4A6B", corner_radius=10)
        self.username_frame.pack(pady=10, padx=10, fill="x")
        self.user_icon = CTkLabel(self.username_frame, text="👤", font=("Arial", 20), text_color="#00FFA3", width=40)
        self.user_icon.pack(side="left", padx=10)
        self.ent_username = CTkEntry(self.username_frame, placeholder_text="Username", text_color="#FFFFFF", 
                                    fg_color="transparent", placeholder_text_color="#8A9FBF", 
                                    border_width=0, font=("Orbitron", 14), height=50)
        self.ent_username.pack(side="left", fill="x", expand=True, padx=(0,10))

        self.password_frame = CTkFrame(self.input_frame, fg_color="#3B4A6B", corner_radius=10)
        self.password_frame.pack(pady=10, padx=10, fill="x")
        self.pass_icon = CTkLabel(self.password_frame, text="🔒", font=("Arial", 20), text_color="#00FFA3", width=40)
        self.pass_icon.pack(side="left", padx=10)
        self.ent_password = CTkEntry(self.password_frame, placeholder_text="Password", text_color="#FFFFFF", 
                                    show="*", fg_color="transparent", placeholder_text_color="#8A9FBF", 
                                    border_width=0, font=("Orbitron", 14), height=50)
        self.ent_password.pack(side="left", fill="x", expand=True, padx=(0,10))

        self.bt_login = CTkButton(self.frame, text="LOGIN", text_color="#0A0F23", 
                                fg_color="#00FFA3", hover_color="#00CC7A", 
                                corner_radius=15, font=("Orbitron", 16, "bold"), 
                                height=50, command=self.login_command,
                                border_width=2, border_color="#FFFFFF")
        self.bt_login.grid(row=3, column=0, padx=20, pady=30)

        self.bt_signup = CTkButton(self.frame, text="SIGN UP", text_color="#0A0F23", 
                                   fg_color="#00FFA3", hover_color="#00CC7A", 
                                   corner_radius=15, font=("Orbitron", 16, "bold"), 
                                   height=50, command=self.show_signup_frame,
                                   border_width=2, border_color="#FFFFFF")
        self.bt_signup.grid(row=4, column=0, padx=20, pady=10)

    def show_signup_frame(self):
        # Clear the current frame
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.lbl = CTkLabel(self.frame, text="SIGN UP", text_color="#00FFA3", font=self.font)
        self.lbl.grid(row=0, column=0, padx=10, pady=30)

        self.signup_frame = CTkFrame(self.frame, fg_color="#2A3655", corner_radius=15)
        self.signup_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        self.signup_frame.grid_columnconfigure(0, weight=1)

        self.signup_username_frame = CTkFrame(self.signup_frame, fg_color="#3B4A6B", corner_radius=10)
        self.signup_username_frame.pack(pady=10, padx=10, fill="x")
        self.signup_user_icon = CTkLabel(self.signup_username_frame, text="👤", font=("Arial", 20), text_color="#00FFA3", width=40)
        self.signup_user_icon.pack(side="left", padx=10)
        self.ent_signup_username = CTkEntry(self.signup_username_frame, placeholder_text="Username", text_color="#FFFFFF", 
                                             fg_color="transparent", placeholder_text_color="#8A9FBF", 
                                             border_width=0, font=("Orbitron", 14), height=50)
        self.ent_signup_username.pack(side="left", fill="x", expand=True, padx=(0,10))

        self.signup_password_frame = CTkFrame(self.signup_frame, fg_color="#3B4A6B", corner_radius=10)
        self.signup_password_frame.pack(pady=10, padx=10, fill="x")
        self.signup_pass_icon = CTkLabel(self.signup_password_frame, text="🔒", font=("Arial", 20), text_color="#00FFA3", width=40)
        self.signup_pass_icon.pack(side="left", padx=10)
        self.ent_signup_password = CTkEntry(self.signup_password_frame, placeholder_text="Password", text_color="#FFFFFF", 
                                             show="*", fg_color="transparent", placeholder_text_color="#8A9FBF", 
                                             border_width=0, font=("Orbitron", 14), height=50)
        self.ent_signup_password.pack(side="left", fill="x", expand=True, padx=(0,10))

        self.bt_signup_submit = CTkButton(self.frame, text="SIGN UP", text_color="#0A0F23", 
                                           fg_color="#00FFA3", hover_color="#00CC7A", 
                                           corner_radius=15, font=("Orbitron", 16, "bold"), 
                                           height=50, command=self.signup_command,
                                           border_width=2, border_color="#FFFFFF")
        self.bt_signup_submit.grid(row=3, column=0, padx=20, pady=30)

    def signup_command(self):
        username = self.ent_signup_username.get().strip()  # Get and strip whitespace
        password = self.ent_signup_password.get().strip()  # Get and strip whitespace

        # Check if username or password is empty
        if not username or not password:
            self.show_popup("Username and password cannot be empty.")
            return

        user_id = self.create_user(username, password)
        if user_id is not None:
            self.show_popup(f"Sign up successful! Your user ID is: {user_id}. Please log in.")
            self.init_login_frame()  # Go back to login frame
        else:
            self.show_popup("Sign up failed. Username may already exist.")

    def create_user(self, username, password):
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                # Check if the username already exists
                cursor.execute("SELECT * FROM Users WHERE name = ?", (username,))
                if cursor.fetchone() is not None:
                    return None  # Username already exists

                # Insert new user into the Users table
                cursor.execute("INSERT INTO Users (name, password_hash) VALUES (?, ?)", (username, password))
                conn.commit()

                # Retrieve the user_id of the newly created user
                cursor.execute("SELECT TOP 1 user_id FROM Users WHERE name = ? ORDER BY user_id DESC", (username,))
                user_id = cursor.fetchone()[0]
                return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def show_popup(self, message):
        popup = CTkToplevel(self)
        popup.title("INFO")
        popup.configure(fg_color="#1E2A44")
        popup.transient(self)
        popup.grab_set()
        popup_width = 300             #move_to_game_page
        popup_height = 150
        popup.geometry(f"{popup_width}x{popup_height}")
        label = CTkLabel(popup, text=message, text_color="#00FFA3", 
                         font=("Orbitron", 14))
        label.pack(pady=20)
        button = CTkButton(popup, text="OK", text_color="#0A0F23", 
                          fg_color="#00FFA3", hover_color="#00CC7A", 
                          corner_radius=10, font=("Orbitron", 12, "bold"), 
                          height=40, command=popup.destroy)
        button.pack(pady=10)

    def animate_background(self):
        self.bg_canvas.delete("all")
        for _ in range(20):
            x = random.randint(0, 1024)
            y = random.randint(0, 768)
            size = random.randint(2, 5)
            self.bg_canvas.create_oval(x, y, x+size, y+size, fill="#00FFA3", outline="")
        self.after(1000, self.animate_background)

    def animate_input(self, frame, reverse=False):
        if reverse:
            frame.configure(fg_color="#3B4A6B", border_color="#3B4A6B")
        else:
            frame.configure(fg_color="#4A5C8C", border_color="#00FFA3")

    def login_command(self):
        if hasattr(self, 'lbl_error'):
            self.lbl_error.grid_forget()
        if hasattr(self, 'auth_label'):
            self.auth_label.grid_forget()
        if hasattr(self, 'progress'):
            self.progress.grid_forget()
        
        username = self.ent_username.get()
        password = self.ent_password.get()
        
        if authenticate_user(username, password):
            self.auth_label = CTkLabel(self.frame, text="AUTHORIZING...", 
                                      text_color="#00FFA3", font=("Orbitron", 14))
            self.auth_label.grid(row=4, column=0, padx=20, pady=15)
            self.progress = CTkProgressBar(self.frame, width=200, progress_color="#00FFA3", 
                                          fg_color="#2A3655", corner_radius=10)
            self.progress.grid(row=5, column=0, padx=20, pady=15)
            self.progress.set(0)
            self.animate_progress()
        else:
            self.lbl_error = CTkLabel(self.frame, text="ACCESS DENIED", text_color="#FF5555", 
                                     font=("Orbitron", 14))
            self.lbl_error.grid(row=4, column=0, padx=20, pady=15)

    def animate_progress(self):
        current = self.progress.get()
        if current < 1:
            self.progress.set(current + 0.05)
            self.after(100, self.animate_progress)
        else:
            self.setup_main_window()

    def validate_key(self, key: str, cipher: str) -> bool:
        try:
            if cipher == "> CAESAR":
                int(key)
                return True
            elif cipher == "> TRANSPOSITION":
                if not key.strip() or len(set(key)) != len(key):
                    return False
                # Check if all characters are either digits or letters   mustafa
                if not all(c.isdigit() or c.isalpha() for c in key):
                    return False
                return True
            elif cipher == "> PLAYFAIR":
                return bool(key.strip() and re.fullmatch(r"[A-Za-z]+", key))
            elif cipher == "> RAILFENCE":
                try:
                    key_int = int(key)
                    return key_int > 1
                except ValueError:
                    return False
            elif cipher == "> ROT13":
                return True
            elif cipher == "> REVERSE":
                return True
            elif cipher == "> SUBSTITUTION":
                return bool(key.strip() and re.fullmatch(r"[A-Za-z]{26}", key) and len(set(key.lower())) == 26)
            elif cipher == "> HILL":
                if not key:
                    return True
                try:
                    numbers = list(map(int, key.split(',')))
                    return len(numbers) == 4
                except ValueError:
                    return False
            elif cipher == "> VIGENERE":
                return bool(key.strip() and re.fullmatch(r"[A-Za-z]+", key))
            elif cipher == "> AFFINE":
                key = key.strip()
                if not re.match(r"^\[\s*\d+\s*,\s*\d+\s*\]$", key):
                    return False
                try:
                    key_values = key.strip('[]').split(',')
                    a = int(key_values[0].strip())
                    b = int(key_values[1].strip())
                    return gcd(a, 26) == 1
                except (ValueError, IndexError):
                    return False
            elif cipher == "> X-OR":
                if not key.strip() or not key.isdigit():
                    return False
                key_int = int(key)
                return 0 <= key_int <= 255  # Restrict key to ASCII range
            elif cipher == "> RSA":
                try:
                    key_parts = key.split(',')
                    if len(key_parts) != 3:
                        return False
                    p, q, e = map(int, key_parts)
                    return is_prime(p) and is_prime(q) and 1 < e < (p-1)*(q-1)
                except ValueError:
                    return False
            elif cipher == "> ΔCIPHER":
                return True
            elif cipher == "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍":
                return True
            return False
        except Exception:
            return False

    def setup_main_window(self):
        self.main_window = CTkToplevel()
        self.main_window.title("HACKER DASHBOARD")
        self.main_window.geometry("1024x768")
        self.main_window.configure(fg_color="#0A0F23")
        self.withdraw()
        self.main_window.grid_columnconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(1, weight=4)
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_rowconfigure(1, weight=0)
        self.navbar_frame = CTkScrollableFrame(self.main_window, width=200, fg_color="#1E2A44", 
                                       corner_radius=15, border_width=2, border_color="#00FFA3")
        self.navbar_frame.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.navbar_frame.grid_columnconfigure(0, weight=1)
        self.content_frame = CTkFrame(self.main_window, fg_color="#1E2A44", corner_radius=15)
        self.content_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.terminal_frame = CTkFrame(self.main_window, fg_color="#2A3655", corner_radius=15)
        self.terminal_frame.grid(row=1, column=1, sticky="sew", padx=20, pady=20)
        self.terminal_output = CTkTextbox(self.terminal_frame, height=100, fg_color="#1E2A44", 
                                         text_color="#00FFA3", font=("Orbitron", 12), 
                                         corner_radius=10, border_width=2, border_color="#00FFA3")
        self.terminal_output.pack(fill="x", padx=5, pady=5)
        self.update_terminal("SYSTEM BOOT: INITIALIZING HACKER DASHBOARD...")
        self.update_terminal("LOADING CIPHER MODULES...")
        self.ciphers_label = CTkLabel(self.navbar_frame, text="🔐 CIPHERS", text_color="#00FFA3", 
                                     font=CTkFont(family="Orbitron", size=18, weight="bold"))
        self.ciphers_label.grid(row=0, column=0, padx=10, pady=15)
        self.ciphers_frame = CTkFrame(self.navbar_frame, fg_color="#1E2A44")
        self.ciphers_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.ciphers_frame.grid_columnconfigure(0, weight=1)
        cipher_icons = {
            "Caesar": "🔄", "Transposition": "🔀", "Playfair": "🔲", "Railfence": "📏",
            "ROT13": "🔢", "Reverse": "🔙", "Substitution": "🔠", "Hill": "📊",
            "Affine": "📈", "Vigenere": "🔤", "X-OR": "🔣", "RSA": "🔑", "ΔCipher": "",
            "𓆑𓇋𓃀𓅱𓂋𓄿𓐍": "𓇳",
            "Mustafa": "🔀",  
            "Photo Cipher": "🖼️",  # New button for Photo Cipher
            "Game": "🎮"  # Added Game button
        }
        ciphers = ["Caesar", "Transposition", "Playfair", "Railfence", "ROT13", "Reverse", 
                   "Substitution", "Hill", "Affine", "Vigenere", "X-OR", "RSA", "ΔCipher", 
                   "𓆑𓇋𓃀𓅱𓂋𓄿𓐍", "Mustafa", "Photo Cipher", "Game"]  # Added Game to the list
        for i, cipher in enumerate(ciphers):
            btn = CTkButton(self.ciphers_frame, text=f"{cipher_icons[cipher]} {cipher}", 
                   text_color="#0A0F23", fg_color="#00FFA3", hover_color="#00CC7A", 
                   corner_radius=10, height=45, font=("Orbitron", 14, "bold"),
                   command=lambda title=cipher: self.update_content(title),
                   border_width=2, border_color="#FFFFFF")
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
        self.initialize_content()

    def initialize_content(self):
        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)
        self.content_frame.grid_rowconfigure(4, weight=0)
        self.title_label = CTkLabel(self.content_frame, text="", text_color="#00FFA3", 
                                   font=CTkFont(family="Orbitron", size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=20, sticky="n")
        self.flicker_title()
        self.plaintext_frame = CTkFrame(self.content_frame, fg_color="#2A3655", corner_radius=15)
        self.plaintext_label = CTkLabel(self.plaintext_frame, text="📝 PLAINTEXT/ENCRYPTED", 
                                       text_color="#00FFA3", font=CTkFont(family="Orbitron", size=14))
        self.plaintext_label.pack(padx=10, pady=5, anchor="w")
        self.plaintext_text = CTkTextbox(self.plaintext_frame, width=400, height=100, 
                                        fg_color="#1E2A44", border_color="#00FFA3", 
                                        border_width=2, corner_radius=10, text_color="#FFFFFF", 
                                        font=("Orbitron", 12))
        self.plaintext_text.pack(padx=10, pady=5)
        self.result_frame = CTkFrame(self.content_frame, fg_color="#2A3655", corner_radius=15)
        self.result_label = CTkLabel(self.result_frame, text="✅ RESULT", 
                                    text_color="#00FFA3", font=CTkFont(family="Orbitron", size=14))
        self.result_label.pack(padx=10, pady=5, anchor="w")
        self.result_text = CTkTextbox(self.result_frame, width=400, height=100, 
                                     fg_color="#1E2A44", border_color="#00FFA3", 
                                     border_width=2, corner_radius=10, text_color="#FFFFFF", 
                                     font=("Orbitron", 12))
        self.result_text.pack(padx=10, pady=5)
        self.key_frame = CTkFrame(self.content_frame, fg_color="#2A3655", corner_radius=15)
        self.key_label = CTkLabel(self.key_frame, text="🔑 SECRET KEY", 
                                 text_color="#00FFA3", font=CTkFont(family="Orbitron", size=14))
        self.key_label.pack(padx=10, pady=5, anchor="w")
        self.key_text = CTkEntry(self.key_frame, width=400, height=50, 
                                fg_color="#1E2A44", border_color="#00FFA3", border_width=2, 
                                corner_radius=10, text_color="#FFFFFF", font=("Orbitron", 12))
        self.key_text.pack(padx=10, pady=5)
        self.button_frame = CTkFrame(self.content_frame, fg_color="transparent")
        self.upload_btn = CTkButton(self.button_frame, text="📤 UPLOAD", text_color="#0A0F23", 
                                   fg_color="#00FFA3", hover_color="#00CC7A", 
                                   corner_radius=10, height=45, font=("Orbitron", 14, "bold"), 
                                   command=self.upload_file, border_width=2, border_color="#FFFFFF")
        self.upload_btn.pack(side="left", padx=5, pady=10)
        self.download_btn = CTkButton(self.button_frame, text="📥 DOWNLOAD", text_color="#0A0F23", 
                                     fg_color="#00FFA3", hover_color="#00CC7A", 
                                     corner_radius=10, height=45, font=("Orbitron", 14, "bold"), 
                                     command=self.download_file, border_width=2, border_color="#FFFFFF")
        self.download_btn.pack(side="left", padx=5, pady=10)
        self.mode_switch = CTkSwitch(self.button_frame, text="🔓 DECRYPT", text_color="#00FFA3",
                                    font=("Orbitron", 14), progress_color="#00FFA3", 
                                    fg_color="#2A3655", button_color="#00CC7A")
        self.mode_switch.pack(side="left", padx=5, pady=10)
        self.mode_switch.bind("<ButtonRelease-1>", self.update_action_button_text)
        self.action_btn = CTkButton(self.button_frame, text="🔐 ENCRYPT", text_color="#0A0F23", 
                                   fg_color="#00FFA3", hover_color="#00CC7A", 
                                   corner_radius=10, height=45, font=("Orbitron", 14, "bold"), 
                                   command=self.perform_action, border_width=2, border_color="#FFFFFF")
        self.action_btn.pack(side="left", padx=5, pady=10)
        self.plaintext_frame.grid_forget()
        self.result_frame.grid_forget()
        self.key_frame.grid_forget()
        self.button_frame.grid_forget()

    def update_action_button_text(self, event=None):
        if self.mode_switch.get() == 1:
            self.action_btn.configure(text="🔓 DECRYPT")
            self.mode_switch.configure(text="🔐 ENCRYPT")
        else:
            self.action_btn.configure(text="🔐 ENCRYPT")
            self.mode_switch.configure(text="🔓 DECRYPT")
#mustafa
    def flicker_title(self):
        current_text = self.title_label.cget("text")
        if current_text:
            self.title_label.configure(text_color="#00FFA3" if random.random() > 0.2 else "#00CC7A")
            self.after(200, self.flicker_title)

    def update_terminal(self, message):
        self.terminal_output.insert("end", f"[SYS] {message}\n")
        self.terminal_output.see("end")

    def update_content(self, title):
        if not hasattr(self, 'title_label'):
            self.update_terminal("ERROR: Title label not initialized")
            return
        self.title_label.configure(text=f"> {title.upper()}")
        self.plaintext_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.key_text.delete(0, "end")
        self.plaintext_frame.grid(row=1, column=0, pady=15, padx=15, sticky="nsew")
        self.result_frame.grid(row=2, column=0, pady=15, padx=15, sticky="nsew")
        self.key_frame.grid(row=3, column=0, pady=15, padx=15, sticky="nsew")
        self.button_frame.grid(row=4, column=0, pady=15, padx=15, sticky="nsew")
        self.content_frame.update()
        self.update_terminal(f"CIPHER MODULE LOADED: {title.upper()}")
        if title == "RSA":
            self.key_label.configure(text="🔑 P, Q, E")
            self.key_text.configure(placeholder_text="Enter P, Q, E (e.g., 3,7,11)")
            self.action_btn.configure(command=self.perform_rsa_action)
            self.update_terminal("RSA PAGE SETUP COMPLETED")
        elif title == "ΔCIPHER":
            self.key_label.configure(text="🔑 NO KEY REQUIRED")
            self.key_text.configure(placeholder_text="No key required for ΔCipher")
            self.key_text.configure(state="disabled")
            self.update_terminal("ΔCIPHER PAGE SETUP COMPLETED")
        elif title == "𓆑𓇋𓃀𓅱𓂋𓄿𓐍":
            self.key_label.configure(text="🔑 NO KEY REQUIRED")
            self.key_text.configure(placeholder_text="No key required for Hieroglyph Cipher")
            self.key_text.configure(state="disabled")
            self.update_terminal("HIEROGLYPH CIPHER PAGE SETUP COMPLETED")
        elif title == "X-OR":
            self.key_label.configure(text="🔑 INTEGER KEY")
            self.key_text.configure(placeholder_text="Enter a non-negative integer key (0-255)")
            self.key_text.configure(state="normal")
            self.update_terminal("X-OR CIPHER PAGE SETUP COMPLETED")
        elif title == "Mustafa":
            self.key_label.configure(text="🔑 NO KEY REQUIRED")
            self.key_text.configure(placeholder_text="No key required for Mustafa Cipher")
            self.key_text.configure(state="disabled")
            self.action_btn.configure(command=self.perform_action)
            self.update_terminal("MUSTAFA CIPHER PAGE SETUP COMPLETED")
        elif title == "Photo Cipher":
            self.key_label.configure(text="🔑 NO KEY REQUIRED")
            self.key_text.configure(placeholder_text="No key required for Photo Cipher")
            self.key_text.configure(state="disabled")
            self.update_terminal("PHOTO CIPHER PAGE SETUP COMPLETED")
            try:
                # Run the mm.py script  D:\AAST\Term 4\Cyber Security\AlgoCypher
                result = subprocess.run(
                    ["python", r"D:\AAST\Term 4\Cyber Security\AlgoCypher\ImageEncryption.py"],
                    capture_output=True,
                    text=True
                )
                # Log the output or errors in the terminal
                if result.stdout:
                    self.update_terminal(f"PHOTO CIPHER OUTPUT: {result.stdout[:100]}...")
                if result.stderr:
                    self.update_terminal(f"PHOTO CIPHER ERROR: {result.stderr[:100]}...")
                else:
                    self.update_terminal("PHOTO CIPHER EXECUTED SUCCESSFULLY")
            except Exception as e:
                self.update_terminal(f"PHOTO CIPHER FAILED: {str(e)}")
                self.show_popup(f"> ERROR: Failed to run Photo Cipher script: {str(e)}")
        
        elif title == "Game":
            self.key_label.configure(text="🎮 NO KEY REQUIRED")
            self.key_text.configure(placeholder_text="No key required for Game")
            self.key_text.configure(state="disabled")
            self.update_terminal("GAME PAGE SETUP COMPLETED")
            try:
                # Run the game.py script
                result = subprocess.run(
                    ["python", r"D:\AAST\Term 4\Cyber Security\AlgoCypher\Dashboard_game.py"],
                    capture_output=True,
                    text=True
                )
                # Log the output or errors in the terminal
                if result.stdout:
                    self.update_terminal(f"GAME OUTPUT: {result.stdout[:100]}...")
                if result.stderr:
                    self.update_terminal(f"GAME ERROR: {result.stderr[:100]}...")
                else:
                    self.update_terminal("GAME EXECUTED SUCCESSFULLY")
            except Exception as e:
                self.update_terminal(f"GAME FAILED: {str(e)}")
                self.show_popup(f"> ERROR: Failed to run Game script: {str(e)}")
                
        
            
        else:
            self.key_label.configure(text="🔑 SECRET KEY")
            self.key_text.configure(placeholder_text="Enter secret key")
            self.key_text.configure(state="normal")
            self.action_btn.configure(command=self.perform_action)
        




    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                self.plaintext_text.delete("1.0", "end")
                self.plaintext_text.insert("1.0", file_content)
                self.update_terminal(f"FILE UPLOADED: {file_path.split('/')[-1]}")
            except Exception as e:
                self.update_terminal(f"UPLOAD ERROR: {str(e)}")
        else:
            self.update_terminal("UPLOAD CANCELLED")

    def download_file(self):
        content = self.result_text.get("1.0", "end-1c")
        if not content.strip():
            self.update_terminal("DOWNLOAD ERROR: No content in result")
            return
        current_cipher = self.title_label.cget("text").strip('> ').strip().lower().replace(' ', '_')
        file_name = f"{current_cipher}_output.txt"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=file_name
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.update_terminal(f"FILE DOWNLOADED: {file_path.split('/')[-1]}")
            except Exception as e:
                self.update_terminal(f"DOWNLOAD ERROR: {str(e)}")
        else:
            self.update_terminal("DOWNLOAD CANCELLED")

    def perform_action(self):
        if self.mode_switch.get() == 1:
            self.decrypt()
        else:
            self.encrypt()

    def encrypt(self):
        key = self.key_text.get().strip()
        plaintext = self.plaintext_text.get("1.0", "end-1c")
        self.result_text.delete("1.0", "end")
        if not plaintext.strip():
            self.show_popup("> ERROR: Text cannot be empty")
            self.update_terminal("ENCRYPTION FAILED: TEXT CANNOT BE EMPTY")
            return
        current_cipher = self.title_label.cget("text")
        if current_cipher not in ["> ROT13", "> REVERSE", "> ΔCIPHER", "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍", "> MUSTAFA"] and not key:
            self.show_popup("> ERROR: Secret key cannot be empty")
            self.update_terminal("ENCRYPTION FAILED: SECRET KEY CANNOT BE EMPTY")
            return
        if current_cipher != "> ROT13" and current_cipher != "> ΔCIPHER" and current_cipher != "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍" and current_cipher != "> MUSTAFA" and not self.validate_key(key, current_cipher):
            error_msg = {
                "> CAESAR": "> ERROR: Key must be an integer",
                "> TRANSPOSITION": "> ERROR: Key must be numeric with unique digits",
                "> PLAYFAIR": "> ERROR: Key must contain only letters",
                "> RAILFENCE": "> ERROR: Key must be an integer greater than 1",
                "> SUBSTITUTION": "> ERROR: Key must be exactly 26 unique letters",
                "> HILL": "> ERROR: Key must be 4 comma-separated integers",
                "> VIGENERE": "> ERROR: Key must contain only letters",
                "> AFFINE": "> ERROR: Key must be in format [a,b] with a coprime to 26",
                "> RSA": "> ERROR: Key must be in format P,Q,E with P, Q prime",
                "> X-OR": "> ERROR: Key must be a non-negative integer between 0 and 255"
            }.get(current_cipher, "> ERROR: Invalid key")
            self.show_popup(error_msg)
            self.update_terminal(f"ENCRYPTION FAILED: {error_msg[8:].upper()}")
            return
        if current_cipher == "> CAESAR":
            try:
                key_int = int(key)
                result = caesar_cipher(plaintext, key_int, "encrypt")
                self.result_text.insert("1.0", result["cipher_text"])
                self.update_terminal(f"ENCRYPTION COMPLETED: {result['cipher_text'][:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")






        elif current_cipher == "> TRANSPOSITION":
            try:
                result = row_transposition_encrypt(plaintext, key)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        
        
        
        
        
        
        
        elif current_cipher == "> PLAYFAIR":
            try:
                result = playfair_cipher(plaintext, key, "encrypt")
                self.result_text.insert("1.0", result["cipher_text"])
                self.update_terminal(f"ENCRYPTION COMPLETED: {result['cipher_text'][:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> RAILFENCE":
            try:
                key_int = int(key)
                result = encrypt_rail_fence(plaintext, key_int)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> ROT13":
            if key:
                self.show_popup("> ERROR: ROT13 does not require a key")
                self.update_terminal("ENCRYPTION FAILED: ROT13 DOES NOT REQUIRE A KEY")
                return
            result = rot13(plaintext)
            self.result_text.insert("1.0", result)
            self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
        elif current_cipher == "> REVERSE":
            if key:
                self.show_popup("> ERROR: Reverse cipher does not require a key")
                self.update_terminal("ENCRYPTION FAILED: REVERSE DOES NOT REQUIRE A KEY")
                return
            result = reverse_cipher(plaintext, "encrypt")
            self.result_text.insert("1.0", result)
            self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
        elif current_cipher == "> SUBSTITUTION":
            try:
                if not re.fullmatch(r"[A-Za-z]{26}", key):
                    raise ValueError("Key must be exactly 26 letters")
                if len(set(key.lower())) != 26:
                    raise ValueError("Key must contain 26 unique letters")
                cipher_key = {string.ascii_lowercase[i]: key[i].lower() for i in range(26)}
                result = substitution_cipher(plaintext, "encrypt", key=cipher_key, preserve_case=True)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> HILL":
            try:
                cipher_key = None
                if key:
                    numbers = list(map(int, key.split(',')))
                    if len(numbers) != 4:
                        raise ValueError("Key must be 4 comma-separated integers")
                    cipher_key = np.array([numbers[:2], numbers[2:]])
                    det = int(np.round(np.linalg.det(cipher_key)))
                    if det == 0:
                        self.update_terminal("WARNING: Key matrix is not invertible (determinant = 0). Using default key.")
                        cipher_key = None
                result = hill_cipher(plaintext, "encrypt", key=cipher_key)
                if result == "Invalid operation":
                    raise ValueError("Invalid operation")
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> VIGENERE":
            try:
                if not is_valid_vigenere_text(plaintext.replace(" ", "")):
                    raise ValueError("Text must contain only letters")
                full_key = generate_key(plaintext.replace(" ", ""), key.upper())
                result = vigenere_encrypt(plaintext.replace(" ", "").upper(), full_key)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> AFFINE":
            try:
                if not is_valid_affine_text(plaintext):
                    raise ValueError("Text must contain only letters and spaces.")
                key_values = key.strip('[]').split(',')
                a = int(key_values[0].strip())
                b = int(key_values[1].strip())
                result = affine_encrypt(plaintext, a, b)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except (ValueError, IndexError) as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> X-OR":
            try:
                key_int = int(key)
                result = xor_operation(plaintext, key_int)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> ΔCIPHER":
            try:
                if not all(0 <= ord(c) <= 255 for c in plaintext):
                    raise ValueError("Text must contain only ASCII characters")
                result = encrypt_obfuscated(plaintext)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍":
            try:
                if not all(c.isalpha() or c.isspace() for c in plaintext):
                    raise ValueError("Text must contain only letters and spaces")
                result = hieroglyph_encrypt(plaintext)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        elif current_cipher == "> MUSTAFA":
            try:
                result = encrypt(plaintext)  
                self.result_text.insert("1.0", result)
                self.update_terminal(f"ENCRYPTION COMPLETED: {result[:20]}...")
            except Exception as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"ENCRYPTION FAILED: {str(e)}")
        else:
            self.result_text.insert("1.0", f"Encrypted (key: {key}): {plaintext} (placeholder)")
            self.update_terminal("ENCRYPTION COMPLETED: (placeholder)")

    def decrypt(self):
        key = self.key_text.get().strip()
        encrypted_text = self.plaintext_text.get("1.0", "end-1c")
        self.result_text.delete("1.0", "end")
        if not encrypted_text.strip():
            self.show_popup("> ERROR: Text cannot be empty")
            self.update_terminal("DECRYPTION FAILED: TEXT CANNOT BE EMPTY")
            return
        
        current_cipher = self.title_label.cget("text")
        
        # Check for MUSTAFA cipher
        if current_cipher == "> MUSTAFA":
            # Validate the input format
            if not re.match(r'^\d+(#\d+)*$', encrypted_text):
                self.show_popup("> ERROR: Invalid input format")
                self.update_terminal("DECRYPTION FAILED: INVALID INPUT FORMAT")
                return

        if current_cipher not in ["> ROT13", "> REVERSE", "> ΔCIPHER", "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍", "> MUSTAFA"] and not key:
            self.show_popup("> ERROR: Secret key cannot be empty")
            self.update_terminal("DECRYPTION FAILED: SECRET KEY CANNOT BE EMPTY")
            return
        if current_cipher != "> ROT13" and current_cipher != "> ΔCIPHER" and current_cipher != "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍" and current_cipher != "> MUSTAFA" and not self.validate_key(key, current_cipher):
            error_msg = {
                "> CAESAR": "> ERROR: Key must be an integer",
                "> TRANSPOSITION": "> ERROR: Key must be numeric with unique digits",
                "> PLAYFAIR": "> ERROR: Key must contain only letters",
                "> RAILFENCE": "> ERROR: Key must be an integer greater than 1",
                "> SUBSTITUTION": "> ERROR: Key must be exactly 26 unique letters",
                "> HILL": "> ERROR: Key must be 4 comma-separated integers",
                "> VIGENERE": "> ERROR: Key must contain only letters",
                "> AFFINE": "> ERROR: Key must be in format [a,b] with a coprime to 26",
                "> RSA": "> ERROR: Key must be in format P,Q,E with P, Q prime",
                "> X-OR": "> ERROR: Key must be a non-negative integer between 0 and 255"
            }.get(current_cipher, "> ERROR: Invalid key")
            self.show_popup(error_msg)
            self.update_terminal(f"DECRYPTION FAILED: {error_msg[8:].upper()}")
            return
        if current_cipher == "> CAESAR":
            try:
                key_int = int(key)
                result = caesar_cipher(encrypted_text, key_int, "decrypt")
                self.result_text.insert("1.0", result["cipher_text"])
                self.update_terminal(f"DECRYPTION COMPLETED: {result['cipher_text'][:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> TRANSPOSITION":
            try:
                result = row_transposition_decrypt(encrypted_text, key)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> PLAYFAIR":
            try:
                result = playfair_cipher(encrypted_text, key, "decrypt")
                self.result_text.insert("1.0", result["cipher_text"])
                self.update_terminal(f"DECRYPTION COMPLETED: {result['cipher_text'][:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> RAILFENCE":
            try:
                key_int = int(key)
                result = decrypt_rail_fence(encrypted_text, key_int)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> ROT13":
            if key:
                self.show_popup("> ERROR: ROT13 does not require a key")
                self.update_terminal("DECRYPTION FAILED: ROT13 DOES NOT REQUIRE A KEY")
                return
            result = rot13(encrypted_text)
            self.result_text.insert("1.0", result)
            self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
        elif current_cipher == "> REVERSE":
            if key:
                self.show_popup("> ERROR: Reverse cipher does not require a key")
                self.update_terminal("DECRYPTION FAILED: REVERSE DOES NOT REQUIRE A KEY")
                return
            result = reverse_cipher(encrypted_text, "decrypt")
            self.result_text.insert("1.0", result)
            self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
        elif current_cipher == "> SUBSTITUTION":
            try:
                if not re.fullmatch(r"[A-Za-z]{26}", key):
                    raise ValueError("Key must be exactly 26 letters")
                if len(set(key.lower())) != 26:
                    raise ValueError("Key must contain 26 unique letters")
                cipher_key = {string.ascii_lowercase[i]: key[i].lower() for i in range(26)}
                result = substitution_cipher(encrypted_text, "decrypt", key=cipher_key, preserve_case=True)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> HILL":
            try:
                cipher_key = None
                if key:
                    numbers = list(map(int, key.split(',')))
                    if len(numbers) != 4:
                        raise ValueError("Key must be 4 comma-separated integers")
                    cipher_key = np.array([numbers[:2], numbers[2:]])
                    det = int(np.round(np.linalg.det(cipher_key)))
                    if det == 0:
                        self.update_terminal("WARNING: Key matrix is not invertible (determinant = 0). Using default key.")
                        cipher_key = None
                result = hill_cipher(encrypted_text, "decrypt", key=cipher_key)
                if result == "Invalid operation":
                    raise ValueError("Invalid operation")
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> VIGENERE":
            try:
                if not is_valid_vigenere_text(encrypted_text.replace(" ", "")):
                    raise ValueError("Text must contain only letters")
                full_key = generate_key(encrypted_text.replace(" ", ""), key.upper())
                result = vigenere_decrypt(encrypted_text.replace(" ", "").upper(), full_key)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> AFFINE":
            try:
                if not is_valid_affine_text(encrypted_text):
                    raise ValueError("Text must contain only letters and spaces.")
                key_values = key.strip('[]').split(',')
                a = int(key_values[0].strip())
                b = int(key_values[1].strip())
                result = affine_decrypt(encrypted_text, a, b)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except (ValueError, IndexError) as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> X-OR":
            try:
                key_int = int(key)
                result = xor_operation(encrypted_text, key_int)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> ΔCIPHER":
            try:
                result = decrypt_obfuscated(encrypted_text)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> 𓆑𓇋𓃀𓅱𓂋𓄿𓐍":
            try:
                valid_hieroglyphs = set(english_to_hieroglyph.values())
                if not all(c in valid_hieroglyphs for c in encrypted_text):
                    raise ValueError("Input must contain only valid hieroglyphs or spaces")
                result = hieroglyph_decrypt(encrypted_text)
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except ValueError as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        elif current_cipher == "> MUSTAFA":
            try:
                result = decrypt(encrypted_text)  
                self.result_text.insert("1.0", result)
                self.update_terminal(f"DECRYPTION COMPLETED: {result[:20]}...")
            except Exception as e:
                self.result_text.insert("1.0", f"Error: {str(e)}")
                self.update_terminal(f"DECRYPTION FAILED: {str(e)}")
        else:
            self.result_text.insert("1.0", f"Decrypted (key: {key}): {encrypted_text} (placeholder)")
            self.update_terminal("DECRYPTION COMPLETED: (placeholder)")

    def perform_rsa_action(self):
        key = self.key_text.get().strip()
        plaintext = self.plaintext_text.get("1.0", "end-1c")
        self.result_text.delete("1.0", "end")
        if not plaintext.strip():
            self.show_popup("> ERROR: Text cannot be empty")
            self.update_terminal("RSA ACTION FAILED: TEXT CANNOT BE EMPTY")
            return
        if not key:
            self.show_popup("> ERROR: P, Q, E cannot be empty")
            self.update_terminal("RSA ACTION FAILED: P, Q, E CANNOT BE EMPTY")
            return
        try:
            key_parts = key.split(',')
            if len(key_parts) != 3:
                raise ValueError("Key must be in the format P,Q,E")
            p, q = map(int, key_parts[:2])
            if not (is_prime(p) and is_prime(q)):
                raise ValueError("P and Q must be prime numbers.")
            if p == q:
                raise ValueError("P and Q must be distinct prime numbers.")
            n = p * q
            phi = (p - 1) * (q - 1)
            e = int(key_parts[2])
            if not (1 < e < phi):
                raise ValueError(f"E must be in the range 1 < E < {phi}.")
            if gcd(e, phi) != 1:
                raise ValueError(f"E must be coprime with φ(n) = {phi}.")
            d = modInverse(e, phi)
            if d == -1:
                raise ValueError("No modular inverse found for E. Choose a different E.")
            if self.mode_switch.get() == 1:  # Decrypt
                try:
                    c = int(plaintext)
                except ValueError:
                    self.show_popup("> ERROR: Plaintext must be an integer")
                    self.update_terminal("RSA ACTION FAILED: PLAINTEXT MUST BE AN INTEGER")
                    return
                if c < 0:
                    raise ValueError("Ciphertext C must be non-negative.")
                m = decrypt_rsa(c, d, n)
                self.result_text.insert("1.0", str(m))
                self.update_terminal(f"DECRYPTION COMPLETED: {str(m)[:20]}...")
            else:  # Encrypt
                try:
                    m = int(plaintext)
                except ValueError:
                    self.show_popup("> ERROR: Plaintext must be an integer")
                    self.update_terminal("RSA ACTION FAILED: PLAINTEXT MUST BE AN INTEGER")
                    return
                if not (0 < m < n):
                    raise ValueError(f"Message M must be in range 0 < M < {n}.")
                c = encrypt_rsa(m, e, n)
                self.result_text.insert("1.0", str(c))
                self.update_terminal(f"ENCRYPTION COMPLETED: {str(c)[:20]}...")
        except ValueError as ve:
            self.show_popup(f"> ERROR: {str(ve)}")
            self.update_terminal(f"RSA ACTION FAILED: {str(ve)}")
        except Exception as e:
            self.show_popup(f"> ERROR: {str(e)}")
            self.update_terminal(f"RSA ACTION FAILED: {str(e)}")

    def calculate_n_phi(self):
        key = self.key_text.get().strip()
        try:
            key_parts = key.split(',')
            if len(key_parts) < 2:
                raise ValueError("Please enter P and Q.")
            p, q = map(int, key_parts[:2])
            if not (is_prime(p) and is_prime(q)):
                raise ValueError("P and Q must be prime numbers.")
            if p == q:
                raise ValueError("P and Q must be distinct prime numbers.")
            n = p * q
            phi = (p - 1) * (q - 1)
            self.update_terminal(f"n = p * q = {n}")
            self.update_terminal(f"φ(n) = (p - 1) * (q - 1) = {phi}")
            self.show_popup(f"Please input E such that e, φ(n) are co-prime and 1 < e < {phi}.")
        except ValueError as ve:
            self.show_popup(f"> ERROR: {str(ve)}")
            self.update_terminal(f"CALCULATION FAILED: {str(ve)}")
        except Exception as e:
            self.show_popup(f"> ERROR: {str(e)}")
            self.update_terminal(f"CALCULATION FAILED: {str(e)}")

    def load_new_cipher_page(self):
        self.update_content("Mustafa")
#decryptt

# SQL Server connection details
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'Amr\SQLEXPRESS'
DATABASE_NAME = "cyber_user"

# Connection string
connection_string = f"""
    DRIVER={DRIVER_NAME};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

def authenticate_user(username, password):
    try:
        # Establish a connection to the database        self.update_content("Photo Cipher")
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # Query to check if the user exists with the provided password
            cursor.execute("SELECT * FROM Users WHERE name = ? AND password_hash = ?", (username, password))
            user = cursor.fetchone()
            return user is not None  # Return True if user exists, otherwise False
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    app = App()
    app.mainloop()