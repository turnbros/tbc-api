import random
import string
from util import kube_job, config
from util.enums import ResourceLifecycleStatus as status
from tenant_handler.tenant import Tenant

def run_terraform(tenant_name):

  tenant_domain = config.get_string_value("tenant", "tenant_domain")
  job_image = config.get_string_value("terraform", "job_image")
  job_namespace = config.get_string_value("terraform", "job_namespace")
  api_endpoint = config.get_string_value("terraform", "api_endpoint")

  job_body = kube_job.kube_create_job_object(
    name=f"tenant-apply-{tenant_name}-{''.join(random.sample(string.ascii_lowercase, 6))}",
    container_image=job_image,
    namespace=job_namespace,
    container_name="tenant-apply-container",
    env_vars={
      "TF_HTTP_ADDRESS": f"{api_endpoint}/tenant/{tenant_name}/workspace/state",
      "TF_HTTP_LOCK_ADDRESS": f"{api_endpoint}/tenant/{tenant_name}/workspace/state",
      "TF_HTTP_UNLOCK_ADDRESS": f"{api_endpoint}/tenant/{tenant_name}/workspace/state",
      "TF_VAR_tbc_api_endpoint": f"{api_endpoint}",
      "TF_VAR_tenant_name": tenant_name,
      "TF_VAR_tenant_domain": f"{tenant_name}.{tenant_domain}"
    })

  # Update the resource status of all the pending resources.
  for resource in Tenant(tenant_name).resource_manifest.resources:
    if resource.status is status.PENDING:
      resource.status = status.PROVISIONING

  api_response = kube_job.api_instance.create_namespaced_job(job_namespace, job_body, pretty=True)
  return api_response.metadata.labels["job-name"]
