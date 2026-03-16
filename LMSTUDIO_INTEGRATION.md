# LM Studio Integration Guide

This project now supports using LM Studio with the Mistral 7B v0.3 model for AI-powered attack planning and website profiling.

## Requirements
- LM Studio installed and running locally
- Mistral 7B v0.3 model downloaded in LM Studio
- LM Studio HTTP API enabled (default: http://localhost:1234)

## Setup Steps
1. Start LM Studio and load the Mistral 7B v0.3 model.
2. Enable the HTTP API in LM Studio settings (default port: 1234).
3. Update your `.env` file:
   ```env
   LMSTUDIO_API_URL=http://localhost:1234/v1/chat/completions
   LMSTUDIO_MODEL=mistral-7b-v0.3
   ```
4. The agent will send prompts to LM Studio for attack planning and profiling.

## Troubleshooting
- Ensure LM Studio is running and the API is enabled.
- Check firewall settings if you cannot connect to http://localhost:1234.
- Review logs for errors in agent output.

## Example Usage
The agent will automatically use LM Studio for AI tasks if the API URL is set in `.env`.

---
For advanced configuration, see LM Studio documentation.
