terraform {
  required_version = ">= 1.5"
}

module "cluster" {
  source             = "../../modules/meridian-cluster"
  cluster_name       = "meridian-dev"
  region             = "us-east-1"
  node_count         = 2
  node_machine_type  = "e2-standard-2"
  kubernetes_version = "1.29"
  tags = {
    env     = "dev"
    project = "meridian"
  }
}

module "iam" {
  source       = "../../modules/meridian-iam"
  cluster_name = module.cluster.cluster_name
}

output "cluster_endpoint" {
  value = module.cluster.endpoint
}
