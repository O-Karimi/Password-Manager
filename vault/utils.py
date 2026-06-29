import secrets
import string

PASSPHRASE_WORDS = [
    "apple", "breeze", "cloud", "dance", "eagle", "flame", "grape", "heart",
    "island", "jungle", "koala", "lemon", "mango", "ninja", "ocean", "panda",
    "quest", "river", "storm", "tiger", "umbra", "valley", "window", "xenon",
    "yellow", "zebra", "brave", "clever", "happy", "lucky", "smart", "wild",
    "cosmic", "dragon", "forest", "galaxy", "hidden", "lunar", "magic", "mystic",
    "planet", "secret", "shadow", "silent", "solar", "spirit", "stellar", "sunset"
]

def generate_advanced_password(
    length=16, use_upper=True, use_lower=True, use_numbers=True, 
    use_symbols=True, custom_symbols="", exclude_ambiguous=False, 
    is_passphrase=False, word_count=4, separator="-"
):
    if is_passphrase:
        words = [secrets.choice(PASSPHRASE_WORDS) for _ in range(word_count)]
        return separator.join(words)

    chars = ""
    if use_lower: 
        chars += string.ascii_lowercase
    if use_upper: 
        chars += string.ascii_uppercase
    if use_numbers: 
        chars += string.digits
    
    if use_symbols:
        chars += custom_symbols if custom_symbols else "!@#$%^&*()-_=+"

    if exclude_ambiguous:
        ambiguous = "l1IO0"
        chars = "".join(c for c in chars if c not in ambiguous)

    if not chars:
        chars = string.ascii_lowercase

    secure_password = ''.join(secrets.choice(chars) for _ in range(length))
    return secure_password