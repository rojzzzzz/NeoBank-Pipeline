# Databricks notebook source
# DBTITLE 1,Connection settings
sqlserver_host = ""
sqlserver_port = ""
sqlserver_database = ""
sqlserver_user = ""
sqlserver_password = ""

secret_scope_name = "banking-scope"

secret_key_name = "sqlserver-connection-json"

# COMMAND ----------

# DBTITLE 1,Build connection configuration
import json

connection_config = {
    "host": sqlserver_host,
    "port": sqlserver_port,
    "database": sqlserver_database,
    "user": sqlserver_user,
    "password": sqlserver_password,
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}

connection_json = json.dumps(connection_config)

print("Connection configuration generated.")

# COMMAND ----------

# DBTITLE 1,Databricks API context
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()

api_url  = ctx.apiUrl().getOrElse(None)
api_token = ctx.apiToken().getOrElse(None)

# COMMAND ----------

# DBTITLE 1,Create secret scope
import requests
import json

DATABRICKS_INSTANCE = api_url
DATABRICKS_TOKEN = api_token

scope_name = secret_scope_name
backend_type = "DATABRICKS"

url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/scopes/create"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope_name
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print(f"Secret scope '{scope_name}' created successfully.")
else:
    print("Failed to create secret scope.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

# COMMAND ----------

# DBTITLE 1,Store SQL Server credentials
import requests
import json

scope = secret_scope_name
secret_key = secret_key_name
secret_value = connection_json

url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/put"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope,
    "key": secret_key,
    "string_value": secret_value
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print(f"Secret '{secret_key}' created successfully in scope '{scope}'.")
else:
    print("Failed to create secret.")
    print("Status:", response.status_code)
    print("Response:", response.text)

# COMMAND ----------

# DBTITLE 1,Verify secret retrieval
try:
    retrieved_json = dbutils.secrets.get(
        scope=secret_scope_name,
        key=secret_key_name
    )

    print("Secret retrieved successfully.")

    parsed = json.loads(retrieved_json)
    print("Secret JSON parsed successfully.")

except Exception as e:
    print("Secret verification failed:")
    print(str(e))

# COMMAND ----------

# DBTITLE 1,Store email credentials
import requests
import json

scope = secret_scope_name
secret_key = 'gmail_api_key'
secret_value = '<api_key>'

url = f"{DATABRICKS_INSTANCE}/api/2.0/secrets/put"

headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "scope": scope,
    "key": secret_key,
    "string_value": secret_value
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print(f"Secret '{secret_key}' created successfully in scope '{scope}'.")
else:
    print("Failed to create secret.")
    print("Status:", response.status_code)
    print("Response:", response.text)
