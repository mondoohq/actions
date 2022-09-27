resource "null_resource" "ls" {
  provisioner "local-exec" {
    command = "ls"
  }
}