"""
AI Agent for Game-like Decision Making
Processes images/videos and makes decisions like it's playing a game with inventory
Uses Google Gemini API for vision analysis
"""

import os
import base64
from typing import Dict, List, Optional, Tuple
from PIL import Image
import io
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InventorySlot:
    """Represents a single inventory slot"""
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.item = None
        self.quantity = 0
    
    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item to this slot"""
        self.item = item_name
        self.quantity = quantity
    
    def remove_item(self):
        """Remove item from this slot"""
        item = self.item
        self.item = None
        self.quantity = 0
        return item
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'slot_id': self.slot_id,
            'item': self.item,
            'quantity': self.quantity
        }


class GameAI:
    """AI Agent that thinks like it's playing a game"""
    
    # Available game commands
    DIRECTIONAL_COMMANDS = [
        "Walk forward",
        "Turn left", 
        "Turn right",
        "Proceed to [Object]"
    ]
    
    INTERACTION_COMMANDS = [
        "Pick up [Object]",
        "Examine [Object]",
        "Use [Object] on [Target]"
    ]
    
    INVENTORY_COMMANDS = [
        "Put [Object] in inventory",
        "Take [Object] from inventory"
    ]
    
    def __init__(self, inventory_size: int = 10, max_history_size: int = 100):
        self.inventory_size = inventory_size
        self.inventory = [InventorySlot(i) for i in range(inventory_size)]
        self.actions_history = []
        self.max_history_size = max_history_size
        
        # Initialize Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_ai = True
        else:
            self.model = None
            self.use_ai = False
            print("Warning: GEMINI_API_KEY not found. Using fallback mode.")
    
    def analyze_image(self, image_data: bytes) -> Dict:
        """
        Analyze an image and decide what action to take
        Returns: Dictionary with action, reasoning, and detected items
        """
        try:
            # Open and analyze the image
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Use Gemini AI if available, otherwise use fallback
            if self.use_ai:
                decision = self._analyze_with_gemini(image)
            else:
                decision = self._fallback_analysis(image, width, height)
            
            # Record the action with history limit
            self.actions_history.append(decision)
            if len(self.actions_history) > self.max_history_size:
                self.actions_history.pop(0)  # Remove oldest action
            
            return decision
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'ERROR',
                'reasoning': f'Failed to process image: {str(e)}'
            }
    
    def _analyze_with_gemini(self, image: Image.Image) -> Dict:
        """
        Use Gemini AI to analyze the image and make a decision
        """
        try:
            # Get inventory status
            inventory_items = [slot.item for slot in self.inventory if slot.item is not None]
            empty_slots = sum(1 for slot in self.inventory if slot.item is None)
            
            # Create detailed prompt for Gemini
            prompt = f"""You are an AI playing a game. Analyze this image and decide ONE action to take.

Available Commands:
1. Directional: "Walk forward", "Turn left", "Turn right", "Proceed to [Object]"
2. Interaction: "Pick up [Object]", "Examine [Object]", "Use [Object] on [Target]"
3. Inventory: "Put [Object] in inventory", "Take [Object] from inventory"

Current Inventory ({len(inventory_items)}/{self.inventory_size} slots used):
{', '.join(inventory_items) if inventory_items else 'Empty'}
Empty slots available: {empty_slots}

Analyze the image and respond in this EXACT format:
ACTION: [Your chosen action]
REASONING: [Why you chose this action]
DETECTED_ITEMS: [Comma-separated list of items/objects you see]
SCENE: [Brief description of what you see]

Think like you're playing a game. Be specific about objects you see and choose the most appropriate action."""

            # Generate response
            response = self.model.generate_content([prompt, image])
            response_text = response.text
            
            # Parse the response
            action = "Observe"
            reasoning = "Analyzing the scene"
            detected_items = []
            scene_analysis = ""
            
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.upper().startswith('ACTION:'):
                    action = line[line.index(':')+1:].strip()
                elif line.upper().startswith('REASONING:'):
                    reasoning = line[line.index(':')+1:].strip()
                elif line.upper().startswith('DETECTED_ITEMS:'):
                    items_str = line[line.index(':')+1:].strip()
                    detected_items = [item.strip() for item in items_str.split(',') if item.strip()]
                elif line.upper().startswith('SCENE:'):
                    scene_analysis = line[line.index(':')+1:].strip()
            
            # Validate that we got meaningful data
            if not action or action == "Observe":
                # Response didn't have proper format, use fallback
                return self._fallback_analysis(image, image.size[0], image.size[1])
            
            # Handle inventory actions
            if "put" in action.lower() and "inventory" in action.lower():
                # Extract object name
                for item in detected_items:
                    if item.lower() in action.lower():
                        if empty_slots > 0:
                            self._add_to_inventory(item)
                        break
            elif "take" in action.lower() and "from inventory" in action.lower():
                # Extract object name from inventory
                for item in inventory_items:
                    if item.lower() in action.lower():
                        for slot in self.inventory:
                            if slot.item == item:
                                slot.remove_item()
                                break
                        break
            
            return {
                'success': True,
                'action': action,
                'reasoning': reasoning,
                'detected_items': detected_items,
                'scene_analysis': scene_analysis
            }
            
        except Exception as e:
            # Log the error for debugging
            print(f"Gemini API error: {type(e).__name__}: {str(e)}")
            # Fallback to simple analysis if Gemini fails
            return self._fallback_analysis(image, image.size[0], image.size[1])
    
    def _fallback_analysis(self, image: Image.Image, width: int, height: int) -> Dict:
        """
        Fallback: Make a game-like decision based on simple image analysis
        """
        # Get dominant colors (simplified)
        image_small = image.resize((50, 50))
        pixels = list(image_small.getdata())
        
        # Calculate average brightness with proper handling for different image modes
        if image.mode == 'RGB' or image.mode == 'RGBA':
            brightness = sum(sum(p[:3]) for p in pixels) / (len(pixels) * 3)
        elif image.mode == 'L':
            # Grayscale - pixels are single integers
            brightness = sum(pixels) / len(pixels)
        else:
            # Convert to RGB first for other modes
            image = image.convert('RGB')
            pixels = list(image_small.getdata())
            brightness = sum(sum(p[:3]) for p in pixels) / (len(pixels) * 3)
        
        # Detect objects based on simple heuristics (placeholder for real AI)
        detected_items = self._detect_items(image, brightness)
        
        # Decide action based on what we "see"
        action = self._choose_action(detected_items, brightness)
        
        return {
            'success': True,
            'action': action['name'],
            'reasoning': action['reasoning'],
            'detected_items': detected_items,
            'image_info': {
                'width': width,
                'height': height,
                'brightness': round(brightness, 2)
            }
        }
    
    def _detect_items(self, image: Image.Image, brightness: float) -> List[str]:
        """
        Detect items in the image (simplified - would use real AI model)
        """
        items = []
        
        # Simple heuristic-based detection
        if brightness > 200:
            items.append("Light Source")
        elif brightness < 50:
            items.append("Dark Area")
        
        # Analyze image mode
        if image.mode == 'RGB':
            items.append("Colorful Object")
        elif image.mode == 'L':
            items.append("Grayscale Object")
        
        # Check aspect ratio
        width, height = image.size
        aspect_ratio = width / height
        if aspect_ratio > 1.5:
            items.append("Wide Object")
        elif aspect_ratio < 0.7:
            items.append("Tall Object")
        else:
            items.append("Square Object")
        
        return items
    
    def _choose_action(self, detected_items: List[str], brightness: float) -> Dict:
        """
        Choose a game command based on detected items
        """
        # Check inventory space
        empty_slots = sum(1 for slot in self.inventory if slot.item is None)
        
        if not detected_items:
            return {
                'name': 'Examine surroundings',
                'reasoning': 'No clear objects detected. Need to examine the environment more carefully.'
            }
        
        # If we have items and space, pick them up
        if empty_slots > 0 and detected_items:
            item_to_collect = detected_items[0]
            if self._add_to_inventory(item_to_collect):
                return {
                    'name': f'Pick up {item_to_collect}',
                    'reasoning': f'Found {item_to_collect}. Picking it up and storing in inventory (slots available: {empty_slots}).'
                }
        
        # If inventory is full, need to manage it
        if empty_slots == 0:
            return {
                'name': 'Examine inventory',
                'reasoning': 'Inventory is full. Need to examine what items to keep or drop.'
            }
        
        # Analyze environment for navigation
        if brightness > 200:
            return {
                'name': 'Turn left',
                'reasoning': 'Bright area ahead. Turning to explore alternative path.'
            }
        elif brightness < 50:
            return {
                'name': 'Use torch',
                'reasoning': 'Environment is dark. Need to use a light source for illumination.'
            }
        
        # Default exploration actions
        if detected_items:
            return {
                'name': f'Proceed to {detected_items[0]}',
                'reasoning': f'Detected {detected_items[0]} ahead. Moving closer to investigate.'
            }
        
        return {
            'name': 'Walk forward',
            'reasoning': 'Clear path ahead. Moving forward to explore.'
        }
    
    def _add_to_inventory(self, item_name: str) -> bool:
        """Add an item to the first available inventory slot"""
        for slot in self.inventory:
            if slot.item is None:
                slot.add_item(item_name, 1)
                return True
        return False
    
    def get_inventory_state(self) -> List[Dict]:
        """Get current inventory state"""
        return [slot.to_dict() for slot in self.inventory]
    
    def clear_inventory(self):
        """Clear all inventory slots"""
        for slot in self.inventory:
            slot.remove_item()
    
    def remove_from_inventory(self, slot_id: int) -> Optional[str]:
        """Remove item from specific slot"""
        if 0 <= slot_id < len(self.inventory):
            return self.inventory[slot_id].remove_item()
        return None
    
    def get_actions_history(self) -> List[Dict]:
        """Get history of all actions taken"""
        return self.actions_history
