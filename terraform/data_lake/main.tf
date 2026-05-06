resource "azurerm_storage_account" "shadow" {
  name                     = "${var.prefix}dl${random_string.suffix.result}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
  tags                     = var.tags
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_storage_data_lake_gen2_filesystem" "raw" {
  name               = "raw-graph-data"
  storage_account_id = azurerm_storage_account.shadow.id
}

output "storage_account_id" {
  value = azurerm_storage_account.shadow.id
}

output "storage_account_name" {
  value = azurerm_storage_account.shadow.name
}
