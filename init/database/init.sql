CREATE TABLE reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    report_id VARCHAR(255) NOT NULL,
    org_name VARCHAR(255),
    email VARCHAR(255),
    date_begin TIMESTAMP NOT NULL,
    date_end TIMESTAMP NOT NULL,
    domain VARCHAR(255) NOT NULL,
    adkim CHAR(1),
    aspf CHAR(1),
    policy VARCHAR(50),
    subdomain_policy VARCHAR(50),
    pct INT,
    
    UNIQUE (report_id)
);

CREATE TABLE records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    report_id BIGINT NOT NULL,
    source_ip VARCHAR(45) NOT NULL, -- IPv4 or IPv6
    count INT NOT NULL,
    disposition VARCHAR(50),
    dkim_result VARCHAR(50),
    spf_result VARCHAR(50),
    header_from VARCHAR(255),

    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE TABLE auth_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    record_id BIGINT NOT NULL,
    auth_type VARCHAR(10) NOT NULL, -- 'dkim' or 'spf'
    domain VARCHAR(255) NOT NULL,
    result VARCHAR(50),

    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
);

CREATE INDEX idx_records_source_ip ON records(source_ip);
CREATE INDEX idx_records_report_id ON records(report_id);
CREATE INDEX idx_auth_results_record_id ON auth_results(record_id);
