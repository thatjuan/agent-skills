# Admin & Rovo Dev Commands

## acli admin auth

Authentication for Atlassian **organization admin** context. Independent from `jira auth`.

| Subcommand | Purpose |
|-----------|---------|
| `login` | Authenticate for org-admin tasks |
| `logout` | Remove org-admin credentials |
| `status` | Show active admin account |
| `switch` | Switch between admin accounts |

## acli admin user

Managed-account lifecycle. Operates on users in an Atlassian organization.

| Subcommand | Purpose |
|-----------|---------|
| `activate` | Activate a user |
| `deactivate` | Deactivate a user |
| `delete` | Delete a managed account (soft-delete, recoverable) |
| `cancel-delete` | Cancel a pending deletion |

## acli rovodev

Atlassian's AI coding agent (Beta).

| Subcommand | Purpose |
|-----------|---------|
| `auth` | Authenticate to use Rovo Dev CLI |

## acli feedback

Submits feedback or a bug report directly to Atlassian.

## Help Discovery

`acli <command> <subcommand> --help` prints the exact flag set for that leaf. When a flag is not in the written reference, the binary's own help output is authoritative.
