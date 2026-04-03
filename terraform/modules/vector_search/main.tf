locals {
  embedding_vector = flatten([
    for chunk in range(ceil(var.dimensions / 1000)) : [
      for i in range(min(1000, var.dimensions - (chunk * 1000))) : 0.0
    ]
  ])
}

resource "google_storage_bucket" "metadata_bucket" {
  name                        = "${var.project_id}-vdb-metadata-${var.environment}"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

resource "google_storage_bucket_object" "placeholder" {
  name   = "initial_data/placeholder.json"
  bucket = google_storage_bucket.metadata_bucket.name
  content = jsonencode({
    id        = "placeholder-0"
    embedding = local.embedding_vector
  })
}

resource "google_vertex_ai_index" "rag_index" {
  display_name = "rag-index-${var.environment}"
  region       = var.region
  description  = "Index for multi-modal embeddings"
  metadata {
    contents_delta_uri = "gs://${google_storage_bucket.metadata_bucket.name}/initial_data/"
    config {
      dimensions                  = var.dimensions
      approximate_neighbors_count = 150
      algorithm_config {
        tree_ah_config {
        }
      }
    }
  }
  depends_on = [google_storage_bucket.metadata_bucket]
}

resource "google_vertex_ai_index_endpoint" "rag_index_endpoint" {
  display_name            = "rag-index-endpoint-${var.environment}"
  region                  = var.region
  public_endpoint_enabled = true
}
