resource "google_project_service" "enabled_apis" {
  for_each           = toset(var.enabled_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
