# Security

Do not put API keys or private documents in issues. Report sensitive vulnerabilities through GitHub's private vulnerability reporting if enabled, or contact the repository owner privately.

Hosted runners upload the selected full PDFs only when invoked explicitly. Credentials come from the environment or an explicitly supplied local environment file. Keep raw outputs and provider operation references outside Git. Review the provider's terms and model licenses for your intended use.

CI checks Python dependencies, scans code with Bandit and secrets with Gitleaks/detect-secrets, and emits an SBOM. Backend model environments and upstream helper code are optional and may have additional security considerations; the core CI does not download or execute GPU models.
