"""
HoloCrypt Flask Application with REST API
Multi-layer encryption system with email delivery and SMS notifications
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import base64
import json
from io import BytesIO
from holocrypt_enhanced import (
    encode_and_send,
    shuffle_data_by_cipher,
    decipher_data,
    validate_and_decrypt,
    generate_qr_with_redirect,
    create_qr_pdf,
    send_password_hint_sms,
    generate_cipher_clue
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'holocrypt-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """Serve React app homepage"""
    return send_file('static/dist/index.html')

@app.route('/assets/<path:path>')
def serve_assets(path):
    """Serve React build assets"""
    return send_from_directory('static/dist/assets', path)

@app.route('/<path:path>')
def serve_react_routes(path):
    """Serve React app for client-side routing"""
    # Don't intercept API routes
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    # Check if file exists in static/dist
    file_path = os.path.join('static/dist', path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    
    # Return index.html for client-side routing (React Router)
    return send_file('static/dist/index.html')

@app.route('/api/docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

# ==================== REST API ENDPOINTS ====================

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'HoloCrypt API',
        'version': '1.0.0'
    })

@app.route('/api/v1/encrypt', methods=['POST'])
def api_encrypt():
    """
    API Endpoint: Encrypt message with cipher
    
    Request Body:
    {
        "message": "Your secret message",
        "cipher_type": "caesar",
        "cipher_params": {"shift": 5}
    }
    
    Response:
    {
        "success": true,
        "encrypted_text": "...",
        "cipher_type": "caesar",
        "cipher_params": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        cipher_type = data.get('cipher_type', 'caesar')
        cipher_params = data.get('cipher_params', {'shift': 5})
        
        # Encrypt the message
        encrypted_text = shuffle_data_by_cipher(message, cipher_type, cipher_params)
        
        return jsonify({
            'success': True,
            'encrypted_text': encrypted_text,
            'cipher_type': cipher_type,
            'cipher_params': cipher_params,
            'original_length': len(message),
            'encrypted_length': len(encrypted_text)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/decrypt', methods=['POST'])
def api_decrypt():
    """
    API Endpoint: Decrypt message with cipher
    
    Request Body:
    {
        "encrypted_text": "...",
        "cipher_type": "caesar",
        "cipher_params": {"shift": 5}
    }
    
    Response:
    {
        "success": true,
        "decrypted_text": "Your secret message"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'encrypted_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: encrypted_text'
            }), 400
        
        encrypted_text = data['encrypted_text']
        cipher_type = data.get('cipher_type', 'caesar')
        cipher_params = data.get('cipher_params', {'shift': 5})
        
        # Decrypt the message
        decrypted_text = decipher_data(encrypted_text, cipher_type, cipher_params)
        
        return jsonify({
            'success': True,
            'decrypted_text': decrypted_text,
            'cipher_type': cipher_type,
            'cipher_params': cipher_params
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/validate-decrypt', methods=['POST'])
def api_validate_decrypt():
    """
    API Endpoint: Validate cipher and decrypt (with puzzle on wrong cipher)
    
    Request Body:
    {
        "encrypted_text": "...",
        "provided_cipher": "caesar",
        "provided_params": {"shift": 5},
        "actual_cipher": "caesar",
        "actual_params": {"shift": 5}
    }
    
    Response:
    {
        "success": true,
        "correct": true,
        "result": "Decrypted message",
        "message": "Correct cipher!"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['encrypted_text', 'provided_cipher', 'provided_params', 
                          'actual_cipher', 'actual_params']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate and decrypt
        result = validate_and_decrypt(
            encrypted_data=data['encrypted_text'],
            provided_cipher=data['provided_cipher'],
            provided_params=data['provided_params'],
            actual_cipher=data['actual_cipher'],
            actual_params=data['actual_params']
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/send-encrypted-email', methods=['POST'])
def api_send_encrypted_email():
    """
    API Endpoint: Encrypt and send via email
    
    Request Body:
    {
        "message": "Your secret message",
        "receiver_email": "receiver@example.com",
        "cipher_type": "caesar",
        "cipher_params": {"shift": 5},
        "sender_name": "Alice",
        "pdf_password": "secret123",
        "receiver_phone": "+1234567890",  // Optional
        "password_hint": "Custom hint"    // Optional
    }
    
    Response:
    {
        "success": true,
        "message": "Email sent successfully",
        "encrypted_text": "...",
        "email_status": {...},
        "sms_status": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['message', 'receiver_email', 'sender_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Get website URL from environment or request
        website_url = os.getenv('DEPLOYMENT_URL', 'https://holocrypt-ewmtjmjwtyue4v8bkc2uik.streamlit.app')
        
        # Send encrypted email
        result = encode_and_send(
            original_message=data['message'],
            receiver_email=data['receiver_email'],
            cipher_type=data.get('cipher_type', 'caesar'),
            cipher_params=data.get('cipher_params', {'shift': 5}),
            sender_name=data['sender_name'],
            website_url=website_url,
            pdf_password=data.get('pdf_password'),
            receiver_phone=data.get('receiver_phone'),
            password_hint=data.get('password_hint')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/generate-qr', methods=['POST'])
def api_generate_qr():
    """
    API Endpoint: Generate QR code for encrypted message
    
    Request Body:
    {
        "encrypted_text": "...",
        "cipher_type": "caesar",
        "cipher_params": {"shift": 5}
    }
    
    Response: PNG image of QR code
    """
    try:
        data = request.get_json()
        
        if not data or 'encrypted_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: encrypted_text'
            }), 400
        
        encrypted_text = data['encrypted_text']
        cipher_type = data.get('cipher_type', 'caesar')
        cipher_params = data.get('cipher_params', {'shift': 5})
        
        # Get website URL
        website_url = os.getenv('DEPLOYMENT_URL', 'https://holocrypt-ewmtjmjwtyue4v8bkc2uik.streamlit.app')
        
        # Generate QR code
        qr_image = generate_qr_with_redirect(
            website_url=website_url,
            encrypted_data=encrypted_text,
            cipher_type=cipher_type,
            cipher_params=cipher_params
        )
        
        # Convert PIL image to bytes
        img_io = BytesIO()
        qr_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=False)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/send-sms', methods=['POST'])
def api_send_sms():
    """
    API Endpoint: Send SMS with password hint
    
    Request Body:
    {
        "receiver_phone": "+1234567890",
        "password_hint": "Your password is: secret123",
        "sender_name": "Alice"
    }
    
    Response:
    {
        "success": true,
        "message": "SMS sent successfully",
        "sms_sid": "...",
        "sms_status": "..."
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['receiver_phone', 'password_hint']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Send SMS
        result = send_password_hint_sms(
            receiver_phone=data['receiver_phone'],
            password_hint=data['password_hint'],
            sender_name=data.get('sender_name', 'HoloCrypt')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/cipher-clue', methods=['POST'])
def api_cipher_clue():
    """
    API Endpoint: Generate cipher clue/hint
    
    Request Body:
    {
        "cipher_type": "caesar",
        "cipher_params": {"shift": 5}
    }
    
    Response:
    {
        "success": true,
        "clue": "Cipher clue text"
    }
    """
    try:
        data = request.get_json()
        
        cipher_type = data.get('cipher_type', 'caesar')
        cipher_params = data.get('cipher_params', {'shift': 5})
        
        # Generate clue
        clue = generate_cipher_clue(cipher_type, cipher_params)
        
        return jsonify({
            'success': True,
            'clue': clue,
            'cipher_type': cipher_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/ciphers', methods=['GET'])
def api_list_ciphers():
    """
    API Endpoint: List available cipher types
    
    Response:
    {
        "success": true,
        "ciphers": [...]
    }
    """
    ciphers = [
        {
            "type": "caesar",
            "name": "Caesar Cipher",
            "description": "Shifts each letter by a fixed number of positions",
            "params": {
                "shift": {"type": "integer", "min": 1, "max": 25, "default": 5}
            },
            "example": {
                "plaintext": "HELLO",
                "shift": 5,
                "ciphertext": "MJQQT"
            }
        },
        {
            "type": "vigenere",
            "name": "Vigenere Cipher",
            "description": "Uses a keyword to shift letters by varying amounts",
            "params": {
                "keyword": {"type": "string", "default": "SECRET"}
            },
            "example": {
                "plaintext": "HELLO",
                "keyword": "SECRET",
                "ciphertext": "ZINCS"
            }
        },
        {
            "type": "atbash",
            "name": "Atbash Cipher",
            "description": "Reverses the alphabet (A↔Z, B↔Y, etc.)",
            "params": {},
            "example": {
                "plaintext": "HELLO",
                "ciphertext": "SVOOL"
            }
        },
        {
            "type": "rail_fence",
            "name": "Rail Fence Cipher",
            "description": "Writes message in zigzag pattern across rails",
            "params": {
                "rails": {"type": "integer", "min": 2, "max": 10, "default": 3}
            },
            "example": {
                "plaintext": "HELLO",
                "rails": 3,
                "ciphertext": "HOELL"
            }
        },
        {
            "type": "substitution",
            "name": "Substitution Cipher",
            "description": "Maps each letter to a different letter using custom key",
            "params": {
                "substitution_key": {"type": "string", "length": 26, "default": "QWERTYUIOPASDFGHJKLZXCVBNM"}
            },
            "example": {
                "plaintext": "HELLO",
                "substitution_key": "QWERTYUIOPASDFGHJKLZXCVBNM",
                "ciphertext": "ITSSG"
            }
        }
    ]
    
    return jsonify({
        'success': True,
        'ciphers': ciphers,
        'total': len(ciphers)
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return render_template('error.html', error="Internal server error"), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB'
    }), 413

# ==================== MAIN ====================

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🔐 HoloCrypt Flask API Server")
    print("=" * 60)
    print(f"Running on: http://localhost:{port}")
    print(f"API Docs: http://localhost:{port}/api/docs")
    print(f"Health Check: http://localhost:{port}/api/v1/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
