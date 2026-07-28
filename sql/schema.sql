DROP TABLE IF EXISTS capa_actions;
DROP TABLE IF EXISTS deviations;
DROP TABLE IF EXISTS microbial_results;
DROP TABLE IF EXISTS test_results;
DROP TABLE IF EXISTS batches;

-- 1. Batches Table
CREATE TABLE batches (
    batch_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    production_line TEXT NOT NULL,
    batch_date TEXT NOT NULL,    -- Expected Format: YYYY-MM-DD
    month_year TEXT NOT NULL,    -- Expected Format: YYYY-MM (For Trend Queries)
    shift TEXT NOT NULL,
    batch_status TEXT NOT NULL   -- e.g., 'PASS', 'FAIL', 'IN_PROGRESS'
);

-- 2. Physicochemical / General Test Results Table
CREATE TABLE test_results (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    parameter TEXT NOT NULL,
    result_value REAL,
    specification_limit REAL,
    result_status TEXT NOT NULL, -- 'Pass' or 'Fail'
    test_date TEXT NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

-- 3. Microbial Test Results Table
CREATE TABLE microbial_results (
    micro_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    test_type TEXT NOT NULL,
    count_cfu INTEGER,
    limit_cfu INTEGER,
    sample_source TEXT,
    result_status TEXT NOT NULL, -- 'Pass' or 'Fail'
    test_date TEXT NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

-- 4. Deviations Table
CREATE TABLE deviations (
    deviation_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    deviation_type TEXT NOT NULL,
    severity TEXT NOT NULL,       -- e.g., 'Critical', 'Major', 'Minor'
    root_cause_category TEXT,     -- e.g., 'Human Error', 'Equipment Failure'
    root_cause_details TEXT,
    detected_by TEXT,             -- e.g., 'QA', 'Operator'
    capa_raised TEXT NOT NULL,    -- 'Yes' or 'No'
    deviation_date TEXT NOT NULL,
    status TEXT NOT NULL,         -- e.g., 'Open', 'Closed'
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

-- 5. CAPA Actions Table
CREATE TABLE capa_actions (
    capa_id TEXT PRIMARY KEY,
    deviation_id TEXT NOT NULL,
    capa_type TEXT NOT NULL,
    assigned_department TEXT,
    target_date TEXT NOT NULL,
    closure_date TEXT,
    tat_days INTEGER,             -- Turnaround time calculated days
    on_time TEXT,                 -- 'Yes' or 'No'
    effectiveness_status TEXT,    -- e.g., 'Effective', 'Ineffective'
    FOREIGN KEY (deviation_id) REFERENCES deviations(deviation_id)
);