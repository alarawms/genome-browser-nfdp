-- Saudi Livestock Genome Browser Database

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Species table
CREATE TABLE species (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(200),
    assembly VARCHAR(100),
    genome_size_gb NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QTL table
CREATE TABLE qtls (
    id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(id) ON DELETE CASCADE,
    chromosome VARCHAR(50) NOT NULL,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    trait VARCHAR(200),
    confidence NUMERIC,
    reference TEXT,
    pmid INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_qtls_species ON qtls(species_id);
CREATE INDEX idx_qtls_chromosome ON qtls(chromosome);
CREATE INDEX idx_qtls_trait ON qtls USING gin(trait gin_trgm_ops);

-- Traits table
CREATE TABLE traits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(100),
    saudi_relevance BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Saudi breeds table
CREATE TABLE saudi_breeds (
    id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(id) ON DELETE CASCADE,
    breed_name VARCHAR(200) NOT NULL,
    arabian_name TEXT,
    region VARCHAR(100),
    population_size INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial species
INSERT INTO species (name, scientific_name, assembly, genome_size_gb) VALUES
    ('Sheep', 'Ovis aries', 'Oar_rambouillet_v1.0', 2.7),
    ('Camel', 'Camelus dromedarius', 'CamDro2', 2.5),
    ('Cattle', 'Bos taurus', 'ARS-UCD1.2', 2.7),
    ('Goat', 'Capra hircus', 'CHIR_1.0', 2.7),
    ('Horse', 'Equus caballus', 'EquCab3.0', 2.7);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
