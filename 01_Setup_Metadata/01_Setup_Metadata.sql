-- Databricks notebook source
-- DBTITLE 1,Create catalog and metadata schema
CREATE CATALOG IF NOT EXISTS banking;
CREATE SCHEMA IF NOT EXISTS banking.metadata;

-- COMMAND ----------

-- DBTITLE 1,Table registry
CREATE TABLE IF NOT EXISTS banking.metadata.tables (
    table_id            INT,
    table_name          STRING,
    source_system       STRING,
    source_schema       STRING,
    source_table        STRING,
    source_path         STRING,
    target_layer        STRING,
    bronze_schema       STRING,
    silver_schema       STRING,
    gold_schema         STRING,
    active_flag         BOOLEAN,
    load_order          INT,
    created_at          TIMESTAMP
)
USING DELTA;

-- COMMAND ----------

-- DBTITLE 1,Table parameters
CREATE TABLE IF NOT EXISTS banking.metadata.table_parameters (
    table_id            INT,
    parameter_name      STRING,        -- load_type / primary_key / watermark_column
    parameter_value     STRING,
    created_at          TIMESTAMP
)
USING DELTA;

-- COMMAND ----------

-- DBTITLE 1,Table watermarks
CREATE TABLE IF NOT EXISTS banking.metadata.table_watermarks (
    table_id                INT,
    last_watermark_value    STRING,
    last_updated_at         TIMESTAMP,
    last_run_id             BIGINT
)
USING DELTA
PARTITIONED BY (table_id);

-- COMMAND ----------

-- DBTITLE 1,Pipeline audit table
CREATE TABLE IF NOT EXISTS banking.metadata.pipeline_runs (
    run_id              BIGINT,
    table_id            INT,
    layer               STRING,
    start_time          TIMESTAMP,
    end_time            TIMESTAMP,
    status              STRING,
    number_of_records     BIGINT,
    error_message       STRING
)
USING DELTA
PARTITIONED BY (table_id);

-- COMMAND ----------

-- DBTITLE 1,Source schema and volume
CREATE SCHEMA IF NOT EXISTS banking.source;

CREATE VOLUME IF NOT EXISTS banking.source.volume;

-- COMMAND ----------

-- DBTITLE 1,Register source tables
INSERT INTO banking.metadata.tables VALUES
(1, 'customers', 'sqlserver', 'banking', 'customers', NULL, 'silver', 'bronze', 'silver', NULL, TRUE, 1, current_timestamp()),

(2, 'accounts', 'sqlserver', 'banking', 'accounts', NULL, 'silver', 'bronze', 'silver', NULL, TRUE, 2, current_timestamp()),

(3, 'transactions', 'sqlserver', 'banking', 'transactions', NULL, 'silver', 'bronze', 'silver', NULL, TRUE, 3, current_timestamp()),

(4, 'branches', 'sqlserver', 'banking', 'branches', NULL, 'silver', 'bronze', 'silver', NULL, TRUE, 4, current_timestamp()),

(5, 'credit_bureau_reports', 'blob', NULL, NULL,
 '/Volumes/banking/source/volume/credit_bureau_reports/', 'silver',
 'bronze', 'silver', NULL, TRUE, 5, current_timestamp()),

(6, 'payment_gateway_logs', 'blob', NULL, NULL,
 '/Volumes/banking/source/volume/payment_gateway_logs/', 'silver',
 'bronze', 'silver', NULL, TRUE, 6, current_timestamp());

-- COMMAND ----------

-- DBTITLE 1,Configure load parameters
INSERT INTO banking.metadata.table_parameters VALUES

(1, 'load_type', 'MERGE', current_timestamp()),
(1, 'primary_key', 'customer_id', current_timestamp()),
(1, 'watermark_column', 'updated_at', current_timestamp()),

(2, 'load_type', 'MERGE', current_timestamp()),
(2, 'primary_key', 'account_id', current_timestamp()),
(2, 'watermark_column', 'updated_at', current_timestamp()),

(3, 'load_type', 'APPEND', current_timestamp()),
(3, 'primary_key', 'txn_id', current_timestamp()),
(3, 'watermark_column', 'txn_timestamp', current_timestamp()),

(4, 'load_type', 'FULL', current_timestamp()),
(4, 'primary_key', 'branch_code', current_timestamp()),

(5, 'load_type', 'MERGE', current_timestamp()),
(5, 'primary_key', 'customer_id', current_timestamp()),
(5, 'watermark_column', 'bureau_pull_date', current_timestamp()),

(6, 'load_type', 'APPEND', current_timestamp()),
(6, 'primary_key', 'txn_id', current_timestamp()),
(6, 'watermark_column', 'processed_timestamp', current_timestamp());

-- COMMAND ----------

-- DBTITLE 1,Initialize watermarks
INSERT INTO banking.metadata.table_watermarks VALUES
(1, '1900-01-01 00:00:00', current_timestamp(), NULL),
(2, '1900-01-01 00:00:00', current_timestamp(), NULL),
(3, '1900-01-01 00:00:00', current_timestamp(), NULL),
(5, '1900-01-01 00:00:00', current_timestamp(), NULL),
(6, '1900-01-01 00:00:00', current_timestamp(), NULL);

-- COMMAND ----------

-- DBTITLE 1,Register customer overview
INSERT INTO banking.metadata.tables
VALUES (
    7,
    'customer_360',
    'silver',
    NULL,
    NULL,
    NULL,
    'gold',
    NULL,
    NULL,
    'gold',
    TRUE,
    1,
    current_timestamp()
);

-- COMMAND ----------

-- DBTITLE 1,Register operational summaries
INSERT INTO banking.metadata.tables
VALUES
(
8,
'branch_performance',
'silver',
NULL,
NULL,
NULL,
'gold',
NULL,
NULL,
'gold',
TRUE,
2,
current_timestamp()
),

(
9,
'transaction_channel_summary',
'silver',
NULL,
NULL,
NULL,
'gold',
NULL,
NULL,
'gold',
TRUE,
3,
current_timestamp()
),

(
10,
'daily_bank_kpi',
'silver',
NULL,
NULL,
NULL,
'gold',
NULL,
NULL,
'gold',
TRUE,
4,
current_timestamp()
);

-- COMMAND ----------

-- DBTITLE 1,Register risk summary
INSERT INTO banking.metadata.tables
VALUES (
    11,
    'risk_customer_summary',
    'silver',
    NULL,
    NULL,
    NULL,
    'gold',
    NULL,
    NULL,
    'gold',
    TRUE,
    1,
    current_timestamp()
);
