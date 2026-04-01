resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-actions-pool-${var.environment}"
  display_name              = "GitHub Actions Pool"
  description               = "Identity pool for GitHub Actions"
  disabled                  = false
}

resource "google_iam_workload_identity_pool_provider" "github_pool_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-pool-provider-${var.environment}"
  display_name                       = "GitHub Actions Pool Provider"
  description                        = "Identity pool provider for GitHub Actions"
  disabled                           = false

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
    "attribute.ref"              = "assertion.ref"
    "attribute.ref_type"         = "assertion.ref_type"
  }

  attribute_condition = "attribute.repository == '${var.github_owner}/${var.github_repo}'"
}

resource "google_service_account" "github_actions_sa" {
  account_id   = "github-actions-sa-${var.environment}"
  display_name = "GitHub Actions SA"
}

resource "google_service_account_iam_member" "github_actions_sa_impersonation" {
  service_account_id = google_service_account.github_actions_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_owner}/${var.github_repo}"
}

resource "google_project_iam_member" "github_actions_member" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.github_actions_sa.email}"
}

