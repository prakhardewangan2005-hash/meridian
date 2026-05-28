terraform {
  required_version = ">= 1.5"
}

# Cloud-agnostic skeleton. Replace the null_resource blocks with your provider's
# cluster + node-pool resources (google_container_cluster, aws_eks_cluster, etc.).

resource "null_resource" "cluster" {
  triggers = {
    name    = var.cluster_name
    region  = var.region
    version = var.kubernetes_version
  }
}

resource "null_resource" "node_pool" {
  count = var.node_count
  triggers = {
    cluster      = var.cluster_name
    machine_type = var.node_machine_type
    index        = count.index
  }
  depends_on = [null_resource.cluster]
}
