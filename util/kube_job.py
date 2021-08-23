import logging
import sys
from kubernetes import client, config
import kubernetes.client
from kubernetes.client.rest import ApiException

# Set logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Setup K8 configs using kubeconfig
kube_config = config.load_kube_config()
print(kube_config)
api_instance = kubernetes.client.BatchV1Api(kubernetes.client.ApiClient(kube_config))

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
