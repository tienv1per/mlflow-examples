# Databricks notebook source
# MAGIC %run ../../Versions

# COMMAND ----------

def get_notebook_tag(tag):
    tag = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get(tag)
    return None if tag.isEmpty() else tag.get()

# COMMAND ----------

user = get_notebook_tag("user")
host_name = get_notebook_tag("browserHostName")
base_dir_fuse = f"/dbfs/tmp/{user}/mlflow_demo"

print("user:",user)
print("host_name:",host_name)
print("base_dir_fuse:",base_dir_fuse)

# COMMAND ----------

import os
import requests

def download_file(data_uri, data_path):
    if os.path.exists(data_path):
        print("File {data_path} already exists")
    else:
        print(f"Downloading {data_uri} to {data_path}")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        rsp = requests.get(data_uri)
        with open(data_path, "w") as f:
            f.write(rsp.text)

# COMMAND ----------

def download_wine_file():
    data_path = f"{base_dir_fuse}/wine-quality.csv"
    data_uri = "https://raw.githubusercontent.com/mlflow/mlflow/master/examples/sklearn_elasticnet_wine/wine-quality.csv"
    download_file(data_uri, data_path)
    return data_path

# COMMAND ----------

def display_run_uri(experiment_id, run_id):
    uri = f"https://{host_name}/#mlflow/experiments/{experiment_id}/runs/{run_id}"
    displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_uri(model_name):
    uri = f"https://{host_name}/#mlflow/models/{model_name}"
    displayHTML("""<b>Registered Model URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_version_uri(model_name, version):
    uri = f"https://{host_name}/#mlflow/models/{model_name}/versions/{version}"
    displayHTML("""<b>Registered Model Version URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_experiment_info(experiment):
  host_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName").get()
  uri = f"https://{host_name}/#mlflow/experiments/{experiment.experiment_id}"
  displayHTML(f"""
   <table cellpadding=5 cellspacing=0 border=1 bgcolor="#feeeee">
   <tr><td colspan=2><b><i>Experiment</i></b></td></tr>
   <tr><td>UI link</td><td><a href="{uri}">{uri}</a></td></tr>
   <tr><td>Name</td><td>{experiment.name}</td></tr>
   <tr><td>ID</td><td>{experiment.experiment_id}</td></tr>
   </table>
   """)

# COMMAND ----------

def to_int(x):
  return None if x is None or x=="" else int(x)

# COMMAND ----------

def to_list_int(str, delimiter=" "): 
    return [ int(x) for x in str.split(delimiter)]

# COMMAND ----------

colLabel = "quality"
colPrediction = "prediction"
colFeatures = "features"

# COMMAND ----------

from mlflow.exceptions import RestException

def delete_registered_model(client, model_name):
    """ Delete a model and all its versions """
    try:
        versions = client.get_latest_versions(model_name)
        print(f"Deleting {len(versions)} versions for model '{model_name}'")
        for v in versions:
            print(f"  version={v.version} status={v.status} stage={v.current_stage} run_id={v.run_id}")
            client.transition_model_version_stage (model_name, v.version, "Archived") # 1.9.0
            client.delete_model_version(model_name, v.version)
        client.delete_registered_model(model_name)
    except RestException:
        pass