variable "value_a" {}
variable "value_b" {}
variable "value_c" {}

resource "null_resource" "example_module_resource_a" {
  provisioner "local-exec" {
    command = "echo 'Value A: ${var.value_a}'"
  }
}
resource "null_resource" "example_module_resource_b" {
  provisioner "local-exec" {
    command = "echo 'Value B: ${var.value_b}'"
  }
}
resource "null_resource" "example_module_resource_c" {
  provisioner "local-exec" {
    command = "echo 'Value C: ${var.value_c}'"
  }
}