# Business Health Check

A mobile-first MVP built against a current fixed-price brief for a simple business health tracker.

## Product relation

Input numbers -> deterministic calculations -> one-screen status -> one useful suggestion.

## Inputs

1. Initial investment
2. Monthly running costs
3. Cost and selling price per sale
4. Typical monthly sales

## Outputs

- profit / loss
- break-even units
- additional units needed to break even
- contribution per sale
- startup payback estimate
- green / yellow / red operating status
- one plain-English suggestion

## Run locally

```powershell
cd E:\product-builds\business-health-tracker
python server.py
```

Then open http://127.0.0.1:8000

The app works without an API key using a deterministic local suggestion.

To enable the OpenAI suggestion endpoint:

```powershell
$env:OPENAI_API_KEY="..."
python server.py
```

Optional model override:

```powershell
$env:OPENAI_MODEL="gpt-5.6-luna"
```

## Test calculations

```powershell
node test.mjs
```

## Current boundary

No accounts, login, payments, bank/accounting integrations, native mobile app, or complex charts. Those are intentionally outside this MVP.