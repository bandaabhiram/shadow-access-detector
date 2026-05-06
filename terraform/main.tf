terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.80" }
    azuread = { source = "hashicorp/azuread", version = "~> 2.45" }
  }
}

provider "azurerm" { features {} }
provider "azuread" {}

locals {
  prefix = "shadow-access"
  tags   = { project = "shadow-access-detector", managed_by = "terraform" }
}

resource "azurerm_resource_group" "audit" {
  name     = "${local.prefix}-rg"
  location = "uksouth"
  tags     = local.tags
}

module "data_lake" {
  source              = "./data_lake"
  resource_group_name = azurerm_resource_group.audit.name
  location            = azurerm_resource_group.audit.location
  prefix              = local.prefix
  tags                = local.tags
}

module "logic_app" {
  source              = "./logic_app_workflow"
  resource_group_name = azurerm_resource_group.audit.name
  location            = azurerm_resource_group.audit.location
  prefix              = local.prefix
  tags                = local.tags
  storage_account_id  = module.data_lake.storage_account_id
}
