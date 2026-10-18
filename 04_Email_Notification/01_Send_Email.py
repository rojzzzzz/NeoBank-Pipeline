# Databricks notebook source
# DBTITLE 1,Run and email parameters
dbutils.widgets.text("run_id", "252525")
job_run_id = dbutils.widgets.get("run_id")

dbutils.widgets.text("sender_email", "")
dbutils.widgets.text("recipient_email", "")
dbutils.widgets.text("support_email", "")

sender_email = dbutils.widgets.get("sender_email").strip()
recipient_email = dbutils.widgets.get("recipient_email").strip()
support_email = dbutils.widgets.get("support_email").strip()

if not sender_email or not recipient_email:
    raise ValueError("sender_email and recipient_email are required")

if not job_run_id:
    raise ValueError("job_run_id is required")

print("Job Run ID:", job_run_id)

# COMMAND ----------

# DBTITLE 1,Read execution summary
audit_df = spark.sql(f"""
SELECT
    p.table_id AS Table_ID,
    t.table_name AS Table_Name,
    p.layer AS Layer,
    p.start_time AS Start_Time,
    p.end_time AS End_Time,
    p.status AS Status,
    p.number_of_records AS Number_Of_Records,
    p.error_message AS Error_Message
FROM banking.metadata.pipeline_runs p
LEFT JOIN banking.metadata.tables t
    ON p.table_id = t.table_id
WHERE p.run_id = {job_run_id}
ORDER BY p.table_id
""")

display(audit_df)

# COMMAND ----------

# DBTITLE 1,Determine overall status
from pyspark.sql.functions import col

total = audit_df.count()
failed = audit_df.filter(col("status") != "SUCCESS").count()

if failed > 0:
    overall_status = "FAILED"
else:
    overall_status = "SUCCESS"

print("Total Tables:", total)
print("Failed Tables:", failed)
print("Overall Status:", overall_status)

# COMMAND ----------

# DBTITLE 1,Build email content
pdf = audit_df.toPandas()

html_table = pdf.to_html(
    index=False,
    border=1,
    justify="center",
    classes="table table-striped"
)

body = f"""
<html>
<body>

<p><b>This is an auto-generated email. Please do not reply.</b></p>

<p>
End-to-end run for <b>Source → Bronze → Silver → Gold</b> layers has completed.
Below is the execution summary:
</p>

<br>

{html_table}

<br>

<p>
For any queries please reach out to:
<b>{support_email or "Banking Support Team"}</b>
</p>

<br>

<p>
Thanks<br>
<b>Banking Support Team</b>
</p>

</body>
</html>
"""

subject = f"NeoBank | {overall_status} | End to End Run"

# COMMAND ----------

# DBTITLE 1,Configure email delivery
gmail_api_key = dbutils.secrets.get(
            scope="banking-scope",
            key="gmail_api_key"
        )

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = sender_email
APP_PASSWORD = gmail_api_key

to_email = recipient_email

msg = MIMEMultipart()
msg["From"] = EMAIL
msg["To"] = to_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "html"))

# COMMAND ----------

# DBTITLE 1,Send notification
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)

    print("✅ Email sent successfully!")

except Exception as e:
    print("❌ Error sending email:", e)
