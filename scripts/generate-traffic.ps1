param(
    [string]$BaseUrl = "http://localhost:8000",
    [int]$Loops = 30
)

for ($i = 1; $i -le $Loops; $i++) {
    try {
        Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get | Out-Null
        Invoke-RestMethod -Uri "$BaseUrl/" -Method Get | Out-Null
        Invoke-RestMethod -Uri "$BaseUrl/simulate/slow" -Method Get | Out-Null
        Invoke-RestMethod `
            -Uri "$BaseUrl/orders" `
            -Method Post `
            -ContentType "application/json" `
            -Body '{"customer_id":"cust-1001","amount":249.90,"currency":"TRY"}' | Out-Null
    }
    catch {
    }

    if ($i % 4 -eq 0) {
        try {
            Invoke-RestMethod -Uri "$BaseUrl/simulate/error" -Method Get | Out-Null
        }
        catch {
        }
    }

    if ($i % 5 -eq 0) {
        try {
            Invoke-RestMethod -Uri "$BaseUrl/products/13" -Method Get | Out-Null
        }
        catch {
        }
    }

    Start-Sleep -Milliseconds 250
}

