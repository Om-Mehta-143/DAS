## Phase 2: Maximum Defense Hardening

**Date:** 2026-03-09

### Scope
- **Proof-of-Work (PoW)**: Implement a mandatory JS challenge for form submission.
- **Honey-fields**: Add decoy form elements to trap automated crawlers.
- **TLS/JA3 Behavior Check**: Analyze request characteristics to identify non-browser clients.
- **Tunneling**: Prepare for Cloudflare Tunnel integration.

### Approach
- **PoW**: Use a SHA-256 base JS challenge. The server provides a salt, the client must find a nonce.
- **Honey-fields**: Add a `display:none` input named `account_id_confirm`. Any value here = instant block.
- **Passwordless**: Explicitly excluded for now to keep the test agent relevant.

### Constraints
- Must remain compatible with the existing `Target Lab` FastAPI structure.
- PoW should be "invisible" to a real user but computationally expensive for a bot.
