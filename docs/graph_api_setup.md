# Graph API Setup Guide

## Required Permissions

Register an application in Azure AD and grant these **Application** permissions:

| Permission | Purpose |
|------------|---------|
| `Directory.Read.All` | Read user, group, and SP data |
| `User.Read.All` | Read sign-in activity |
| `AuditLog.Read.All` | Access `signInActivity` and `servicePrincipalSignInActivity` |
| `Policy.Read.All` | Read Conditional Access policies |

## Admin Consent

All permissions require **Admin Consent** from a Global Administrator.

## Break-Glass Monitoring

The Logic App runs under a dedicated service principal. Monitor this SP with:
- Sign-in logs in Log Analytics
- Alert on any interactive sign-in attempts
- Rotate secret every 90 days
