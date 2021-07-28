terraform {
  backend "http" {
    address = "http://192.168.1.165:8444/tenant/tenantA/state"
    lock_address = "http://192.168.1.165:8444/tenant/tenantA/state"
    unlock_address = "http://192.168.1.165:8444/tenant/tenantA/state"
  }
}

data "http" "tenant_resources" {
  url = "http://192.168.1.165:8444/tenant/tenantA/resources"
  request_headers = {
    Accept = "application/json"
  }
}
