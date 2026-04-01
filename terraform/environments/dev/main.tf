resource "google_project_service" "enabled_apis" {
  for_each           = toset(var.enabled_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

module "github_wif" {
  source       = "../../modules/github_wif"
  project_id   = var.project_id
  github_repo  = var.github_repo
  github_owner = var.github_owner
  environment  = var.environment
}
