# Configure Ollama to use D drive for model storage
Write-Host "🔧 Configuring Ollama to use D drive for models..." -ForegroundColor Green

# Create the ollama models directory on D drive
$ollamaModelsPath = "D:\Pys\Myra\ollama_models"
New-Item -ItemType Directory -Path $ollamaModelsPath -Force | Out-Null

# Set environment variable for current session
$env:OLLAMA_MODELS = $ollamaModelsPath
Write-Host "✅ Set OLLAMA_MODELS to: $ollamaModelsPath" -ForegroundColor Green

# Add to user environment variables permanently
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ollamaModelsPath, "User")
Write-Host "✅ Added OLLAMA_MODELS to user environment variables" -ForegroundColor Green

Write-Host "📋 Configuration complete!" -ForegroundColor Yellow
