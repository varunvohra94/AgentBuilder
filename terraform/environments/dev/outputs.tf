output "github_actions_sa_email" {
  description = "Copy this into your GitHub Actions YAML 'service_account' field."
  value       = module.github_wif.service_account_email
}

output "github_actions_wif_provider" {
  description = "Copy this into your GitHub Actions YAML 'workload_identity_provider' field."
  value       = module.github_wif.workload_identity_provider_name
}
