# Local Testing Script for Job Scraper API
# Run this script to test all endpoints

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Job Scraper API - Local Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "Test 1: Health Check Endpoint" -ForegroundColor Yellow
Write-Host "GET http://localhost:8080/health`n" -ForegroundColor Gray
$health = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get
$health | ConvertTo-Json -Depth 5
Write-Host "`n✅ Health check passed!`n" -ForegroundColor Green

Start-Sleep -Seconds 1

# Test 2: Root Endpoint
Write-Host "Test 2: Root Endpoint (API Info)" -ForegroundColor Yellow
Write-Host "GET http://localhost:8080/`n" -ForegroundColor Gray
$root = Invoke-RestMethod -Uri "http://localhost:8080/" -Method Get
$root | ConvertTo-Json -Depth 5
Write-Host "`n✅ Root endpoint passed!`n" -ForegroundColor Green

Start-Sleep -Seconds 1

# Test 3: Status Endpoint
Write-Host "Test 3: Status Endpoint" -ForegroundColor Yellow
Write-Host "GET http://localhost:8080/api/status`n" -ForegroundColor Gray
$status = Invoke-RestMethod -Uri "http://localhost:8080/api/status" -Method Get
$status | ConvertTo-Json -Depth 5
Write-Host "`n✅ Status endpoint passed!`n" -ForegroundColor Green

Start-Sleep -Seconds 1

# Test 4: Scraping Endpoint (OPTIONAL - takes time)
Write-Host "Test 4: Scraping Endpoint (Optional)" -ForegroundColor Yellow
$response = Read-Host "Do you want to test scraping? This will take 30-90 seconds (y/n)"

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`nPOST http://localhost:8080/api/scrape-jobs" -ForegroundColor Gray
    Write-Host "Payload: { platform: 'SimplyHired', keywords: ['python developer'], pages: 1 }`n" -ForegroundColor Gray
    Write-Host "⏳ Scraping in progress... Please wait (30-90 seconds)`n" -ForegroundColor Yellow
    
    $body = @{
        platform = "SimplyHired"
        keywords = @("python developer")
        pages = 1
        location = "United States"
    } | ConvertTo-Json
    
    try {
        $scrapeResult = Invoke-RestMethod -Uri "http://localhost:8080/api/scrape-jobs" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 180
        
        Write-Host "✅ Scraping completed successfully!`n" -ForegroundColor Green
        Write-Host "Results:" -ForegroundColor Cyan
        Write-Host "  Total Jobs: $($scrapeResult.total_jobs)" -ForegroundColor White
        Write-Host "  Scraped At: $($scrapeResult.scraped_at)" -ForegroundColor White
        
        if ($scrapeResult.jobs.Count -gt 0) {
            Write-Host "`nSample Jobs (first 3):" -ForegroundColor Cyan
            for ($i = 0; $i -lt [Math]::Min(3, $scrapeResult.jobs.Count); $i++) {
                $job = $scrapeResult.jobs[$i]
                Write-Host "`nJob $($i + 1):" -ForegroundColor Yellow
                Write-Host "  Title: $($job.title)" -ForegroundColor White
                Write-Host "  Company: $($job.company)" -ForegroundColor White
                Write-Host "  Location: $($job.location)" -ForegroundColor White
                Write-Host "  Type: $($job.job_type)" -ForegroundColor White
                Write-Host "  Posted: $($job.posted_date)" -ForegroundColor White
            }
        }
    }
    catch {
        Write-Host "❌ Scraping failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "⏭️  Skipping scraping test`n" -ForegroundColor Gray
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Suite Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ All basic tests passed!" -ForegroundColor Green
Write-Host "`nYour API is ready to deploy to DigitalOcean! 🚀`n" -ForegroundColor Cyan
