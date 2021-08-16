from python_terraform import *


def run_terraform(tenant_name):
  tf = Terraform(working_dir="_example-terraform", variables={'tenant_name':tenant_name})
  tf.init()
  return tf.apply(skip_plan=True)
