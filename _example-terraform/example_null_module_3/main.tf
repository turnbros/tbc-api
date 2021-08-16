variable "value_foo" {}
variable "value_bar" {}
variable "value_baz" {}

resource "null_resource" "example_module_resource_foo" {
  provisioner "local-exec" {
    command = "echo 'Value FOO: ${var.value_foo}'"
  }
}
resource "null_resource" "example_module_resource_bar" {
  provisioner "local-exec" {
    command = "echo 'Value BAR: ${var.value_bar}'"
  }
}
resource "null_resource" "example_module_resource_baz" {
  provisioner "local-exec" {
    command = "echo 'Value BAZ: ${var.value_baz}'"
  }
}