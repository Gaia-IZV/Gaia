locals {
  app_env_file_exists      = fileexists(var.app_env_file_path)
  app_env_content_resolved = local.app_env_file_exists ? file(var.app_env_file_path) : var.app_env_content
}
