/**
 * AR Viewer - Dynamic Model Loading
 *
 * Fetches 3D model metadata from Supabase and loads it into Model-Viewer.
 * Also tracks analytics (views, AR activations).
 */

// ============================================================
// Configuration
// ============================================================

// Supabase Configuration
// These should match the values in your .env file
const SUPABASE_URL = 'https://kqhhvhrwfaygklrvwiul.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxaGh2aHJ3ZmF5Z2tscnZ3aXVsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NTMyMzMsImV4cCI6MjA4NTUyOTIzM30.EybsDJxTf668vX7dhFESm6YyaWnMMAqu-bsiw7aTpXs';

// DOM Elements
const modelViewer = document.getElementById('modelViewer');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const productInfo = document.getElementById('productInfo');
const productName = document.getElementById('productName');
const productCategory = document.getElementById('productCategory');
const productPrice = document.getElementById('productPrice');
const productDescription = document.getElementById('productDescription');
const disclaimer = document.getElementById('disclaimer');

// ============================================================
// Main Initialization
// ============================================================

// Get model ID from URL parameter
const urlParams = new URLSearchParams(window.location.search);
const modelId = urlParams.get('model');

console.log('AR Viewer initialized');
console.log('Model ID from URL:', modelId);

// Validate model ID parameter
if (!modelId) {
    showError('No model specified in URL. Please scan a valid QR code.');
} else {
    loadModel(modelId);
}

// ============================================================
// Model Loading
// ============================================================

/**
 * Load 3D model from Supabase database.
 * @param {string} modelId - The model ID to load
 */
async function loadModel(modelId) {
    console.log(`Loading model: ${modelId}`);

    // Check Supabase configuration
    if (SUPABASE_URL === 'YOUR_SUPABASE_URL' || SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
        showError(
            'Supabase credentials not configured. ' +
            'Please update SUPABASE_URL and SUPABASE_ANON_KEY in fetch_models.js'
        );
        return;
    }

    try {
        // Query Supabase for model metadata
        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/models?model_id=eq.${modelId}&select=*`,
            {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API response:', data);

        // Check if model exists
        if (!data || data.length === 0) {
            throw new Error(`Model '${modelId}' not found in database`);
        }

        const model = data[0];
        console.log('Model data:', model);

        // Load model into viewer
        displayModel(model);

        // Track view analytics
        trackAnalytics(modelId, 'view');

    } catch (err) {
        console.error('Error loading model:', err);
        showError(`Failed to load model: ${err.message}`);
    }
}

/**
 * Display the model in Model-Viewer.
 * @param {object} model - Model metadata from database
 */
function displayModel(model) {
    console.log('Displaying model:', model.model_id);

    // Set model source
    modelViewer.src = model.public_url;

    // Update page title
    document.title = `${model.product_name} - AR View`;

    // Update product info
    productName.textContent = model.product_name;
    productCategory.textContent = model.category.toUpperCase();

    if (model.price) {
        const currency = model.currency || 'USD';
        productPrice.textContent = `${currency} ${model.price.toFixed(2)}`;
        productPrice.style.display = 'block';
    } else {
        productPrice.style.display = 'none';
    }

    if (model.description) {
        productDescription.textContent = model.description;
        productDescription.style.display = 'block';
    } else {
        productDescription.style.display = 'none';
    }

    // Show UI elements
    productInfo.classList.remove('hidden');
    disclaimer.classList.remove('hidden');
}

// ============================================================
// Event Handlers
// ============================================================

// Hide loading when model loads successfully
modelViewer.addEventListener('load', () => {
    console.log('Model loaded successfully');
    loading.classList.add('hidden');
    modelViewer.classList.remove('hidden');
});

// Handle model load errors
modelViewer.addEventListener('error', (event) => {
    console.error('Model load error:', event);
    showError('Failed to load 3D model. The file may be corrupted or unavailable.');
});

// Track when user enters AR mode
modelViewer.addEventListener('ar-status', (event) => {
    console.log('AR status:', event.detail.status);

    if (event.detail.status === 'session-started') {
        console.log('User entered AR mode');
        const modelId = urlParams.get('model');
        if (modelId) {
            trackAnalytics(modelId, 'ar_activated');
        }
    }
});

// Handle progress updates
modelViewer.addEventListener('progress', (event) => {
    const progressBar = modelViewer.querySelector('.update-bar');
    if (progressBar) {
        const progress = event.detail.totalProgress * 100;
        progressBar.style.width = `${progress}%`;
        console.log(`Loading progress: ${progress.toFixed(0)}%`);
    }
});

// ============================================================
// Analytics
// ============================================================

/**
 * Track analytics events (views, AR activations).
 * @param {string} modelId - The model ID
 * @param {string} eventType - Event type ('view', 'ar_activated', 'qr_scanned')
 */
async function trackAnalytics(modelId, eventType) {
    console.log(`Tracking analytics: ${eventType} for ${modelId}`);

    try {
        // Detect device type and OS
        const userAgent = navigator.userAgent;
        const deviceType = /Mobile|Android|iPhone|iPad/.test(userAgent) ? 'mobile' : 'desktop';
        const osName = getOSName(userAgent);

        // Generate session ID (simple implementation)
        let sessionId = localStorage.getItem('ar_session_id');
        if (!sessionId) {
            sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('ar_session_id', sessionId);
        }

        // Send analytics to Supabase
        await fetch(
            `${SUPABASE_URL}/rest/v1/analytics`,
            {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify({
                    model_id: modelId,
                    event_type: eventType,
                    user_agent: userAgent,
                    device_type: deviceType,
                    os_name: osName,
                    session_id: sessionId
                })
            }
        );

        console.log('Analytics tracked successfully');
    } catch (err) {
        console.warn('Failed to track analytics:', err);
        // Don't fail the app if analytics fail
    }
}

/**
 * Detect operating system from user agent.
 * @param {string} userAgent - Navigator user agent string
 * @returns {string} OS name
 */
function getOSName(userAgent) {
    if (/iPhone|iPad|iPod/.test(userAgent)) return 'iOS';
    if (/Android/.test(userAgent)) return 'Android';
    if (/Windows/.test(userAgent)) return 'Windows';
    if (/Mac/.test(userAgent)) return 'macOS';
    if (/Linux/.test(userAgent)) return 'Linux';
    return 'Unknown';
}

// ============================================================
// Error Handling
// ============================================================

/**
 * Show error message to user.
 * @param {string} message - Error message to display
 */
function showError(message) {
    console.error('Error:', message);

    loading.classList.add('hidden');
    modelViewer.classList.add('hidden');
    errorMessage.textContent = message;
    error.classList.remove('hidden');
}

// ============================================================
// Utility Functions
// ============================================================

/**
 * Copy AR viewer URL to clipboard (for sharing).
 */
function copyToClipboard() {
    const url = window.location.href;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url)
            .then(() => {
                alert('Link copied to clipboard!');
            })
            .catch(err => {
                console.error('Failed to copy:', err);
            });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = url;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('Link copied to clipboard!');
    }
}

// ============================================================
// Debug Information (Development Only)
// ============================================================

console.log('='.repeat(60));
console.log('AR VIEWER DEBUG INFO');
console.log('='.repeat(60));
console.log('URL:', window.location.href);
console.log('Model ID:', modelId);
console.log('User Agent:', navigator.userAgent);
console.log('Device Type:', /Mobile|Android|iPhone|iPad/.test(navigator.userAgent) ? 'mobile' : 'desktop');
console.log('AR Supported:', 'xr' in navigator ? 'Yes' : 'No');
console.log('='.repeat(60));
