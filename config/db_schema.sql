-- AR Platform Database Schema
-- PostgreSQL (Supabase)

-- ============================================================
-- TABLE: clients
-- Stores client/restaurant information
-- ============================================================
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(50) PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: models
-- Stores 3D model metadata
-- ============================================================
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    description TEXT,
    client_id VARCHAR(50) REFERENCES clients(client_id) ON DELETE CASCADE,

    -- File information
    public_url TEXT NOT NULL,
    file_size_bytes BIGINT,
    file_size_mb DECIMAL(10, 2),
    storage_path VARCHAR(500),

    -- Technical details
    polygon_count INTEGER,
    texture_resolution VARCHAR(50),
    file_format VARCHAR(20) DEFAULT 'GLB',

    -- Metadata
    tags TEXT[],  -- Array of tags
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by VARCHAR(100) DEFAULT 'system'
);

-- ============================================================
-- TABLE: analytics
-- Tracks model views and interactions
-- ============================================================
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(50) REFERENCES models(model_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,  -- 'view', 'ar_activated', 'qr_scanned'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    device_type VARCHAR(50),  -- 'mobile', 'tablet', 'desktop'
    os_name VARCHAR(50),  -- 'iOS', 'Android', 'Windows', etc.
    country_code VARCHAR(10),
    session_id VARCHAR(100)
);

-- ============================================================
-- INDEXES for performance
-- ============================================================

-- Index on model_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_models_model_id ON models(model_id);

-- Index on category for filtering
CREATE INDEX IF NOT EXISTS idx_models_category ON models(category);

-- Index on client_id for client-specific queries
CREATE INDEX IF NOT EXISTS idx_models_client_id ON models(client_id);

-- Index on created_at for sorting by upload date
CREATE INDEX IF NOT EXISTS idx_models_created_at ON models(created_at DESC);

-- Index on analytics model_id for aggregation
CREATE INDEX IF NOT EXISTS idx_analytics_model_id ON analytics(model_id);

-- Index on analytics timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp DESC);

-- Composite index for analytics queries
CREATE INDEX IF NOT EXISTS idx_analytics_model_event ON analytics(model_id, event_type);

-- ============================================================
-- FUNCTIONS: Auto-update timestamp
-- ============================================================

-- Function to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for models table
DROP TRIGGER IF EXISTS update_models_updated_at ON models;
CREATE TRIGGER update_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for clients table
DROP TRIGGER IF EXISTS update_clients_updated_at ON clients;
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- SAMPLE DATA (for testing)
-- ============================================================

-- Insert a test client
INSERT INTO clients (client_id, client_name, business_type, contact_email)
VALUES ('TEST_CLIENT', 'Test Restaurant', 'restaurant', 'test@example.com')
ON CONFLICT (client_id) DO NOTHING;

-- ============================================================
-- VIEWS (for easier querying)
-- ============================================================

-- View: Model statistics
CREATE OR REPLACE VIEW model_stats AS
SELECT
    m.model_id,
    m.product_name,
    m.category,
    m.client_id,
    COUNT(DISTINCT a.id) FILTER (WHERE a.event_type = 'view') AS total_views,
    COUNT(DISTINCT a.id) FILTER (WHERE a.event_type = 'ar_activated') AS total_ar_activations,
    COUNT(DISTINCT a.id) FILTER (WHERE a.event_type = 'qr_scanned') AS total_qr_scans,
    MAX(a.timestamp) AS last_viewed,
    m.created_at AS uploaded_at
FROM models m
LEFT JOIN analytics a ON m.model_id = a.model_id
GROUP BY m.model_id, m.product_name, m.category, m.client_id, m.created_at;

-- ============================================================
-- COMMENTS (documentation)
-- ============================================================

COMMENT ON TABLE models IS 'Stores 3D model metadata and file information';
COMMENT ON TABLE clients IS 'Stores client/restaurant information';
COMMENT ON TABLE analytics IS 'Tracks model views and user interactions';
COMMENT ON COLUMN models.model_id IS 'Unique identifier for the model (e.g., BURGER_001)';
COMMENT ON COLUMN models.public_url IS 'Public Supabase Storage URL for the GLB file';
COMMENT ON COLUMN analytics.event_type IS 'Type of event: view, ar_activated, or qr_scanned';
