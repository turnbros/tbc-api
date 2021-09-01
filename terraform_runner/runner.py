import random
import string
from util import kube_job, config
from util.enums import ResourceLifecycleStatus as status
from tenant_handler.tenant import Tenant

def run_terraform(tenant_name):

  opnsense_url = config.get_string_value("opnsense", "opnsense_url")
  opnsense_key = config.get_string_value("opnsense", "opnsense_key")
  opnsense_secret = config.get_string_value("opnsense", "opnsense_secret")
  opnsense_allow_unverified_tls = config.get_string_value("opnsense", "opnsense_allow_unverified_tls")
  nodeport_alias_name = config.get_string_value("opnsense", "nodeport_alias_name")
  nodeport_alias_uuid = config.get_string_value("opnsense", "nodeport_alias_uuid")

  cluster_endpoint = config.get_string_value("kubernetes", "cluster_endpoint")
  cluster_cert = config.get_string_value("kubernetes", "cluster_cert")
  client_key = config.get_string_value("kubernetes", "client_key")
  client_cert = config.get_string_value("kubernetes", "client_cert")

  tenant_domain = config.get_string_value("tenant", "tenant_domain")

  log_level = config.get_string_value("terraform", "log_level")
  job_image = config.get_string_value("terraform", "job_image")
  job_namespace = config.get_string_value("terraform", "job_namespace")
  api_endpoint = config.get_string_value("terraform", "api_endpoint")

  job_body = kube_job.kube_create_job_object(
    name=f"tenant-apply-{tenant_name}-{''.join(random.sample(string.ascii_lowercase, 6))}",
    container_image=job_image,
    namespace=job_namespace,
    container_name="tenant-apply-container",
    env_vars={
      "TF_HTTP_ADDRESS": f"{api_endpoint}/tenants/{tenant_name}/workspace/state",
      "TF_HTTP_LOCK_ADDRESS": f"{api_endpoint}/tenants/{tenant_name}/workspace/state",
      "TF_HTTP_UNLOCK_ADDRESS": f"{api_endpoint}/tenants/{tenant_name}/workspace/state",
      "TF_VAR_kube_host": f"{cluster_endpoint}",
      "TF_VAR_kube_cluster_ca_cert": f"{cluster_cert}",
      "TF_VAR_kube_client_key": f"{client_key}",
      "TF_VAR_kube_client_cert": f"{client_cert}",
      "TF_VAR_tbc_api_endpoint": f"{api_endpoint}",
      "TF_VAR_tenant_name": tenant_name,
      "TF_VAR_tenant_domain": f"{tenant_name}.{tenant_domain}",
      "OPNSENSE_URL": f"{opnsense_url}",
      "OPNSENSE_KEY": f"{opnsense_key}",
      "OPNSENSE_SECRET": f"{opnsense_secret}",
      "OPNSENSE_ALLOW_UNVERIFIED_TLS": f"{opnsense_allow_unverified_tls}",
      "TF_VAR_nodeport_alias_name": nodeport_alias_name,
      "TF_VAR_nodeport_alias_uuid": nodeport_alias_uuid,
      "TF_LOG": log_level
    })

  # Update the resource status of all the pending resources.
  for resource in Tenant(tenant_name).resource_manifest.resources:
    if resource.status is status.PENDING:
      resource.status = status.PROVISIONING

  api_response = kube_job.api_instance.create_namespaced_job(job_namespace, job_body, pretty=True)
  return api_response.metadata.labels["job-name"]
