---
description: How to expose the local Fortress Lab via Cloudflare Tunnel (domain-less)
---

# Cloudflare Tunnel Setup Guide (Fortress Edition)

Since you don't have a custom domain yet, we will use **Cloudflare Tunnel (TryCloudflare)** or a persistent tunnel linked to a Cloudflare account.

## Option 1: Quick "TryCloudflare" (Instant, No Account Required)
Best for quick testing and demonstration.

1.  **Download Cloudflared**:
    *   Windows: `https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi`
    *   (Or use `brew install cloudflare/cloudflare/cloudflared` if you have it)

2.  **Start the Lab Server**:
    Ensure the Target Lab is running on its current port (e.g., 9005):
    ```powershell
    uvicorn target_lab.main:app --port 9005
    ```

3.  **Launch Tunnel**:
    Run this in a new terminal:
    ```powershell
    cloudflared tunnel --url http://localhost:9005
    ```
    *   Cloudflare will give you a dynamic URL like `https://some-word-pair.trycloudflare.com`.
    *   **Anyone can now access your hardened lab via this URL.**

## Option 2: Persistent Tunnel (Recommended for "Strong Type" Labs)
Requires a free Cloudflare account.

1.  **Authenticate**:
    ```powershell
    cloudflared tunnel login
    ```
    *   Follow the browser prompt.

2.  **Create Tunnel**:
    ```powershell
    cloudflared tunnel create fortress-node
    ```

3.  **Config File**:
    Create `.cloudflared/config.yml`:
    ```yaml
    url: http://localhost:9005
    tunnel: <TUNNEL_ID>
    credentials-file: <PATH_TO_JSON_OBTAINED_IN_STEP_2>
    ```

4.  **Run persistent node**:
    ```powershell
    cloudflared tunnel run fortress-node
    ```

---

> [!IMPORTANT]
> When your lab is exposed via Cloudflare, the `SITREP` middleware will see Cloudflare's IPs. To see the **real attacker IP**, ensure you check the `X-Forwarded-For` header in the logs. Our SITREP system is already configured to prefer this header if present!
