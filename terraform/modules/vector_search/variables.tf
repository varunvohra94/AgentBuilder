variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP Region"
  type        = string
}

variable "environment" {
  description = "The environment"
  type        = string
}

variable "dimensions" {
  description = "The number of dimensions for the vector search"
  type        = number
}
