# Script to download from or upload to Azure Key Vault

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("download", "upload")]
    [string]$Operation,
    
    [Parameter(Mandatory=$false)]
    [string]$InputFile = "secrets.env",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyVaultName = "kv-govt-assist-dev"
)

# Display operation information
Write-Host "`n=== Operation Details ===" -ForegroundColor Cyan
Write-Host "Operation: $Operation" -ForegroundColor Yellow
Write-Host "Key Vault: $KeyVaultName" -ForegroundColor Yellow
if ($Operation -eq "upload") {
    Write-Host "Input File: $InputFile" -ForegroundColor Yellow
}
Write-Host "========================`n" -ForegroundColor Cyan

# Connect to Azure using device code
try {
    Write-Host "Connecting to Azure..."
    Connect-AzAccount -UseDeviceAuthentication
    
    # Wait for authentication
    Write-Host "Please authenticate using the code above in your browser at https://microsoft.com/devicelogin"
    
} catch {
    Write-Host "Error connecting to Azure: $_" -ForegroundColor Red
    exit
}

if ($Operation -eq "download") {
    # Get all secrets from Key Vault
    try {
        Write-Host "Downloading secrets from Key Vault: $KeyVaultName" -ForegroundColor Green
        $secrets = Get-AzKeyVaultSecret -VaultName $KeyVaultName
        
        # Clear existing file
        "" | Set-Content -Path $InputFile
        
        foreach ($secret in $secrets) {
            # Convert hyphens back to underscores for .env file
            $secretName = $secret.Name.Replace('-', '_')
            $secretValue = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name $secret.Name -AsPlainText
            
            # Write to the specified output file
            "$secretName=`"$secretValue`"" | Add-Content -Path $InputFile
        }
        
        Write-Host "✅ Secrets downloaded successfully to $InputFile" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error downloading secrets: $_" -ForegroundColor Red
    }
}
elseif ($Operation -eq "upload") {
    try {
        Write-Host "Reading secrets from file: $InputFile" -ForegroundColor Green
        Write-Host "Uploading to Key Vault: $KeyVaultName" -ForegroundColor Green
        
        # Check if input file exists
        if (-not (Test-Path $InputFile)) {
            Write-Host "❌ Error: Input file '$InputFile' not found!" -ForegroundColor Red
            exit
        }
        
        # Read the .env file
        $envContent = Get-Content $InputFile
        
        $successCount = 0
        $errorCount = 0
        
        foreach ($line in $envContent) {
            # Match any valid env var line (KEY=VALUE)
            if ($line -match '^[A-Za-z_][A-Za-z0-9_]*=(.*)$') {
                $key, $value = $line -split '=', 2
                $key = $key.Trim()
                
                # Convert underscores to hyphens for Azure Key Vault
                $kvKey = $key.Replace('_', '-')
                
                # Remove surrounding quotes if they exist
                $value = $value.Trim().Trim('"', "'")
                
                Write-Host "Setting secret: $key (Key Vault name: $kvKey)"
                
                try {
                    $secureValue = ConvertTo-SecureString -String $value -AsPlainText -Force
                    Set-AzKeyVaultSecret -VaultName $KeyVaultName -Name $kvKey -SecretValue $secureValue
                    $successCount++
                }
                catch {
                    Write-Host "❌ Error setting secret $kvKey : $_" -ForegroundColor Red
                    $errorCount++
                    continue
                }
            }
        }
        
        Write-Host "`n=== Upload Summary ===" -ForegroundColor Cyan
        Write-Host "Total secrets processed: $($successCount + $errorCount)" -ForegroundColor Yellow
        Write-Host "Successfully uploaded: $successCount" -ForegroundColor Green
        Write-Host "Failed to upload: $errorCount" -ForegroundColor Red
        Write-Host "=====================`n" -ForegroundColor Cyan
        
    }
    catch {
        Write-Host "❌ Error uploading secrets: $_" -ForegroundColor Red
    }
}
