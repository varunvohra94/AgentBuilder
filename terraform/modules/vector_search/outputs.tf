output "rag_index_id" {
  description = "The ID of the RAG Index."
  value       = google_vertex_ai_index.rag_index.id
}

output "rag_index_name" {
  description = "The name of the RAG Index."
  value       = google_vertex_ai_index.rag_index.name
}

output "rag_index_endpoint_id" {
  description = "The ID of the RAG Index Endpoint."
  value       = google_vertex_ai_index_endpoint.rag_index_endpoint.id
}

output "rag_index_endpoint_name" {
  description = "The name of the RAG Index Endpoint."
  value       = google_vertex_ai_index_endpoint.rag_index_endpoint.name
}

output "metadata_bucket_name" {
  description = "The name of the metadata bucket."
  value       = google_storage_bucket.metadata_bucket.name
}
