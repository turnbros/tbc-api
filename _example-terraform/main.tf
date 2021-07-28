
locals {
  tenant_modules = jsondecode(data.http.tenant_resources.body)
}

module "example_null_module_1" {
  source = "./example-module"

  count = length(local.tenant_modules["example_null_module_1"])

  value_1 = local.tenant_modules["example_null_module_1"][count.index].value_1
  value_2 = local.tenant_modules["example_null_module_1"][count.index].value_2
  value_3 = local.tenant_modules["example_null_module_1"][count.index].value_3
}
