# Sanitisation Notes

Loopsmith is built privately first, then prepared for public release.

## Remove or redact before public push

- secrets
- API keys
- tokens
- passwords
- private infra addresses
- customer names
- customer-specific prompts
- private data fixtures

## Allowed in public repo

- agent names
- role structures
- evaluation concepts
- mutation boundary ideas
- routing concepts at a general level

## Public safety rule

The public repo history must also be clean. Do not publish a git history that ever contained secrets or private infrastructure details.
