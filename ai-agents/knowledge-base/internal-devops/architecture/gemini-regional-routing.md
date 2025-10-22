# Gemini Regional Routing Architecture

## Overview
IELTS AI Prep uses Google Gemini 2.5 Flash Lite and Flash models across 21 global regions with Dynamic Shared Quota (DSQ) for optimal latency and reliability.

## Regional Configuration

### Asia-Pacific (6 regions)
- **asia-southeast1** (Singapore) - Primary for ASEAN
- **asia-northeast1** (Tokyo) - Primary for Japan
- **asia-northeast3** (Seoul) - Primary for South Korea  
- **asia-south1** (Mumbai) - Primary for India/South Asia
- **asia-east1** (Taiwan) - Primary for Taiwan
- **australia-southeast1** (Sydney) - Primary for Australia/NZ

### Europe (8 regions)
- **europe-west1** (Belgium) - Primary for Western Europe
- **europe-west2** (London) - Primary for UK
- **europe-west3** (Frankfurt) - Primary for Germany/Central Europe
- **europe-west4** (Netherlands) - Primary for Northern Europe
- **europe-west6** (Zurich) - Primary for Switzerland
- **europe-west9** (Paris) - Primary for France
- **europe-north1** (Finland) - Primary for Nordics
- **europe-central2** (Warsaw) - Primary for Eastern Europe

### Americas (3 regions)
- **us-east4** (Virginia) - Primary for US East Coast
- **us-west1** (Oregon) - Primary for US West Coast
- **southamerica-east1** (São Paulo) - Primary for Latin America

### Middle East (2 regions)
- **me-west1** (Tel Aviv) - Primary for Israel
- **me-central1** (Doha) - Primary for Gulf states

### Africa (1 region)
- **africa-south1** (Johannesburg) - Primary for Africa

## Model Selection Strategy

### Smart Selection Algorithm
The system dynamically selects between Flash Lite and Flash based on IELTS speaking test part:

```python
# Part 1: Simple questions (4-5 minutes)
if part == 1:
    model = "gemini-2.0-flash-lite"  # Cost: $0.000075/1K tokens
    
# Parts 2-3: Long turn + discussion (7-10 minutes)
elif part in [2, 3]:
    model = "gemini-2.0-flash"  # Cost: $0.00015/1K tokens
```

### Cost Savings
- Flash Lite: 50% cheaper than Flash
- Part 1 uses Flash Lite: 4-5 min duration
- Parts 2-3 use Flash: 7-10 min duration
- **Average cost reduction: 58%** vs using Flash for entire test

## Regional Failover

### Health Monitoring
```python
class GeminiRegionalHealth:
    def check_region_health(self, region):
        """
        Checks regional endpoint health
        - Response time < 2 seconds: Healthy
        - Response time 2-5 seconds: Degraded
        - Response time > 5 seconds or error: Unhealthy
        """
```

### Failover Logic
1. **Primary Region:** Based on user's geographic location
2. **Fallback 1:** Nearest healthy region (same continent)
3. **Fallback 2:** Next nearest region (cross-continent if needed)
4. **Timeout:** 5 seconds per region attempt

### Example Failover Chain
User in Thailand:
1. Try: asia-southeast1 (Singapore) - 80ms latency
2. Fail → Try: asia-northeast1 (Tokyo) - 120ms latency
3. Fail → Try: asia-south1 (Mumbai) - 150ms latency

## Implementation Files

### Core Service
- **File:** `gemini_live_audio_service_smart.py`
- **Lines:** 444
- **Class:** `GeminiLiveAudioServiceSmart`

### Key Methods
```python
def select_model_for_part(self, part):
    """Selects Gemini model based on IELTS part"""
    
def get_regional_endpoint(self, user_location):
    """Returns optimal Gemini region for user"""
    
def handle_regional_failover(self, current_region):
    """Fails over to next healthy region"""
```

### Configuration
Located in: `ielts_workflow_manager.py`
```python
GEMINI_REGIONS = {
    'asia-southeast1': {'countries': ['TH', 'SG', 'MY', 'ID', ...]},
    'asia-northeast1': {'countries': ['JP']},
    # ... 21 regions total
}
```

## Latency Optimization

### Performance Metrics
- **Asian users:** 50-70% latency reduction
- **European users:** 30-40% latency reduction  
- **US users:** 20-30% latency reduction

### Country-to-Region Mapping
77 countries mapped to optimal regions:
```python
COUNTRY_REGION_MAP = {
    'TH': 'asia-southeast1',  # Thailand → Singapore
    'JP': 'asia-northeast1',  # Japan → Tokyo
    'DE': 'europe-west3',     # Germany → Frankfurt
    # ... 77 total mappings
}
```

## Dynamic Shared Quota (DSQ)

### How It Works
- **No manual quota management** required
- Automatic capacity distribution across regions
- Load balancing handled by Vertex AI
- No quota reservation needed

### Benefits
1. **Automatic scaling:** Quota adjusts based on demand
2. **No pre-allocation:** Pay only for what you use
3. **Regional flexibility:** Capacity moves where needed
4. **Simplified ops:** No quota management overhead

## Common Issues & Fixes

### Issue: Maya Disconnecting in Part 2/3
**Symptom:** Connection drops during long responses  
**Cause:** Regional timeout too short (5 seconds)  
**Fix:** Increase timeout to 10 seconds
```python
# In gemini_live_audio_service_smart.py
REGIONAL_TIMEOUT = 10  # Changed from 5
```

### Issue: High Latency for Specific Country
**Symptom:** Users report slow responses  
**Cause:** Country mapped to suboptimal region  
**Fix:** Update country-to-region mapping
```python
# In ielts_workflow_manager.py
COUNTRY_REGION_MAP['XX'] = 'optimal-region'
```

### Issue: Regional Health Check False Positives
**Symptom:** Healthy regions marked unhealthy  
**Cause:** Timeout threshold too aggressive  
**Fix:** Adjust health check timeout
```python
HEALTH_CHECK_TIMEOUT = 3  # Increased from 2
```

## Monitoring & Debugging

### CloudWatch Metrics
- `gemini_region_latency` - Per-region response time
- `gemini_failover_count` - Regional failover frequency
- `gemini_model_usage` - Flash vs Flash Lite usage

### Debugging Steps
1. Check user's IP geolocation
2. Verify country-to-region mapping
3. Test regional endpoint health
4. Review CloudWatch logs for errors
5. Check Gemini quotas (should be DSQ)

## Cost Analysis

### Monthly Estimates (1,000 speaking tests)
- **Flash Lite (Part 1):** ~$5
- **Flash (Parts 2-3):** ~$20
- **Total:** ~$25/month for 1,000 tests
- **Per test:** ~$0.025

### Without Smart Selection
- **Flash only (all parts):** ~$60/month
- **Savings:** 58% ($35/month)

## Best Practices

1. **Always use smart selection** - Don't hardcode model choice
2. **Monitor regional health** - Set up CloudWatch alarms
3. **Update country mappings** - As new regions launch
4. **Test failover chains** - Periodically verify backups work
5. **Review latency metrics** - Optimize region selection

## Related Files
- `gemini_live_audio_service_smart.py` - Core implementation
- `ielts_workflow_manager.py` - Region configuration
- `deployment/lambda_speaking_handler.py` - AWS Lambda integration
- `gemini_live_audio_service_aws.py` - AWS-specific version
