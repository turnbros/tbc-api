variable "tbc_api_endpoint" {
  type        = string
  description = "The API endpoint for TBC"
  default     = "http://192.168.1.206:8444"
}
variable "tenant_name" {
  type        = string
  description = "The name of the tenant"
  default     = "test_tenant_2"
}

