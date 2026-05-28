variable "cluster_name" {
  type        = string
  description = "Name of the Kubernetes cluster"
}

variable "region" {
  type        = string
  description = "Region to deploy into"
}

variable "node_count" {
  type        = number
  default     = 3
  description = "Number of worker nodes"
}

variable "node_machine_type" {
  type        = string
  default     = "e2-standard-4"
  description = "Machine type for worker nodes"
}

variable "kubernetes_version" {
  type    = string
  default = "1.29"
}

variable "tags" {
  type    = map(string)
  default = {}
}
