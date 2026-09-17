variable "instance_name" {
  type    = string
  default = "app-node-01"
}

variable "subnet_cidr" {
  type    = string
}

output "compute_summary" {
  value = "Provisioned compute instance ${var.instance_name} attached to network subnet ${var.subnet_cidr}"
}
