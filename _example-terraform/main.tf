locals {
  tenant_modules = jsondecode(data.http.tenant_resources.body)
}

module "example_null_module_1" {
  source = "./example-module"
  for_each = local.tenant_modules["example_null_module_1"]
  value_1 = each.value["value_1"]
  value_2 = each.value["value_2"]
  value_3 = each.value["value_3"]
}
