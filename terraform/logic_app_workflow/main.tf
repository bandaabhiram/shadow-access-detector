resource "azurerm_logic_app_workflow" "audit" {
  name                = "${var.prefix}-audit-workflow"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "logic_app_storage" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_logic_app_workflow.audit.identity[0].principal_id
}
