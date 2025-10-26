# Environment Configuration Files

This directory contains environment-specific configuration files for different deployment environments.

## Files

- **`.env.local`** - Local development settings
- **`.env.test`** - Test/staging environment settings
- **`.env.production`** - Production environment settings

## Usage

### Local Development

The startup script will automatically use `.env.local`:

```bash
./scripts/start-local.sh
```

Or manually copy to root:

```bash
cp env/.env.local .env
```

### Test Environment

```bash
cp env/.env.test .env
```

### Production

```bash
cp env/.env.production .env
# Then edit .env with real production credentials
```

## Security Notes

- ⚠️ **NEVER** commit `.env` files with real credentials to git
- `.env.production` should only contain placeholder values in the repo
- Use secret management tools (AWS Secrets Manager, HashiCorp Vault, etc.) in production
- Rotate keys regularly
- Use strong random values for `SECRET_KEY`

## Required Variables

All environments must set:
- `OPENAI_API_KEY` - Your OpenAI API key
- `TELNYX_API_KEY` - Your Telnyx API key
- `SECRET_KEY` - Random secret for JWT/encryption
- `PERSONA_NAME` - Which persona to use
- `BUSINESS_NAME` - Your business name

## Optional Variables

- `TELNYX_SIGNING_SECRET` - For webhook signature verification
- `OPENAI_MODEL` - Override default model (gpt-4o-mini)
- `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR
