// Main JavaScript for AI Game Project

let currentFile = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeInventory();
    loadHistory();
});

// Upload functionality
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');

    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // File selection
    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files[0]);
    });

    // Analyze button
    analyzeBtn.addEventListener('click', analyzeImage);
}

function handleFileSelect(file) {
    if (!file) return;

    // Check if it's an image
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    currentFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imagePreview').classList.remove('hidden');
        document.getElementById('analyzeBtn').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

async function analyzeImage() {
    if (!currentFile) return;

    showLoading(true);

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            displayError(data.error);
        } else {
            displayResults(data.result);
            updateInventory(data.inventory);
            loadHistory();
        }
    } catch (error) {
        displayError('Failed to analyze image: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    
    if (!result.success) {
        resultsDiv.innerHTML = `
            <div class="result-item">
                <strong>Error:</strong>
                <p>${result.error || result.reasoning}</p>
            </div>
        `;
        return;
    }

    const detectedItemsHTML = result.detected_items && result.detected_items.length > 0
        ? `<div class="detected-items">
            ${result.detected_items.map(item => `<span class="item-tag">${item}</span>`).join('')}
           </div>`
        : '';

    resultsDiv.innerHTML = `
        <div class="result-item">
            <strong>Action Taken:</strong>
            <div class="action-badge action-${result.action.replace(/ /g, '_').toUpperCase()}">${result.action}</div>
        </div>
        <div class="result-item">
            <strong>AI Reasoning:</strong>
            <p>${result.reasoning}</p>
        </div>
        ${result.scene_analysis ? `
        <div class="result-item">
            <strong>Scene Analysis:</strong>
            <p>${result.scene_analysis}</p>
        </div>
        ` : ''}
        <div class="result-item">
            <strong>Detected Items:</strong>
            ${detectedItemsHTML || '<p>None</p>'}
        </div>
    `;
}

function displayError(error) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="result-item">
            <strong>Error:</strong>
            <p style="color: #f44336;">${error}</p>
        </div>
    `;
}

// Inventory functionality
function initializeInventory() {
    loadInventory();
    
    const clearBtn = document.getElementById('clearInventoryBtn');
    clearBtn.addEventListener('click', clearInventory);
}

async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        const inventory = await response.json();
        updateInventory(inventory);
    } catch (error) {
        console.error('Failed to load inventory:', error);
    }
}

function updateInventory(inventory) {
    const inventoryDiv = document.getElementById('inventory');
    
    inventoryDiv.innerHTML = inventory.map(slot => {
        const filled = slot.item !== null;
        const itemIcon = getItemIcon(slot.item);
        
        return `
            <div class="inventory-slot ${filled ? 'filled' : ''}" data-slot="${slot.slot_id}">
                <span class="slot-number">${slot.slot_id}</span>
                ${filled ? `
                    <button class="remove-item-btn" onclick="removeItem(${slot.slot_id})">×</button>
                    <div class="slot-item">${itemIcon}</div>
                    <div class="slot-name">${slot.item}</div>
                    <div class="slot-quantity">×${slot.quantity}</div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function getItemIcon(itemName) {
    if (!itemName) return '';
    
    const icons = {
        'key': '🔑',
        'sword': '⚔️',
        'shield': '🛡️',
        'potion': '🧪',
        'book': '📖',
        'torch': '🔦',
        'coin': '💰',
        'gem': '💎',
        'map': '🗺️',
        'food': '🍖',
        'water': '💧',
        'tool': '🔧',
        'weapon': '🗡️',
        'armor': '🦺',
        'backpack': '🎒',
    };
    
    // Check for partial matches
    const lowerName = itemName.toLowerCase();
    for (const [key, icon] of Object.entries(icons)) {
        if (lowerName.includes(key)) {
            return icon;
        }
    }
    
    return '📦';
}

async function clearInventory() {
    if (!confirm('Are you sure you want to clear all inventory?')) return;
    
    try {
        const response = await fetch('/api/inventory/clear', {
            method: 'POST'
        });
        const data = await response.json();
        updateInventory(data.inventory);
    } catch (error) {
        console.error('Failed to clear inventory:', error);
    }
}

async function removeItem(slotId) {
    try {
        const response = await fetch(`/api/inventory/remove/${slotId}`, {
            method: 'POST'
        });
        const data = await response.json();
        updateInventory(data.inventory);
    } catch (error) {
        console.error('Failed to remove item:', error);
    }
}

// History functionality
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        displayHistory(history);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function displayHistory(history) {
    const historyDiv = document.getElementById('history');
    
    if (history.length === 0) {
        historyDiv.innerHTML = '<p class="placeholder">No actions yet...</p>';
        return;
    }
    
    historyDiv.innerHTML = history.slice().reverse().map((action, index) => `
        <div class="history-item">
            <div class="action">
                <span class="action-badge action-${action.action.replace(/ /g, '_').toUpperCase()}">${action.action}</span>
            </div>
            <div class="reasoning">${action.reasoning}</div>
            ${action.detected_items && action.detected_items.length > 0 ? `
                <div class="detected-items">
                    ${action.detected_items.map(item => `<span class="item-tag">${item}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Loading overlay
function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    if (show) {
        loadingDiv.classList.remove('hidden');
    } else {
        loadingDiv.classList.add('hidden');
    }
}
