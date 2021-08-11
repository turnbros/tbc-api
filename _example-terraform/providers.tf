terraform {
  backend "http" {
    address = "http://192.168.1.165:8444/tenant/test_tenant_9/resource_collection/state"
    lock_address = "http://192.168.1.165:8444/tenant/test_tenant_9/resource_collection/state"
    unlock_address = "http://192.168.1.165:8444/tenant/test_tenant_9/resource_collection/state"
  }
}

data "http" "tenant_resources" {
  url = "http://192.168.1.165:8444/tenant/test_tenant_9/resources"
  request_headers = {
    Accept = "application/json"
  }
}
