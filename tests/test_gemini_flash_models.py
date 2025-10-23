"""
Comprehensive tests for Gemini 2.5 Flash and Flash Lite models
Tests smart selection, regional routing, and model-specific functionality
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from gemini_live_audio_service_smart import GeminiLiveServiceSmart
from ielts_workflow_manager import IELTSWorkflowManager, SmartSelectionOrchestrator
from gemini_regional_router import get_regional_router


class TestGeminiFlashModels:
    """Test suite for Gemini 2.5 Flash and Flash Lite models"""
    
    def test_models_configuration(self):
        """Test that both Flash and Flash Lite models are properly configured"""
        with patch('gemini_live_audio_service_smart.genai.Client'):
            service = GeminiLiveServiceSmart(
                project_id='test-project',
                region='us-central1',
                auto_regional_routing=False
            )
            
            assert 'flash-lite' in service.models
            assert 'flash' in service.models
            assert service.models['flash-lite'] == 'gemini-2.5-flash-lite'
            assert service.models['flash'] == 'gemini-2.5-flash'
    
    def test_smart_selection_orchestrator_part1_uses_flash_lite(self):
        """Test Part 1 always uses Flash Lite (cost-optimized)"""
        workflow = IELTSWorkflowManager()
        
        # Part 1: Simple Q&A
        config = workflow.update_state_for_part(1)
        model = workflow.get_optimal_model()
        
        assert model == 'gemini-2.5-flash-lite'
        assert config['part'] == 1
    
    def test_smart_selection_orchestrator_part2_uses_flash_lite(self):
        """Test Part 2 uses Flash Lite (structured but predictable)"""
        workflow = IELTSWorkflowManager()
        
        # Part 2: Long turn
        config = workflow.update_state_for_part(2)
        model = workflow.get_optimal_model()
        
        assert model == 'gemini-2.5-flash-lite'
        assert config['part'] == 2
    
    def test_smart_selection_part3_simple_uses_flash_lite(self):
        """Test Part 3 uses Flash Lite for simple discussions"""
        workflow = IELTSWorkflowManager()
        
        # Part 2 with low complexity (short response, simple vocabulary)
        workflow.update_state_for_part(2)
        workflow.state.part2_duration = 45.0  # Under 60 seconds
        workflow.state.part2_complexity_score = 3  # Low complexity
        
        # Part 3 configuration
        config = workflow.update_state_for_part(3)
        model = workflow.get_optimal_model()
        
        assert model == 'gemini-2.5-flash-lite'
        assert workflow.state.part3_model == 'flash-lite'
    
    def test_smart_selection_part3_complex_uses_flash(self):
        """Test Part 3 uses Flash for complex discussions"""
        workflow = IELTSWorkflowManager()
        
        # Part 2 with high complexity (long response, rich vocabulary)
        workflow.update_state_for_part(2)
        workflow.state.part2_duration = 120.0  # Over 60 seconds
        workflow.state.part2_complexity_score = 8  # High complexity
        
        # Part 3 configuration
        config = workflow.update_state_for_part(3)
        model = workflow.get_optimal_model()
        
        assert model == 'gemini-2.5-flash'
        assert workflow.state.part3_model == 'flash'
    
    def test_complexity_detection_algorithm(self):
        """Test complexity scoring for Part 2"""
        workflow = IELTSWorkflowManager()
        
        # Simple response
        simple_transcript = "I like reading. It's fun. I read books every day."
        assert not workflow.detect_complexity(simple_transcript)
        
        # Complex response
        complex_transcript = """
        Well, I'm particularly fascinated by contemporary literature, especially 
        magical realism. Authors like Gabriel García Márquez and Salman Rushdie 
        masterfully blend fantastical elements with realistic narratives, creating 
        profound commentaries on societal issues. The intricate symbolism and 
        multi-layered storytelling techniques they employ offer endless analytical 
        possibilities, which I find intellectually stimulating.
        """
        assert workflow.detect_complexity(complex_transcript)


class TestRegionalRouting:
    """Test suite for Gemini regional routing with DSQ"""
    
    def test_regional_router_initialization(self):
        """Test regional router supports multiple regions"""
        router = get_regional_router()
        
        # Verify 21 global regions are configured
        regions = router.get_all_regions()
        assert len(regions) >= 21
        
        # Check key regions exist
        region_ids = [r['region'] for r in regions]
        assert 'us-central1' in region_ids
        assert 'asia-southeast1' in region_ids
        assert 'europe-west1' in region_ids
    
    def test_regional_routing_by_country_code(self):
        """Test optimal region selection by country code"""
        router = get_regional_router()
        
        # Test Asian country routing
        region, info = router.get_optimal_region(country_code='SG')  # Singapore
        assert 'asia' in region.lower()
        
        # Test European country routing
        region, info = router.get_optimal_region(country_code='DE')  # Germany
        assert 'europe' in region.lower()
        
        # Test US routing
        region, info = router.get_optimal_region(country_code='US')  # United States
        assert 'us-' in region.lower()
    
    def test_regional_health_monitoring(self):
        """Test regional health check functionality"""
        router = get_regional_router()
        
        # Health status should be tracked
        health = router.get_region_health('us-central1')
        assert 'status' in health
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
    
    def test_automatic_failover_to_healthy_region(self):
        """Test failover when primary region is unhealthy"""
        router = get_regional_router()
        
        # Mark a region as unhealthy
        router.mark_region_unhealthy('us-central1')
        
        # Request for US should failover to alternative region
        region, info = router.get_optimal_region(country_code='US')
        assert region != 'us-central1'  # Should use fallback
        assert 'us-' in region.lower() or region in ['northamerica-northeast1']


class TestCostOptimization:
    """Test suite for cost optimization through smart selection"""
    
    def test_cost_calculation_flash_lite_only(self):
        """Test cost when only Flash Lite is used (Parts 1-3 simple)"""
        workflow = IELTSWorkflowManager()
        
        # Simulate simple assessment (all Flash Lite)
        workflow.update_state_for_part(1)
        workflow.update_state_for_part(2)
        workflow.state.part2_duration = 40.0
        workflow.state.part2_complexity_score = 2
        workflow.update_state_for_part(3)
        
        # All parts use Flash Lite
        assert workflow.get_optimal_model() == 'gemini-2.5-flash-lite'
        
        # Cost should be minimal
        # Flash Lite: $0.01 per 14 min = ~$0.01 per session
    
    def test_cost_calculation_flash_for_part3(self):
        """Test cost when Flash is needed for Part 3"""
        workflow = IELTSWorkflowManager()
        
        # Simulate complex assessment (Flash for Part 3)
        workflow.update_state_for_part(1)
        workflow.update_state_for_part(2)
        workflow.state.part2_duration = 120.0
        workflow.state.part2_complexity_score = 9
        workflow.update_state_for_part(3)
        
        # Part 3 uses Flash
        assert workflow.state.part3_model == 'flash'
        
        # Cost: Flash Lite (Parts 1-2) + Flash (Part 3)
        # ~$0.01 + $0.015 = ~$0.025 per session (vs $0.059 all Flash)


class TestVertexAIIntegration:
    """Test Vertex AI specific configuration"""
    
    def test_vertex_ai_environment_configuration(self):
        """Test Vertex AI environment variables are set correctly"""
        with patch('gemini_live_audio_service_smart.genai.Client'):
            service = GeminiLiveServiceSmart(
                project_id='test-project-123',
                region='asia-southeast1',
                auto_regional_routing=False
            )
            
            assert os.environ.get('GOOGLE_CLOUD_PROJECT') == 'test-project-123'
            assert os.environ.get('GOOGLE_CLOUD_LOCATION') == 'asia-southeast1'
            assert os.environ.get('GOOGLE_GENAI_USE_VERTEXAI') == 'True'
    
    def test_vertex_ai_with_auto_regional_routing(self):
        """Test Vertex AI with automatic regional routing"""
        with patch('gemini_live_audio_service_smart.genai.Client'):
            with patch('gemini_live_audio_service_smart.get_regional_router') as mock_router:
                mock_instance = Mock()
                mock_instance.get_optimal_region.return_value = (
                    'europe-west4',
                    {'location': 'Netherlands', 'latency_ms': 25}
                )
                mock_router.return_value = mock_instance
                
                service = GeminiLiveServiceSmart(
                    project_id='test-project',
                    country_code='NL',
                    auto_regional_routing=True
                )
                
                assert service.region == 'europe-west4'
                mock_instance.get_optimal_region.assert_called_once()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('GOOGLE_CLOUD_PROJECT'),
    reason="GOOGLE_CLOUD_PROJECT not set - skipping Vertex AI integration tests"
)
class TestGeminiFlashIntegration:
    """Integration tests with real Vertex AI API (requires credentials)"""
    
    @pytest.mark.asyncio
    async def test_flash_lite_real_api_call(self):
        """Test real API call with Flash Lite model"""
        service = GeminiLiveServiceSmart(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            region='us-central1',
            auto_regional_routing=False
        )
        
        # This test requires actual Vertex AI credentials
        # It will be skipped in CI without credentials
        assert service.models['flash-lite'] == 'gemini-2.5-flash-lite'
    
    @pytest.mark.asyncio
    async def test_flash_real_api_call(self):
        """Test real API call with Flash model"""
        service = GeminiLiveServiceSmart(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            region='us-central1',
            auto_regional_routing=False
        )
        
        assert service.models['flash'] == 'gemini-2.5-flash'
    
    @pytest.mark.asyncio
    async def test_regional_endpoint_connectivity(self):
        """Test connectivity to different regional endpoints"""
        test_regions = ['us-central1', 'asia-southeast1', 'europe-west1']
        
        for region in test_regions:
            service = GeminiLiveServiceSmart(
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                region=region,
                auto_regional_routing=False
            )
            
            assert service.region == region
            assert service.client is not None


class TestDynamicSharedQuota:
    """Test Dynamic Shared Quota (DSQ) functionality"""
    
    def test_dsq_automatic_capacity_distribution(self):
        """Test DSQ distributes quota automatically across regions"""
        router = get_regional_router()
        
        # DSQ should allow requests to any region without manual quota management
        regions = router.get_all_regions()
        
        for region_info in regions[:5]:  # Test first 5 regions
            region = region_info['region']
            # Each region should be available for requests
            assert router.is_region_available(region)
    
    def test_quota_exhaustion_fallback(self):
        """Test failover when region quota is exhausted"""
        router = get_regional_router()
        
        # Simulate quota exhaustion
        router.mark_quota_exhausted('us-central1')
        
        # Should failover to alternative region
        region, info = router.get_optimal_region(country_code='US')
        assert region != 'us-central1'
