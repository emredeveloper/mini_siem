param(
    [string]$BaseUrl = "http://localhost:8000",
    [int]$Loops = 30
)

# Generate demo traffic by calling multiple endpoints
for ($i = 1; $i -le $Loops; $i++) {
    try {
        # Health check and home endpoint
        Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get | Out-Null
        Invoke-RestMethod -Uri "$BaseUrl/" -Method Get | Out-Null
        
        # Simulate slow request
        Invoke-RestMethod -Uri "$BaseUrl/simulate/slow" -Method Get | Out-Null
        
        # Create orders
        Invoke-RestMethod `
            -Uri "$BaseUrl/orders" `
            -Method Post `
            -ContentType "application/json" `
            -Body '{"customer_id":"cust-1001","amount":249.90,"currency":"TRY"}' | Out-Null
    }
    catch {
        # Silently catch errors
    }

    # Every 4th iteration, trigger an error
    if ($i % 4 -eq 0) {
        try {
            Invoke-RestMethod -Uri "$BaseUrl/simulate/error" -Method Get | Out-Null
        }
        catch {
            # Expected error
        }
    }

    # Every 5th iteration, try a not-found endpoint
    if ($i % 5 -eq 0) {
        try {
            Invoke-RestMethod -Uri "$BaseUrl/products/13" -Method Get | Out-Null
        }
        catch {
            # Expected 404
        }
    }

    # Wait 250ms between requests
    Start-Sleep -Milliseconds 250
}

