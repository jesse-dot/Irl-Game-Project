# AI Game Project 🎮

An AI-powered game agent that analyzes images and makes game-like decisions with inventory management. The AI thinks like it's playing a real game, making decisions about movement, interactions, and inventory management.

## Features

- 🤖 **AI Vision Analysis**: Uses Google Gemini API to analyze images and understand the scene
- 🎮 **Game-like Commands**: Makes decisions using realistic game commands
  - **Directional**: Walk forward, Turn left/right, Proceed to objects
  - **Interaction**: Pick up items, Examine objects, Use items on targets
  - **Inventory**: Put items in inventory, Take items from inventory
- 🎒 **Inventory System**: 10-slot inventory with visual representation
- 🌐 **Web UI**: Beautiful, responsive interface for easy interaction
- 📜 **Action History**: Track all decisions and actions made by the AI

## Game Commands

The AI can choose from the following types of commands:

### Directional Commands
- "Walk forward" - Move ahead
- "Turn left" - Rotate left
- "Turn right" - Rotate right  
- "Proceed to [Object]" - Move towards a specific object

### Interaction Commands
- "Pick up [Object]" - Collect an item
- "Examine [Object]" - Investigate something
- "Use [Object] on [Target]" - Use one item on another

### Inventory Commands
- "Put [Object] in inventory" - Store an item
- "Take [Object] from inventory" - Retrieve an item

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- A Google Gemini API key (free tier available)

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/jesse-dot/Irl-Game-Project.git
cd Irl-Game-Project

# Install required packages
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_actual_api_key_here
```

Or set it as an environment variable:

```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 4. Run the Application

```bash
python app.py
```

The web interface will be available at: `http://localhost:5000`

## Usage

1. **Open the web interface** in your browser
2. **Upload an image** by clicking the upload area or dragging and dropping
3. **Click "Analyze Image"** to let the AI make a decision
4. **View the results**:
   - See what action the AI chose
   - Read the AI's reasoning
   - Check detected items and scene analysis
   - Monitor inventory changes
   - Review action history

## How It Works

1. **Image Upload**: User uploads an image through the web UI
2. **AI Analysis**: Gemini vision model analyzes the image
3. **Decision Making**: AI chooses one game-appropriate action based on:
   - What objects/items it sees in the scene
   - Current inventory status (full/empty slots)
   - Game context and objectives
4. **Inventory Management**: Items are automatically added/removed from inventory
5. **Action Recording**: All decisions are logged in the history

## Example Scenarios

### Scenario 1: Finding an Item
- **Image**: Picture of a key on a table
- **AI Decision**: "Pick up key"
- **Reasoning**: "Found a key on the table. This could be useful for unlocking doors."
- **Result**: Key added to inventory slot

### Scenario 2: Dark Environment
- **Image**: Dark room or hallway
- **AI Decision**: "Use torch"
- **Reasoning**: "Environment is very dark. Need illumination to see clearly."

### Scenario 3: Multiple Objects
- **Image**: Room with various items
- **AI Decision**: "Examine sword"
- **Reasoning**: "Detected a sword among other objects. Should examine it before picking up."

## Project Structure

```
Irl-Game-Project/
├── app.py                 # Flask web application
├── ai_agent.py           # AI agent with Gemini integration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variable template
├── templates/
│   └── index.html       # Web UI template
├── static/
│   ├── css/
│   │   └── style.css    # Styles
│   └── js/
│       └── main.js      # Frontend JavaScript
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main web interface
- `POST /api/analyze` - Analyze an uploaded image
- `GET /api/inventory` - Get current inventory state
- `POST /api/inventory/clear` - Clear all inventory
- `POST /api/inventory/remove/<slot_id>` - Remove item from slot
- `GET /api/history` - Get action history

## Gemini API Free Tier

The free tier of Gemini API includes:
- 15 requests per minute
- 1,500 requests per day
- Free for testing and development

Perfect for this project! No credit card required.

## Troubleshooting

### "GEMINI_API_KEY not found" Warning
- Make sure you created a `.env` file with your API key
- Or set the `GEMINI_API_KEY` environment variable
- The app will still work in fallback mode without AI

### API Rate Limits
- Free tier: 15 requests/minute
- If you hit limits, wait a minute before trying again

### Image Upload Issues
- Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP
- Max file size: 16MB

### Multi-User Considerations
- Currently, all users share the same inventory and action history
- For production use with multiple users, consider implementing session-based storage
- Set `FLASK_DEBUG=false` in production environments

## Contributing

Feel free to open issues or submit pull requests!

## License

MIT License - feel free to use this project for learning and development.
