output "cluster_name" {
  value = var.cluster_name
}

output "node_count" {
  value = var.node_count
}

output "endpoint" {
  value       = "https://${var.cluster_name}.${var.region}.example.com"
  description = "Cluster API endpoint (placeholder)"
}
