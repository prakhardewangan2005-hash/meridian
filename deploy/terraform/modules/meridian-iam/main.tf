terraform {
  required_version = ">= 1.5"
}

variable "cluster_name" { type = string }
variable "namespace" {
  type    = string
  default = "meridian"
}

resource "null_resource" "controller_sa" {
  triggers = { name = "meridian-controller", ns = var.namespace }
}

resource "null_resource" "agent_sa" {
  triggers = { name = "meridian-agent", ns = var.namespace }
}

output "controller_sa" {
  value = "meridian-controller@${var.cluster_name}"
}
output "agent_sa" {
  value = "meridian-agent@${var.cluster_name}"
}
