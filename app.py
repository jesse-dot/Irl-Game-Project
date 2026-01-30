"""
Flask Web Application for AI Game Project
Provides web UI for uploading images/videos and viewing AI decisions
"""

from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from ai_agent import GameAI

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI agent
ai_agent = GameAI(inventory_size=10)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded image and return AI decision"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Read file data
        image_data = file.read()
        
        # Analyze with AI
        result = ai_agent.analyze_image(image_data)
        
        # Get updated inventory
        inventory = ai_agent.get_inventory_state()
        
        return jsonify({
            'result': result,
            'inventory': inventory
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get current inventory state"""
    return jsonify(ai_agent.get_inventory_state())


@app.route('/api/inventory/clear', methods=['POST'])
def clear_inventory():
    """Clear all inventory"""
    ai_agent.clear_inventory()
    return jsonify({'success': True, 'inventory': ai_agent.get_inventory_state()})


@app.route('/api/inventory/remove/<int:slot_id>', methods=['POST'])
def remove_item(slot_id):
    """Remove item from specific slot"""
    item = ai_agent.remove_from_inventory(slot_id)
    return jsonify({
        'success': item is not None,
        'removed_item': item,
        'inventory': ai_agent.get_inventory_state()
    })


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get action history"""
    return jsonify(ai_agent.get_actions_history())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
