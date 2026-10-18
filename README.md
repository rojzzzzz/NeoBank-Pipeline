# NeoBank | Data Engineering Pipeline

NeoBank is a hands-on data engineering project based on a banking scenario. Built with **Databricks and PySpark**, it brings together data from Azure SQL Server and CSV files, processes it through a **Medallion Architecture**, and makes it available for reporting and analysis.

## Pipeline Architecture

![Pipeline architecture](<pipeline_structure.png>)

The pipeline is organized into three layers:

- **Bronze:** Ingests banking tables from Azure SQL Server using Spark JDBC and external CSV files using Databricks Auto Loader. The raw data is kept for later processing.
- **Silver:** Loads and updates the data using different load strategies: `MERGE` (upsert) for customers and accounts, `append` for transactions and gateway logs, and `overwrite` for branch reference data. Watermarks help identify new or updated records during incremental loads.
- **Gold:** Creates five business-focused datasets: `branch_performance`, `customer_360`, `daily_bank_kpi`, `risk_customer_summary`, and `transaction_channel_summary`.

## Data Model

![Source tables and data model](<source_tables.png>)

The source data includes four SQL tables (`branches`, `customers`, `accounts`, and `transactions`) and two CSV datasets (`credit_bureau_reports` and `payment_gateway_logs`).

## Pipeline Management

Instead of defining every table's processing rules separately, the pipeline uses **metadata tables** to store configuration and track execution:

- `tables` and `table_parameters` define the source, load strategy, keys, and execution order.
- `table_watermarks` tracks incremental load progress.
- `pipeline_runs` records execution status, processed rows, and errors.

A **Databricks multi-task job** coordinates the workflow, running independent ingestion tasks in parallel before executing the Gold transformations. The project also includes email notifications, **Unity Catalog** for organizing data across layers, and **Secret Scopes** for credentials.

The Gold datasets are used in **Databricks Dashboards** and **Databricks Genie** to explore banking metrics through visualizations and natural-language questions.

## Execution order

1. Run `01_Setup_Metadata/01_Setup_Metadata.sql` to initialize metadata and storage.
2. Configure credentials through `02_Source_to_Silver/00_Setup_Secret_Scope.py` in your private workspace. Keep the repository values blank or as placeholders.
3. Run `02_Source_to_Silver/01_Read_Tables_List.py.py` with the desired `source_system`.
4. For each source table, run `02_Read_Table_Parameters.py`, `03_Source_to_Bronze.py`, and `04_Bronze_to_Silver.py` in order.
5. Read metadata with `source_system = silver` and run `03_Silver_to_Gold/01_Silver_to_Gold_Driver.py` for each Gold table. Keep `gold_transformations` beside the driver notebook.
6. Run `04_Email_Notification/01_Send_Email.py` after processing, using the same `run_id`. Set the required `sender_email` and `recipient_email` widgets; `support_email` is optional. The sender must match the Gmail account associated with the stored SMTP credentials.

---

*Learning project based on [DataBeli's Databricks project](https://youtu.be/aEGan35iBbE?si=KeTmua_yw0ED-Elz).*
