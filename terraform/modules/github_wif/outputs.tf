output "service_account_email" {
  description = "The email of the Service Account created for GitHub Actions."
  value       = google_service_account.github_actions_sa.email
}

output "workload_identity_provider_name" {
  description = "The exact WIF Provider string needed for the GitHub Actions YAML."
  value       = google_iam_workload_identity_pool_provider.github_pool_provider.name
}
