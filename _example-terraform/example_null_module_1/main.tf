variable "value_1" {}
variable "value_2" {}
variable "value_3" {}

resource "null_resource" "example_module_resource_1" {
  provisioner "local-exec" {
    command = "echo 'Value 1: ${var.value_1}'"
  }
}
resource "null_resource" "example_module_resource_2" {
  provisioner "local-exec" {
    command = "echo 'Value 2: ${var.value_2}'"
  }
}
resource "null_resource" "example_module_resource_3" {
  provisioner "local-exec" {
    command = "echo 'Value 3: ${var.value_3}'"
  }
}