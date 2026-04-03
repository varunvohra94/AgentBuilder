output "github_actions_sa_email" {
  description = "Copy this into your GitHub Actions YAML 'service_account' field."
  value       = module.github_wif.service_account_email
}

output "github_actions_wif_provider" {
  description = "Copy this into your GitHub Actions YAML 'workload_identity_provider' field."
  value       = module.github_wif.workload_identity_provider_name
}

output "rag_index_id" {
  description = "The ID of the RAG Index."
  value       = module.vector_search.rag_index_id
}

output "rag_index_name" {
  description = "The name of the RAG Index."
  value       = module.vector_search.rag_index_name
}

output "rag_index_endpoint_id" {
  description = "The ID of the RAG Index Endpoint."
  value       = module.vector_search.rag_index_endpoint_id
}

output "rag_index_endpoint_name" {
  description = "The name of the RAG Index Endpoint."
  value       = module.vector_search.rag_index_endpoint_name
}

output "metadata_bucket_name" {
  description = "The name of the metadata bucket."
  value       = module.vector_search.metadata_bucket_name
}

