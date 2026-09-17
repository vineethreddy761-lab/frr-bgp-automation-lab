variable "vpc_cidr" {
  type    = string
  default = "192.168.10.0/24"
}

output "vpc_network" {
  value = "Configured virtual network CIDR: ${var.vpc_cidr}"
}
