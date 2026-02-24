# Odoo <-> Git Automation (v1)

## Objectif
- Connecter un profil Odoo via XML-RPC.
- Connecter un profil Git vers un depot distant.
- Configurer une automation qui cree une branche Git quand une tache Odoo entre dans une etape cible.

## API

### Odoo profiles
- `GET /api/odoo-profiles/`
- `POST /api/odoo-profiles/`
- `POST /api/odoo-profiles/{id}/test/`
- `GET /api/odoo-profiles/{id}/projects/`
- `GET /api/odoo-profiles/{id}/projects/{project_id}/stages/`

Payload creation:

```json
{
  "name": "odoo-prod",
  "base_url": "https://odoo.example.com",
  "database": "mydb",
  "email": "user@example.com",
  "password": "secret"
}
```

### Git profiles
- `GET /api/git-profiles/`
- `POST /api/git-profiles/`
- `POST /api/git-profiles/{id}/test/`

Payload creation:

```json
{
  "name": "git-main",
  "provider": "github",
  "repository_url": "https://github.com/org/repo.git",
  "username": "bot-user",
  "token": "ghp_xxx",
  "default_source_branch": "dev"
}
```

### Automations
- `GET /api/automations/`
- `POST /api/automations/`
- `POST /api/automations/{id}/run-task/`

Payload creation:

```json
{
  "name": "branch-on-specification",
  "odoo_profile_id": 1,
  "git_profile_id": 1,
  "odoo_project_id": 10,
  "odoo_project_name": "MyMemoMaster",
  "trigger_stage_id": 42,
  "trigger_stage_name": "specification",
  "source_branch_field": "x_branch_source",
  "work_branch_field": "x_work_branch"
}
```

Execution payload:

```json
{
  "task_id": 1234
}
```

## Regle v1 implementee
- Si la tache n'est pas dans l'etape configuree: skip.
- Si le champ "branche de travail" est vide: skip (aucune branche creee).
- Sinon creation de la branche de travail a partir de la branche source.
- Si la branche existe deja: statut `already_exists`.

## Notes techniques
- Odoo est interroge via XML-RPC (`/xmlrpc/2/common`, `/xmlrpc/2/object`).
- Le nom technique des champs Odoo est configurable (`source_branch_field`, `work_branch_field`).
- La creation de branche Git se fait sans clone local via `git ls-remote` et `git push <sha>:refs/heads/<branch>`.
