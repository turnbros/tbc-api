import hashlib
import string
import random
import logging
import yaml
import sys, os, time
from kubernetes import client, config, utils
import kubernetes.client
from kubernetes.client.rest import ApiException

# Set logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

api_cert = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJrRENDQVRlZ0F3SUJBZ0lJWUwySlNheFIxODh3Q2dZSUtvWkl6ajBFQXdJd0l6RWhNQjhHQTFVRUF3d1kKYXpOekxXTnNhV1Z1ZEMxallVQXhOakUxTVRZMU16azVNQjRYRFRJeE1ETXdPREF4TURNeE9Wb1hEVEl5TURNdwpPREF4TURNeE9Wb3dNREVYTUJVR0ExVUVDaE1PYzNsemRHVnRPbTFoYzNSbGNuTXhGVEFUQmdOVkJBTVRESE41CmMzUmxiVHBoWkcxcGJqQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlBd0VIQTBJQUJBZUREZERJcFZLa21QUTMKQ2kwdzYwQ3Z4Zko2NmRhRTgxZnQvQ1lDUUZQZk15NUMwVXkrRkVnaDJya3o0T29TOVhjRU1hb0ZhQXkzaVR4bQpwdFQ5VlVpalNEQkdNQTRHQTFVZER3RUIvd1FFQXdJRm9EQVRCZ05WSFNVRUREQUtCZ2dyQmdFRkJRY0RBakFmCkJnTlZIU01FR0RBV2dCU1hQdUg0cTg3eE00cGMrbUVZN2JHQmtheGNaakFLQmdncWhrak9QUVFEQWdOSEFEQkUKQWlBNSt5WTF1a2RkQkZkdVJ5SzN0WUY3c0pkT1NaNlV0ZmNXYTJSZ2NKQlBVd0lnRW1LaEdMSUEyWjdvYXFwSQpibDVCalZvNGhDcVhsaE1hQUJWcTJyaGk3T0E9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0KLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJkakNDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdFkyeHAKWlc1MExXTmhRREUyTVRVeE5qVXpPVGt3SGhjTk1qRXdNekE0TURFd016RTVXaGNOTXpFd016QTJNREV3TXpFNQpXakFqTVNFd0h3WURWUVFEREJock0zTXRZMnhwWlc1MExXTmhRREUyTVRVeE5qVXpPVGt3V1RBVEJnY3Foa2pPClBRSUJCZ2dxaGtqT1BRTUJCd05DQUFSZWxjNkluYnZJVStKdy9GU3JPakRrMFJ4VXN0dHNrOWptOU5ldFpBc1MKTFlidWtkbFZLNy82V1B4SFpzT1FwSGt3YndkaXhWM3UyTmV3KzloT1hqWW1vMEl3UURBT0JnTlZIUThCQWY4RQpCQU1DQXFRd0R3WURWUjBUQVFIL0JBVXdBd0VCL3pBZEJnTlZIUTRFRmdRVWx6N2grS3ZPOFRPS1hQcGhHTzJ4CmdaR3NYR1l3Q2dZSUtvWkl6ajBFQXdJRFJ3QXdSQUlnYlhOc2NzdzJMQW55UVk2cWhRbXVwaU41YXRRSC9sT08KMC9ReTdZN2l0OUlDSUVlWHZ4WUMyNEowbjhYV2pjQU9sZEh4TERTeHdNZUcrenZydmxhTFRmZnYKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="
api_key = "LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUVYQ0RPQytpYlc2YVZtdHlQSWFUeDF2SStZSkt5SEc4dUJyemJWYTJrUHhvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFQjRNTjBNaWxVcVNZOURjS0xURHJRSy9GOG5ycDFvVHpWKzM4SmdKQVU5OHpMa0xSVEw0VQpTQ0hhdVRQZzZoTDFkd1F4cWdWb0RMZUpQR2FtMVAxVlNBPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQo="

# Setup K8 configs
asd = config.load_kube_config()
kubernetes.client.Configuration()
configuration = client.Configuration(host="https://danger-doug.turnbull.corp:6443", api_key=api_key)
configuration.verify_ssl = False
configuration.username = "arroyo-admin"


api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(asd))


def kube_delete_empty_pods(namespace='default', phase='Succeeded'):
  """
  Pods are never empty, just completed the lifecycle.
  As such they can be deleted.
  Pods can be without any running container in 2 states:
  Succeeded and Failed. This call doesn't terminate Failed pods by default.
  """
  # The always needed object
  deleteoptions = client.V1DeleteOptions()
  # We need the api entry point for pods
  api_pods = client.CoreV1Api()
  # List the pods
  try:
    pods = api_pods.list_namespaced_pod(namespace,
                                      #  include_uninitialized=False,
                                        pretty=True,
                                        timeout_seconds=60)
  except ApiException as e:
    logging.error("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)

  for pod in pods.items:
    logging.debug(pod)
    podname = pod.metadata.name
    try:
      if pod.status.phase == phase:
        api_response = api_pods.delete_namespaced_pod(podname, namespace, deleteoptions)
        logging.info("Pod: {} deleted!".format(podname))
        logging.debug(api_response)
      else:
        logging.info("Pod: {} still not done... Phase: {}".format(podname, pod.status.phase))
    except ApiException as e:
      logging.error("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

  return


def kube_cleanup_finished_jobs(namespace='default', state='Finished'):
  """
  Since the TTL flag (ttl_seconds_after_finished) is still in alpha (Kubernetes 1.12) jobs need to be cleanup manually
  As such this method checks for existing Finished Jobs and deletes them.

  By default it only cleans Finished jobs. Failed jobs require manual intervention or a second call to this function.

  Docs: https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#clean-up-finished-jobs-automatically

  For deletion you need a new object type! V1DeleteOptions! But you can have it empty!

  CAUTION: Pods are not deleted at the moment. They are set to not running, but will count for your autoscaling limit, so if
           pods are not deleted, the cluster can hit the autoscaling limit even with free, idling pods.
           To delete pods, at this moment the best choice is to use the kubectl tool
           ex: kubectl delete jobs/JOBNAME.
           But! If you already deleted the job via this API call, you now need to delete the Pod using Kubectl:
           ex: kubectl delete pods/PODNAME
  """
  deleteoptions = client.V1DeleteOptions()
  try:
    jobs = api_instance.list_namespaced_job(namespace,
                                            #include_uninitialized=False,
                                            pretty=True,
                                            timeout_seconds=60)
    # print(jobs)
  except ApiException as e:
    print("Exception when calling BatchV1Api->list_namespaced_job: %s\n" % e)

  # Now we have all the jobs, lets clean up
  # We are also logging the jobs we didn't clean up because they either failed or are still running
  for job in jobs.items:
    logging.debug(job)
    jobname = job.metadata.name
    jobstatus = job.status.conditions
    if job.status.succeeded == 1:
      # Clean up Job
      logging.info("Cleaning up Job: {}. Finished at: {}".format(jobname, job.status.completion_time))
      try:
        # What is at work here. Setting Grace Period to 0 means delete ASAP. Otherwise it defaults to
        # some value I can't find anywhere. Propagation policy makes the Garbage cleaning Async
        api_response = api_instance.delete_namespaced_job(jobname,
                                                          namespace,
                                                          deleteoptions,
                                                          grace_period_seconds=0,
                                                          propagation_policy='Background')
        logging.debug(api_response)
      except ApiException as e:
        print("Exception when calling BatchV1Api->delete_namespaced_job: %s\n" % e)
    else:
      if jobstatus is None and job.status.active == 1:
        jobstatus = 'active'
      logging.info("Job: {} not cleaned up. Current status: {}".format(jobname, jobstatus))

  # Now that we have the jobs cleaned, let's clean the pods
  kube_delete_empty_pods(namespace)
  # And we are done!
  return


def kube_create_job_object(name, container_image, namespace="default", container_name="jobcontainer", env_vars={}):
  """
  Create a k8 Job Object
  Minimum definition of a job object:
  {'api_version': None, - Str
  'kind': None,     - Str
  'metadata': None, - Metada Object
  'spec': None,     -V1JobSpec
  'status': None}   - V1Job Status
  Docs: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Job.md
  Docs2: https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#writing-a-job-spec

  Also docs are pretty pretty bad. Best way is to ´pip install kubernetes´ and go via the autogenerated code
  And figure out the chain of objects that you need to hold a final valid object So for a job object you need:
  V1Job -> V1ObjectMeta
        -> V1JobStatus
        -> V1JobSpec -> V1PodTemplate -> V1PodTemplateSpec -> V1Container

  Now the tricky part, is that V1Job.spec needs a .template, but not a PodTemplateSpec, as such
  you need to build a PodTemplate, add a template field (template.template) and make sure
  template.template.spec is now the PodSpec.
  Then, the V1Job.spec needs to be a JobSpec which has a template the template.template field of the PodTemplate.
  Failure to do so will trigger an API error.

  Also Containers must be a list!

  Docs3: https://github.com/kubernetes-client/python/issues/589
  """
  # Body is the object Body
  body = client.V1Job(api_version="batch/v1", kind="Job")
  # Body needs Metadata
  # Attention: Each JOB must have a different name!
  body.metadata = client.V1ObjectMeta(namespace=namespace, name=name)
  # And a Status
  body.status = client.V1JobStatus()
  # Now we start with the Template...
  template = client.V1PodTemplate()
  template.template = client.V1PodTemplateSpec()
  # Passing Arguments in Env:
  env_list = []
  for env_name, env_value in env_vars.items():
    env_list.append(client.V1EnvVar(name=env_name, value=env_value))
  container = client.V1Container(name=container_name, image=container_image, env=env_list)
  template.template.spec = client.V1PodSpec(containers=[container], restart_policy='Never')
  # And finaly we can create our V1JobSpec!
  body.spec = client.V1JobSpec(ttl_seconds_after_finished=600, template=template.template)
  return body


def kube_test_credentials():
  """
  Testing function.
  If you get an error on this call don't proceed. Something is wrong on your connectivty to
  Google API.
  Check Credentials, permissions, keys, etc.
  Docs: https://cloud.google.com/docs/authentication/
  """
  try:
    api_response = api_instance.get_api_resources()
    logging.info(api_response)
  except ApiException as e:
    print("Exception when calling API: %s\n" % e)


def kube_create_job():
  # Create the job definition
  container_image = "namespace/k8-test-app:83226641581a1f0971055f972465cb903755fc9a"
  name = id_generator()
  body = kube_create_job_object(name, container_image, env_vars={"VAR": "TESTING"})
  try:
    api_response = api_instance.create_namespaced_job("default", body, pretty=True)
    print(api_response)
  except ApiException as e:
    print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)
  return


def id_generator(size=12, chars=string.ascii_lowercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))


if __name__ == '__main__':
  # Testing Credentials
  kube_test_credentials()
  # We try to cleanup dead jobs (READ THE FUNCTION CODE!)
  kube_cleanup_finished_jobs()
  kube_delete_empty_pods()
  # Create a couple of jobs
  for i in range(3):
    kube_create_job()
  # This was to test the use of ENV variables.
  logging.info("Finshed! - ENV: {}".format(os.environ["VAR"]))
  sys.exit(0)