terraform {
  backend "http" {
    address        = "http://192.168.1.206:8444/tenant/test_tenant_2/workspace/state"
    lock_address   = "http://192.168.1.206:8444/tenant/test_tenant_2/workspace/state"
    unlock_address = "http://192.168.1.206:8444/tenant/test_tenant_2/workspace/state"
  }
}

data "http" "tenant_resources" {
  url = "${var.tbc_api_endpoint}/tenant/${var.tenant_name}/workspace/variables"
  request_headers = {
    Accept = "application/json"
  }
}
