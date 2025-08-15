# Azure Key Vault Secrets Management Script

This PowerShell script (`keyvault.ps1`) provides a convenient way to download secrets from or upload secrets to Azure Key Vault.

## Prerequisites

- PowerShell 5.1 or later
- Azure PowerShell module (`Az` module)
- Azure subscription with access to the target Key Vault
- Proper permissions to read/write secrets in the Key Vault

## Installation

1. Install the Azure PowerShell module:
```powershell
Install-Module -Name Az -AllowClobber -Force
```

2. Import the module:
```powershell
Import-Module Az
```

## Usage

### Basic Syntax

```powershell
.\keyvault.ps1 -Operation <download|upload> [-InputFile <filename>] [-KeyVaultName <vault-name>]
```

### Parameters

- **Operation** (Required): Specifies the operation to perform
  - `download`: Download all secrets from Key Vault to a local file
  - `upload`: Upload secrets from a local file to Key Vault

- **InputFile** (Optional): Path to the file containing secrets for upload
  - Default: `secrets.env`
  - Format: Environment variables file (KEY=VALUE format)

- **KeyVaultName** (Optional): Name of the Azure Key Vault
  - Default: `kv-govt-assist-dev`

## Operations

### Download Secrets from Key Vault

Downloads all secrets from the specified Key Vault and saves them to `secrets.env`:

```powershell
.\keyvault.ps1 -Operation download
```

**What happens:**
- Connects to Azure using device authentication
- Retrieves all secrets from the Key Vault
- Converts Key Vault secret names (with hyphens) to environment variable format (with underscores)
- Saves secrets to `secrets.env` file in the current directory

**Output file:** `secrets.env`

### Upload Secrets to Key Vault

Uploads secrets from a local file to the specified Key Vault:

```powershell
.\keyvault.ps1 -Operation upload
```

**Input file:** `secrets.env` (default)

**File format:** Environment variables file with the following format:
```
SECRET_NAME=secret_value
DATABASE_URL=postgresql://user:pass@host:port/db
API_KEY=your_api_key_here
```

**What happens:**
- Reads secrets from the specified input file
- Converts environment variable names (with underscores) to Key Vault secret names (with hyphens)
- Uploads each secret to the Key Vault
- Provides a summary of successful and failed uploads

## File Formats

### Input File for Upload (`secrets.env`)

The script expects a standard environment variables file:

```
# Database configuration
DATABASE_URL=postgresql://user:password@host:5432/database
DATABASE_USER=myuser
DATABASE_PASSWORD=mypassword

# API Keys
API_KEY=sk-1234567890abcdef
JWT_SECRET=your-jwt-secret-key

# Service URLs
AUTH_SERVICE_URL=https://auth.example.com
PAYMENT_SERVICE_URL=https://payments.example.com
```

**Rules:**
- One secret per line
- Format: `KEY=VALUE`
- Keys must start with a letter or underscore
- Values can be quoted or unquoted
- Comments (lines starting with #) are ignored

### Output File for Download (`secrets.env`)

The script creates a `secrets.env` file with the same format as the input file.

## Examples

### Download all secrets from development Key Vault
```powershell
.\keyvault.ps1 -Operation download -KeyVaultName kv-govt-assist-dev
```

### Upload secrets from a custom file
```powershell
.\keyvault.ps1 -Operation upload -InputFile my-secrets.env -KeyVaultName kv-govt-assist-prod
```

### Upload secrets using default settings
```powershell
.\keyvault.ps1 -Operation upload
```

## Authentication

The script uses Azure device authentication:

1. When you run the script, it will display a code
2. Open your browser and go to https://microsoft.com/devicelogin
3. Enter the displayed code
4. Sign in with your Azure credentials

## Error Handling

- **Connection errors**: Script will exit if Azure connection fails
- **File not found**: Upload operation will fail if the input file doesn't exist
- **Individual secret errors**: Failed secrets are logged but don't stop the entire operation
- **Summary**: Both operations provide detailed success/failure summaries

## Security Notes

- Secrets are stored securely in Azure Key Vault
- Local files (`secrets.env`) should be added to `.gitignore`
- The script uses secure string conversion for sensitive data
- Device authentication provides secure Azure access

## Troubleshooting

### Common Issues

1. **"Module Az not found"**
   - Install the Azure PowerShell module: `Install-Module -Name Az`

2. **"Access denied" errors**
   - Ensure your Azure account has proper permissions on the Key Vault
   - Check Key Vault access policies

3. **"File not found" errors**
   - Verify the input file exists and path is correct
   - Use absolute paths if needed

4. **Authentication failures**
   - Ensure you have valid Azure credentials
   - Check if your account has access to the subscription

### Getting Help

- Check Azure PowerShell documentation: https://docs.microsoft.com/en-us/powershell/azure/
- Verify Key Vault permissions in Azure Portal
- Review Azure Key Vault documentation: https://docs.microsoft.com/en-us/azure/key-vault/
