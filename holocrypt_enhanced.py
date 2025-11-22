import os
import qrcode
from cryptography.fernet import Fernet
from io import BytesIO
import requests
import json
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import hashlib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import nltk
from nltk.corpus import words
import base64
import urllib.parse
from pypdf import PdfReader, PdfWriter

# Download NLTK data (run once)
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

# Load environment variables
load_dotenv()

# --- Encryption/Decryption ---

def generate_key():
    """Generates a new Fernet key (AES-256)."""
    return Fernet.generate_key()

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypts data using AES-256 (Fernet)."""
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypts data using AES-256 (Fernet)."""
    f = Fernet(key)
    return f.decrypt(encrypted_data)

def generate_access_code_hash(access_code: str) -> str:
    """Generates SHA-256 hash of access code for verification."""
    return hashlib.sha256(access_code.encode()).hexdigest()

# --- Cipher-based Data Shuffling ---

def shuffle_data_by_cipher(data: str, cipher_type: str, cipher_params: dict) -> str:
    """
    Shuffles/randomizes data based on the chosen cipher type.
    
    Args:
        data: Original text data
        cipher_type: Type of cipher (Caesar, Vigenere, Atbash, etc.)
        cipher_params: Cipher parameters (shift, keyword, etc.)
    
    Returns:
        Shuffled/encrypted text
    """
    if cipher_type.lower() == "caesar":
        shift = cipher_params.get('shift', 3)
        return caesar_cipher(data, shift)
    
    elif cipher_type.lower() == "vigenere":
        keyword = cipher_params.get('keyword', 'KEY')
        return vigenere_cipher(data, keyword)
    
    elif cipher_type.lower() == "atbash":
        return atbash_cipher(data)
    
    elif cipher_type.lower() == "substitution":
        key = cipher_params.get('substitution_key', None)
        return substitution_cipher(data, key)
    
    elif cipher_type.lower() == "rail_fence":
        rails = cipher_params.get('rails', 3)
        return rail_fence_cipher(data, rails)
    
    else:
        # Default: simple character shuffling
        chars = list(data)
        random.shuffle(chars)
        return ''.join(chars)

def caesar_cipher(text: str, shift: int) -> str:
    """Caesar cipher encryption."""
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def caesar_decipher(text: str, shift: int) -> str:
    """Caesar cipher decryption."""
    return caesar_cipher(text, -shift)

def vigenere_cipher(text: str, keyword: str) -> str:
    """Vigenere cipher encryption."""
    result = ""
    keyword = keyword.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            shift = ord(keyword[key_index % len(keyword)]) - ord('A')
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            key_index += 1
        else:
            result += char
    return result

def vigenere_decipher(text: str, keyword: str) -> str:
    """Vigenere cipher decryption."""
    result = ""
    keyword = keyword.upper()
    key_index = 0
    
    for char in text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            shift = ord(keyword[key_index % len(keyword)]) - ord('A')
            result += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            key_index += 1
        else:
            result += char
    return result

def atbash_cipher(text: str) -> str:
    """Atbash cipher (reverses alphabet)."""
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += chr(ord('Z') - (ord(char) - ord('A')))
            else:
                result += chr(ord('z') - (ord(char) - ord('a')))
        else:
            result += char
    return result

def substitution_cipher(text: str, key: str = None) -> str:
    """Simple substitution cipher."""
    if key is None:
        alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        key = alphabet.copy()
        random.shuffle(key)
        key = ''.join(key)
    
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += key[ord(char) - ord('A')]
            else:
                result += key[ord(char) - ord('a')].lower()
        else:
            result += char
    return result

def rail_fence_cipher(text: str, rails: int) -> str:
    """Rail fence cipher encryption."""
    if rails == 1:
        return text
    
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    
    for char in text:
        fence[rail].append(char)
        rail += direction
        
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    return ''.join([''.join(row) for row in fence])

def rail_fence_decipher(text: str, rails: int) -> str:
    """Rail fence cipher decryption."""
    if rails == 1:
        return text
    
    fence = [['' for _ in range(len(text))] for _ in range(rails)]
    rail = 0
    direction = 1
    
    # Mark positions
    for i in range(len(text)):
        fence[rail][i] = '*'
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    # Fill fence
    index = 0
    for i in range(rails):
        for j in range(len(text)):
            if fence[i][j] == '*' and index < len(text):
                fence[i][j] = text[index]
                index += 1
    
    # Read fence
    result = []
    rail = 0
    direction = 1
    for i in range(len(text)):
        result.append(fence[rail][i])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    
    return ''.join(result)

def decipher_data(encrypted_text: str, cipher_type: str, cipher_params: dict) -> str:
    """
    Decrypts data based on cipher type and parameters.
    
    Args:
        encrypted_text: Cipher text to decrypt
        cipher_type: Type of cipher used
        cipher_params: Cipher parameters
    
    Returns:
        Decrypted plaintext
    """
    if cipher_type.lower() == "caesar":
        shift = cipher_params.get('shift', 3)
        return caesar_decipher(encrypted_text, shift)
    
    elif cipher_type.lower() == "vigenere":
        keyword = cipher_params.get('keyword', 'KEY')
        return vigenere_decipher(encrypted_text, keyword)
    
    elif cipher_type.lower() == "atbash":
        return atbash_cipher(encrypted_text)  # Atbash is its own inverse
    
    elif cipher_type.lower() == "rail_fence":
        rails = cipher_params.get('rails', 3)
        return rail_fence_decipher(encrypted_text, rails)
    
    else:
        return encrypted_text

# --- NLTK Puzzle Generation ---

def generate_cipher_clue(cipher_type: str, cipher_params: dict) -> str:
    """
    Generates a riddled clue for the cipher type and parameters.
    Receiver must solve the clue to find the decryption key.
    
    Args:
        cipher_type: Type of cipher used
        cipher_params: Cipher parameters
    
    Returns:
        A riddled clue string
    """
    if cipher_type.lower() == "caesar":
        shift = cipher_params.get('shift', 3)
        clues = [
            f"The Roman emperor would shift his letters by {shift} steps forward in battle.",
            f"Julius moved {shift} positions ahead to encode his secret messages.",
            f"Cipher Type: CAESAR | The magic number is: {shift}",
            f"Move each letter {shift} places to the right, like Caesar did in ancient Rome.",
        ]
        return clues[2]  # Most direct clue
    
    elif cipher_type.lower() == "vigenere":
        keyword = cipher_params.get('keyword', 'KEY')
        clues = [
            f"The repeating key that unlocks this cipher is: '{keyword}'",
            f"Cipher Type: VIGENERE | Use the keyword: {keyword}",
            f"A French diplomat's cipher with the secret word: '{keyword}'",
        ]
        return clues[1]  # Clear clue
    
    elif cipher_type.lower() == "atbash":
        clues = [
            "Cipher Type: ATBASH | No parameters needed - just reverse the alphabet!",
            "The Hebrew cipher where A becomes Z, B becomes Y... mirror the alphabet.",
            "First becomes last, last becomes first - the alphabet is reversed.",
        ]
        return clues[0]  # Direct clue
    
    elif cipher_type.lower() == "rail_fence":
        rails = cipher_params.get('rails', 3)
        clues = [
            f"Cipher Type: RAIL FENCE | Number of rails: {rails}",
            f"Write in zigzag across {rails} lines, then read row by row.",
            f"The fence has {rails} horizontal rails - write up and down!",
        ]
        return clues[0]  # Clear clue
    
    elif cipher_type.lower() == "substitution":
        key = cipher_params.get('substitution_key', 'QWERTYUIOPASDFGHJKLZXCVBNM')
        clues = [
            f"Cipher Type: SUBSTITUTION | Custom alphabet key: {key}",
            f"Each letter maps to a different one using: {key}",
        ]
        return clues[0]  # Direct clue
    
    else:
        return f"Cipher Type: {cipher_type.upper()} | Parameters: {cipher_params}"

def generate_puzzle_with_nltk(original_text: str, difficulty: str = "medium") -> str:
    """
    Generates a word puzzle using NLTK when wrong cipher is entered.
    
    Args:
        original_text: The text to puzzleify
        difficulty: easy, medium, or hard
    
    Returns:
        Puzzled text
    """
    try:
        word_list = words.words()
        
        # Split text into words
        text_words = original_text.split()
        puzzled_words = []
        
        for word in text_words:
            if len(word) < 3 or not word.isalpha():
                puzzled_words.append(word)
                continue
            
            if difficulty == "easy":
                # Replace with rhyming-ish word (similar ending)
                similar = [w for w in word_list if len(w) == len(word) and w[-2:] == word[-2:]]
                puzzled_words.append(random.choice(similar) if similar else word)
            
            elif difficulty == "hard":
                # Complete scramble with random words
                similar = [w for w in word_list if len(w) == len(word)]
                puzzled_words.append(random.choice(similar) if similar else word)
            
            else:  # medium
                # Anagram-style shuffling
                chars = list(word)
                random.shuffle(chars)
                puzzled_words.append(''.join(chars))
        
        return ' '.join(puzzled_words)
    
    except Exception as e:
        # Fallback: simple character shuffling
        chars = list(original_text)
        random.shuffle(chars)
        return ''.join(chars)

# --- LSB Steganography (Hide data in QR code images) ---

def hide_data_in_image(qr_image: Image.Image, encrypted_data: bytes, access_code_hash: str) -> Image.Image:
    """
    Hides encrypted data inside a QR code image using LSB steganography.
    Returns a new Image object with hidden data.
    """
    # Convert encrypted data to base64 string for embedding
    import base64
    data_to_hide = base64.b64encode(encrypted_data).decode('utf-8')
    
    # Add access code hash as metadata
    payload = json.dumps({
        'hash': access_code_hash,
        'data': data_to_hide
    })
    
    # Convert QR to RGB if needed
    if qr_image.mode != 'RGB':
        qr_image = qr_image.convert('RGB')
    
    # Embed data using LSB
    img_array = np.array(qr_image)
    
    # Simple LSB implementation: encode payload length + payload
    payload_bytes = payload.encode('utf-8')
    payload_length = len(payload_bytes)
    
    # Store length in first pixels (4 bytes = 32 bits)
    length_bits = format(payload_length, '032b')
    
    flat_array = img_array.flatten()
    
    # Check if image has enough capacity
    max_bytes = len(flat_array) // 8
    if payload_length > max_bytes - 4:
        raise ValueError("Image too small to hide this much data")
    
    # Encode length
    for i in range(32):
        flat_array[i] = (flat_array[i] & 0xFE) | int(length_bits[i])
    
    # Encode payload
    payload_bits = ''.join(format(byte, '08b') for byte in payload_bytes)
    for i, bit in enumerate(payload_bits):
        flat_array[32 + i] = (flat_array[32 + i] & 0xFE) | int(bit)
    
    # Reshape back to original shape
    stego_array = flat_array.reshape(img_array.shape)
    return Image.fromarray(stego_array.astype('uint8'), mode='RGB')

def extract_data_from_image(stego_image: Image.Image, access_code: str) -> bytes:
    """
    Extracts and decrypts hidden data from a steganographic image.
    Verifies access code before returning data.
    """
    import base64
    
    # Convert to RGB if needed
    if stego_image.mode != 'RGB':
        stego_image = stego_image.convert('RGB')
    
    img_array = np.array(stego_image)
    flat_array = img_array.flatten()
    
    # Check if array is large enough
    if len(flat_array) < 32:
        raise ValueError("Image too small to contain hidden data")
    
    # Extract length (first 32 bits)
    length_bits = ''.join(str(flat_array[i] & 1) for i in range(32))
    payload_length = int(length_bits, 2)
    
    # Validate payload length
    max_bytes = (len(flat_array) - 32) // 8
    if payload_length > max_bytes or payload_length <= 0:
        raise ValueError("Invalid payload length detected - image may not contain hidden data")
    
    # Extract payload
    payload_bits = ''.join(str(flat_array[32 + i] & 1) for i in range(payload_length * 8))
    payload_bytes = bytes(int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8))
    
    # Parse JSON payload
    try:
        payload = json.loads(payload_bytes.decode('utf-8'))
    except:
        raise ValueError("Failed to decode payload - image may not contain valid hidden data")
    
    # Verify access code
    provided_hash = generate_access_code_hash(access_code)
    if payload.get('hash') != provided_hash:
        raise ValueError("Invalid access code")
    
    # Decode and return encrypted data
    encrypted_data = base64.b64decode(payload['data'])
    return encrypted_data

# --- IPFS Integration (Pinata) ---

def upload_to_ipfs(image: Image.Image, filename: str = "holocrypt_qr.png") -> str:
    """
    Uploads steganographic image to IPFS using Pinata.
    Returns the IPFS CID.
    """
    PINATA_JWT = os.getenv('PINATA_JWT')
    
    if not PINATA_JWT:
        raise ValueError("PINATA_JWT not found in environment variables")
    
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }
    
    # Convert image to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    files = {
        'file': (filename, img_byte_arr, 'image/png')
    }
    
    try:
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result['IpfsHash']
    except Exception as e:
        raise Exception(f"Failed to upload to IPFS: {str(e)}")

def get_from_ipfs(cid: str) -> Image.Image:
    """
    Retrieves image from IPFS using Pinata gateway.
    """
    try:
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        raise Exception(f"Failed to retrieve from IPFS: {str(e)}")

# --- QR Code Generation with Website Redirect ---

def generate_qr_with_redirect(website_url: str, encrypted_data: str, cipher_type: str, 
                              cipher_params: dict) -> Image.Image:
    """
    Generates a QR code that redirects to your website with encrypted data as parameters.
    Works with both localhost (development) and deployed URLs (production).
    
    Args:
        website_url: Your website URL (e.g., "https://yourapp.streamlit.app/decrypt" or "http://localhost:8502")
        encrypted_data: The encrypted cipher text
        cipher_type: Type of cipher used
        cipher_params: Cipher parameters
    
    Returns:
        QR code image
    """
    # Use Streamlit deployment URL as default
    deployment_url = os.getenv('DEPLOYMENT_URL', 'https://holocrypt-ewmtjmjwtyue4v8bkc2uik.streamlit.app')
    
    # Create URL with encrypted data as query parameters
    params = {
        'data': base64.urlsafe_b64encode(encrypted_data.encode()).decode(),
        'cipher': cipher_type,
        'params': base64.urlsafe_b64encode(json.dumps(cipher_params).encode()).decode()
    }
    
    redirect_url = f"{deployment_url}?{urllib.parse.urlencode(params)}"
    
    qr = qrcode.QRCode(
        version=10,  # Larger version to hold URL with data
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img.convert('RGB')

def generate_base_qr(data: str = "HoloCrypt Protected Content") -> Image.Image:
    """Generates a base QR code image that will serve as the container."""
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img.convert('RGB')

# --- Credit System (Database) ---

class CreditSystem:
    """Manages user credits for encoding/decoding operations."""
    
    def __init__(self):
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_KEY", "")
            self.client = create_client(url, key) if url and key else None
        except:
            self.client = None
    
    def get_credits(self, user_id: str) -> int:
        """Get user's current credit balance."""
        if not self.client:
            return 100  # Default credits for demo mode
        
        try:
            result = self.client.table('users').select('credits').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0]['credits']
            return 0
        except:
            return 100  # Fallback to demo mode
    
    def deduct_credits(self, user_id: str, amount: int) -> bool:
        """Deduct credits from user account."""
        if not self.client:
            return True  # Always succeed in demo mode
        
        try:
            current = self.get_credits(user_id)
            if current < amount:
                return False
            
            new_balance = current - amount
            self.client.table('users').update({'credits': new_balance}).eq('user_id', user_id).execute()
            return True
        except:
            return True  # Fallback to demo mode
    
    def add_credits(self, user_id: str, amount: int):
        """Add credits to user account."""
        if not self.client:
            return
        
        try:
            current = self.get_credits(user_id)
            new_balance = current + amount
            self.client.table('users').upsert({'user_id': user_id, 'credits': new_balance}).execute()
        except:
            pass

# --- SMS/Text Message Function ---

def send_password_hint_sms(receiver_phone: str, password_hint: str, sender_name: str = "HoloCrypt") -> dict:
    """
    Sends a text message with the PDF password hint using Twilio.
    
    Args:
        receiver_phone: Recipient's phone number (format: +1234567890)
        password_hint: Hint or password message
        sender_name: Sender's name
    
    Returns:
        dict with success status and message
    """
    try:
        # Get Twilio credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, twilio_phone]):
            return {
                'success': False,
                'message': 'Twilio credentials not configured in .env file'
            }
        
        # Import Twilio client
        from twilio.rest import Client
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Format message body
        message_body = f"🔐 HoloCrypt from {sender_name}\n\n{password_hint}"
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone,
            to=receiver_phone
        )
        
        print(f"\n📱 SMS Sent Successfully!")
        print(f"To: {receiver_phone}")
        print(f"From: {twilio_phone}")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        
        return {
            'success': True,
            'message': f'SMS sent to {receiver_phone}',
            'sms_sid': message.sid,
            'sms_status': message.status,
            'sms_body': message_body
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ SMS Error: {error_msg}")
        
        return {
            'success': False,
            'message': f'SMS sending failed: {error_msg}'
        }

# --- Email Sending with Resend API ---

def create_qr_pdf(qr_image: Image.Image, cipher_text: str, cipher_type: str, 
                  cipher_params: dict, receiver_email: str, sender_name: str, 
                  pdf_password: str = None) -> BytesIO:
    """
    Creates a password-protected PDF containing the QR code and encrypted cipher information.
    
    Args:
        pdf_password: Password to protect the PDF (optional)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 1*inch, "HoloCrypt Encrypted Message")
    
    # Receiver info
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, f"To: {receiver_email}")
    c.drawString(1*inch, height - 1.8*inch, f"From: {sender_name}")
    
    # QR Code
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2.5*inch, "Scan this QR Code:")
    
    # Insert QR image
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    c.drawImage(qr_reader, 1*inch, height - 5.5*inch, width=3*inch, height=3*inch)
    
    # Cipher Information Box
    c.setFont("Helvetica-Bold", 14)
    c.drawString(4.5*inch, height - 2.5*inch, "Cipher Clue:")
    
    c.setFont("Helvetica", 10)
    
    # Generate and display cipher clue
    cipher_clue = generate_cipher_clue(cipher_type, cipher_params)
    
    # Wrap the clue text
    max_width_clue = 35
    clue_lines = []
    words = cipher_clue.split()
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_width_clue:
            current_line += (" " + word) if current_line else word
        else:
            if current_line:
                clue_lines.append(current_line)
            current_line = word
    if current_line:
        clue_lines.append(current_line)
    
    y_pos = height - 2.8*inch
    for line in clue_lines[:5]:  # Max 5 lines for clue
        c.drawString(4.5*inch, y_pos, line)
        y_pos -= 0.2*inch
    
    # Encrypted text (wrapped)
    c.setFont("Courier-Bold", 9)
    c.drawString(1*inch, height - 6.2*inch, "Encrypted Cipher Text:")
    
    c.setFont("Courier", 8)
    # Wrap cipher text
    max_width = 90
    wrapped_lines = [cipher_text[i:i+max_width] for i in range(0, len(cipher_text), max_width)]
    
    y_pos = height - 6.5*inch
    for line in wrapped_lines[:25]:
        c.drawString(1*inch, y_pos, line)
        y_pos -= 0.15*inch
        if y_pos < 1*inch:
            c.drawString(1*inch, y_pos, "... (text truncated, see full message in email)")
            break
    
    # Instructions at bottom
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1*inch, 0.7*inch, "Keep this document secure. Scan QR code to decrypt on our website.")
    c.drawString(1*inch, 0.5*inch, "Enter the correct cipher to decrypt, wrong cipher will show a puzzle.")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 0.3*inch, "HoloCrypt - Secure Multi-Layer Encryption System")
    
    c.save()
    pdf_buffer.seek(0)
    
    # Apply password protection if provided
    if pdf_password:
        temp_buffer = BytesIO()
        reader = PdfReader(pdf_buffer)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Encrypt with password
        writer.encrypt(pdf_password, algorithm="AES-256")
        
        # Write to new buffer
        writer.write(temp_buffer)
        temp_buffer.seek(0)
        return temp_buffer
    
    return pdf_buffer

def send_email_with_resend(receiver_email: str, puzzle_message: str, qr_image: Image.Image, 
                           cipher_type: str, cipher_params: dict, cipher_text: str,
                           sender_name: str = "HoloCrypt", 
                           website_url: str = "https://yourwebsite.com/decrypt",
                           pdf_password: str = None) -> dict:
    """
    Sends an email to the receiver using Resend API with ONLY the PDF attachment (no body text).
    
    Args:
        receiver_email: Recipient's email address
        puzzle_message: The riddle/puzzle formatted message
        qr_image: PIL Image of the QR code
        cipher_type: Type of cipher used
        cipher_params: Dictionary of cipher parameters
        cipher_text: The encrypted cipher text
        sender_name: Sender's name
        website_url: URL of your decryption website
        pdf_password: Password to protect the PDF
    
    Returns:
        dict with 'success' (bool) and 'message' (str) keys
    """
    # Get API key from environment or use provided key
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', "re_gDc5Qt7T_8XAdPpZx2dRajsS9CHMJhXiP")
    
    if not RESEND_API_KEY:
        return {
            'success': False,
            'message': 'RESEND_API_KEY not configured in .env file'
        }
    
    # Check if this is a test mode (unverified domain)
    # In test mode, can only send to account owner email
    test_mode_email = "punithns26@gmail.com"
    
    try:
        # Create password-protected PDF attachment
        pdf_buffer = create_qr_pdf(
            qr_image=qr_image,
            cipher_text=cipher_text,
            cipher_type=cipher_type,
            cipher_params=cipher_params,
            receiver_email=receiver_email,
            sender_name=sender_name,
            pdf_password=pdf_password
        )
        
        # Convert PDF to base64
        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode()
        
        # Minimal email body - no details revealed
        email_html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <p>You have received a secure encrypted message.</p>
            <p><strong>Please open the attached PDF for details.</strong></p>
        </body>
        </html>
        """
        
        # Prepare Resend API request
        url = "https://api.resend.com/emails"
        
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": "onboarding@resend.dev",  # Resend verified sender
            "to": [receiver_email],
            "subject": "HoloCrypt: You've Received an Encrypted Message",
            "html": email_html,
            "attachments": [
                {
                    "filename": "holocrypt_encrypted_message.pdf",
                    "content": pdf_base64
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        # Debug: Print response details
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get('message', str(error_data))
                
                # Provide helpful message for common errors
                if response.status_code == 403 and 'testing emails' in error_msg:
                    return {
                        'success': False,
                        'message': f'⚠️ Test Mode: Can only send to {test_mode_email}\n\n' +
                                 'To send to other emails:\n' +
                                 '1. Verify a domain at resend.com/domains\n' +
                                 '2. Update sender email in code\n\n' +
                                 f'For testing, use receiver email: {test_mode_email}'
                    }
            except:
                error_msg = response.text
            
            return {
                'success': False,
                'message': f'Resend API error ({response.status_code}): {error_msg}'
            }
        
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': True,
            'message': f'Email successfully sent to {receiver_email} via Resend',
            'email_id': result.get('id')
        }
    
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json() if e.response else str(e)
        return {
            'success': False,
            'message': f'Resend API error: {error_detail}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }

# --- Web-based Decryption Functions ---

def validate_and_decrypt(encrypted_data: str, provided_cipher: str, provided_params: dict,
                        actual_cipher: str, actual_params: dict) -> dict:
    """
    Validates the provided cipher and decrypts or puzzles the data accordingly.
    
    Args:
        encrypted_data: The encrypted cipher text
        provided_cipher: Cipher type entered by user
        provided_params: Cipher parameters entered by user
        actual_cipher: The actual cipher type used
        actual_params: The actual cipher parameters used
    
    Returns:
        dict with 'correct' (bool), 'result' (str), and 'message' (str)
    """
    # Check if cipher matches
    if (provided_cipher.lower() == actual_cipher.lower() and 
        provided_params == actual_params):
        # Correct cipher - decrypt the data
        try:
            decrypted = decipher_data(encrypted_data, actual_cipher, actual_params)
            return {
                'correct': True,
                'result': decrypted,
                'message': '✅ Correct cipher! Message decrypted successfully.'
            }
        except Exception as e:
            return {
                'correct': False,
                'result': '',
                'message': f'❌ Decryption failed: {str(e)}'
            }
    else:
        # Wrong cipher - generate puzzle
        try:
            puzzled = generate_puzzle_with_nltk(encrypted_data, difficulty="medium")
            return {
                'correct': False,
                'result': puzzled,
                'message': '❌ Wrong cipher! Here\'s a puzzled version of the message.'
            }
        except Exception as e:
            return {
                'correct': False,
                'result': encrypted_data,
                'message': f'❌ Wrong cipher! Original encrypted text shown. Error: {str(e)}'
            }

def decode_qr_params(query_string: str) -> dict:
    """
    Decodes parameters from QR code redirect URL.
    
    Args:
        query_string: URL query string from QR scan
    
    Returns:
        dict with decoded parameters
    """
    try:
        params = urllib.parse.parse_qs(query_string)
        
        encrypted_data = base64.urlsafe_b64decode(params['data'][0]).decode()
        cipher_type = params['cipher'][0]
        cipher_params = json.loads(base64.urlsafe_b64decode(params['params'][0]).decode())
        
        return {
            'encrypted_data': encrypted_data,
            'cipher_type': cipher_type,
            'cipher_params': cipher_params
        }
    except Exception as e:
        raise ValueError(f"Failed to decode QR parameters: {str(e)}")


# --- Complete Workflow Functions ---

def encode_and_send(original_message: str, receiver_email: str, cipher_type: str,
                   cipher_params: dict, sender_name: str = "HoloCrypt",
                   website_url: str = "https://holocrypt-ewmtjmjwtyue4v8bkc2uik.streamlit.app",
                   pdf_password: str = None, receiver_phone: str = None,
                   password_hint: str = None) -> dict:
    """
    Complete workflow: Encrypt, generate QR, send email with password-protected PDF, and send SMS with password hint.
    
    Args:
        original_message: Plain text message to encrypt
        receiver_email: Recipient's email
        cipher_type: Type of cipher to use
        cipher_params: Cipher parameters
        sender_name: Sender's name
        website_url: Your decryption website URL
        pdf_password: Password to protect the PDF
        receiver_phone: Recipient's phone number for SMS (optional)
        password_hint: Custom password hint message for SMS (optional)
    
    Returns:
        dict with status and details
    """
    try:
        # Step 1: Shuffle/encrypt data based on cipher
        encrypted_text = shuffle_data_by_cipher(original_message, cipher_type, cipher_params)
        
        # Step 2: Create puzzle message
        puzzle_message = f"🧩 Encrypted with {cipher_type} cipher\n\n{encrypted_text}"
        
        # Step 3: Generate QR code with redirect URL
        qr_image = generate_qr_with_redirect(website_url, encrypted_text, cipher_type, cipher_params)
        
        # Step 4: Send email via Resend with password-protected PDF
        email_result = send_email_with_resend(
            receiver_email=receiver_email,
            puzzle_message=puzzle_message,
            qr_image=qr_image,
            cipher_type=cipher_type,
            cipher_params=cipher_params,
            cipher_text=encrypted_text,
            sender_name=sender_name,
            website_url=website_url,
            pdf_password=pdf_password
        )
        
        # Step 5: Send SMS with password hint (if phone number provided)
        sms_result = None
        if receiver_phone and pdf_password:
            if not password_hint:
                password_hint = f"Your PDF password is: {pdf_password}"
            
            sms_result = send_password_hint_sms(
                receiver_phone=receiver_phone,
                password_hint=password_hint,
                sender_name=sender_name
            )
        
        if email_result['success']:
            return {
                'success': True,
                'message': 'Message encrypted and sent successfully!',
                'encrypted_text': encrypted_text,
                'email_status': email_result,
                'sms_status': sms_result
            }
        else:
            return {
                'success': False,
                'message': email_result['message']
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Encoding failed: {str(e)}'
        }


# --- Example Usage ---

if __name__ == "__main__":
    # Example: Encode and send a message
    result = encode_and_send(
        original_message="Hello, this is a secret message!",
        receiver_email="receiver@example.com",
        cipher_type="caesar",
        cipher_params={"shift": 5},
        sender_name="Alice",
        website_url="https://yourwebsite.com/decrypt"
    )
    
    print(json.dumps(result, indent=2))
    
    # Example: Validate decryption attempt
    validation = validate_and_decrypt(
        encrypted_data="Mjqqt, ymx nx f xjhwjy rjxxflj!",
        provided_cipher="caesar",
        provided_params={"shift": 5},
        actual_cipher="caesar",
        actual_params={"shift": 5}
    )
    
    print(json.dumps(validation, indent=2))
