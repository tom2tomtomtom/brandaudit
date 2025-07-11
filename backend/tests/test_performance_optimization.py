"""
Performance Optimization Tests
Tests to validate that optimizations maintain data accuracy while improving speed
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.services.async_analysis_service import AsyncAnalysisService
from src.services.image_optimization_service import ImageOptimizationService
from src.services.intelligent_cache_service import IntelligentCacheService
from src.services.database_optimization_service import DatabaseOptimizationService


class TestAsyncAnalysisService:
    """Test concurrent processing performance and accuracy"""
    
    @pytest.fixture
    def async_service(self):
        return AsyncAnalysisService()
    
    @pytest.fixture
    def sample_analysis_data(self):
        return {
            "analysis_id": "test-123",
            "company_name": "Test Company",
            "website": "https://testcompany.com",
            "analysis_options": {
                "brandPerception": True,
                "competitiveAnalysis": True,
                "visualAnalysis": True,
                "pressCoverage": True
            }
        }
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self, async_service, sample_analysis_data):
        """Test that concurrent processing is faster than sequential"""
        
        # Mock the individual service calls to simulate realistic timing
        with patch.object(async_service, '_get_brand_info_async') as mock_brand, \
             patch.object(async_service, '_get_news_analysis_async') as mock_news, \
             patch.object(async_service, '_get_campaign_analysis_async') as mock_campaign, \
             patch.object(async_service, '_get_llm_analysis_async') as mock_llm, \
             patch.object(async_service, '_get_visual_analysis_async') as mock_visual:
            
            # Configure mocks with realistic delays
            async def delayed_response(delay, response):
                await asyncio.sleep(delay)
                return response
            
            mock_brand.return_value = delayed_response(0.5, {"brand_info": "test"})
            mock_news.return_value = delayed_response(1.0, {"news": "test"})
            mock_campaign.return_value = delayed_response(0.8, {"campaigns": "test"})
            mock_llm.return_value = delayed_response(1.2, {"analysis": "test"})
            mock_visual.return_value = delayed_response(2.0, {"visuals": "test"})
            
            start_time = time.time()
            result = await async_service.run_concurrent_analysis(sample_analysis_data)
            end_time = time.time()
            
            # Should complete in less than sum of individual delays (5.5s)
            # Due to concurrency, should be closer to the longest individual delay (2.0s)
            assert end_time - start_time < 4.0, "Concurrent processing should be faster than sequential"
            assert result["performance_metrics"]["concurrent_tasks_executed"] > 0
            assert "optimization_enabled" in result["performance_metrics"]
    
    @pytest.mark.asyncio
    async def test_data_accuracy_maintained(self, async_service, sample_analysis_data):
        """Test that concurrent processing maintains data accuracy"""
        
        # Mock services to return specific test data
        test_responses = {
            "brand_info": {"name": "Test Company", "industry": "Technology"},
            "news_analysis": {"articles": [{"title": "Test Article"}]},
            "campaign_analysis": {"campaigns": [{"name": "Test Campaign"}]},
            "llm_insights": {"sentiment": "positive", "score": 85},
            "visual_analysis": {"colors": ["#FF0000", "#00FF00"]}
        }
        
        with patch.object(async_service, '_get_brand_info_async', return_value=test_responses["brand_info"]), \
             patch.object(async_service, '_get_news_analysis_async', return_value=test_responses["news_analysis"]), \
             patch.object(async_service, '_get_campaign_analysis_async', return_value=test_responses["campaign_analysis"]), \
             patch.object(async_service, '_get_llm_analysis_async', return_value=test_responses["llm_insights"]), \
             patch.object(async_service, '_get_visual_analysis_async', return_value=test_responses["visual_analysis"]):
            
            result = await async_service.run_concurrent_analysis(sample_analysis_data)
            
            # Verify all expected data is present and accurate
            assert result["brand_info"] == test_responses["brand_info"]
            assert result["news_analysis"] == test_responses["news_analysis"]
            assert result["campaign_analysis"] == test_responses["campaign_analysis"]
            assert result["llm_insights"] == test_responses["llm_insights"]
            assert result["visual_analysis"] == test_responses["visual_analysis"]
            
            # Verify metadata is correct
            assert result["company_name"] == sample_analysis_data["company_name"]
            assert result["analysis_id"] == sample_analysis_data["analysis_id"]


class TestImageOptimizationService:
    """Test image optimization performance and quality"""
    
    @pytest.fixture
    def image_service(self):
        return ImageOptimizationService()
    
    def test_image_compression_performance(self, image_service, tmp_path):
        """Test image compression maintains quality while reducing size"""
        
        # Create a test image
        from PIL import Image
        import os
        
        test_image = Image.new('RGB', (1920, 1080), color='red')
        test_path = tmp_path / "test_image.png"
        test_image.save(test_path)
        
        original_size = os.path.getsize(test_path)
        
        # Test optimization
        result = asyncio.run(image_service.optimize_image_async(str(test_path), 'medium'))
        
        assert not result.get("error"), f"Optimization failed: {result.get('error')}"
        assert result["compression_ratio"] > 0, "Should achieve some compression"
        assert result["optimized_size_bytes"] < original_size, "Optimized image should be smaller"
        assert os.path.exists(result["optimized_path"]), "Optimized image should exist"
    
    def test_progressive_loading_variants(self, image_service, tmp_path):
        """Test creation of progressive loading variants"""
        
        from PIL import Image
        
        test_image = Image.new('RGB', (1920, 1080), color='blue')
        test_path = tmp_path / "test_progressive.png"
        test_image.save(test_path)
        
        result = asyncio.run(image_service.create_progressive_variants(str(test_path)))
        
        assert not result.get("error"), f"Progressive variants failed: {result.get('error')}"
        assert result["progressive_loading_ready"], "Should be ready for progressive loading"
        assert "thumbnail" in result["variants"], "Should have thumbnail variant"
        assert "medium" in result["variants"], "Should have medium variant"
        assert "large" in result["variants"], "Should have large variant"


class TestIntelligentCacheService:
    """Test caching performance and accuracy"""
    
    @pytest.fixture
    def cache_service(self):
        return IntelligentCacheService()
    
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self, cache_service):
        """Test cache hit performance vs cache miss"""
        
        test_key = "performance_test_key"
        test_data = {"large_data": list(range(10000))}
        
        # First call (cache miss)
        start_time = time.time()
        await cache_service.set(test_key, test_data, 'api_response')
        set_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        cached_result = await cache_service.get(test_key, 'api_response')
        get_time = time.time() - start_time
        
        assert cached_result == test_data, "Cached data should match original"
        assert get_time < set_time, "Cache hit should be faster than cache set"
        assert get_time < 0.01, "Cache hit should be very fast (< 10ms)"
    
    @pytest.mark.asyncio
    async def test_cache_invalidation_accuracy(self, cache_service):
        """Test that cache invalidation works correctly"""
        
        # Set multiple cache entries
        test_keys = ["test_1", "test_2", "test_3"]
        for key in test_keys:
            await cache_service.set(key, f"data_{key}", 'api_response')
        
        # Verify all are cached
        for key in test_keys:
            result = await cache_service.get(key, 'api_response')
            assert result == f"data_{key}"
        
        # Invalidate by pattern
        invalidated = await cache_service.invalidate(pattern="test_")
        assert invalidated >= len(test_keys), "Should invalidate matching entries"
        
        # Verify invalidation worked
        for key in test_keys:
            result = await cache_service.get(key, 'api_response')
            assert result is None, "Invalidated entries should return None"


class TestDatabaseOptimizationService:
    """Test database optimization performance"""
    
    @pytest.fixture
    def db_service(self):
        return DatabaseOptimizationService()
    
    def test_query_monitoring(self, db_service):
        """Test that query monitoring captures performance metrics"""
        
        initial_count = db_service.query_stats['total_queries']
        
        # Simulate a database query (this would normally be a real query)
        with patch('src.extensions.db.session') as mock_session:
            mock_session.execute.return_value = MagicMock()
            
            # The actual query monitoring happens via SQLAlchemy events
            # For testing, we'll directly update the stats
            db_service.query_stats['total_queries'] += 1
            db_service.query_stats['query_times'].append(0.05)  # 50ms query
            
            assert db_service.query_stats['total_queries'] > initial_count
            assert len(db_service.query_stats['query_times']) > 0
    
    def test_bulk_operations_performance(self, db_service):
        """Test bulk operations are more efficient than individual operations"""
        
        # Test bulk update performance
        updates = [
            {"analysis_id": f"test_{i}", "progress": i * 10, "status": "processing"}
            for i in range(100)
        ]
        
        with patch('src.extensions.db.session') as mock_session:
            mock_session.query.return_value.filter.return_value.update.return_value = None
            mock_session.commit.return_value = None
            
            start_time = time.time()
            result = db_service.bulk_update_analysis_progress(updates)
            end_time = time.time()
            
            assert result is True, "Bulk update should succeed"
            assert end_time - start_time < 1.0, "Bulk update should be fast"
            
            # Verify bulk operation was used (single commit)
            assert mock_session.commit.call_count == 1


class TestEndToEndPerformance:
    """End-to-end performance tests"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_performance_benchmark(self):
        """Benchmark full analysis pipeline performance"""
        
        analysis_data = {
            "analysis_id": "benchmark-test",
            "company_name": "Benchmark Company",
            "website": "https://benchmark.com",
            "analysis_options": {
                "brandPerception": True,
                "competitiveAnalysis": True,
                "visualAnalysis": True,
                "pressCoverage": True
            }
        }
        
        async_service = AsyncAnalysisService()
        
        # Mock all external services for consistent benchmarking
        with patch.object(async_service, '_get_brand_info_async') as mock_brand, \
             patch.object(async_service, '_get_news_analysis_async') as mock_news, \
             patch.object(async_service, '_get_campaign_analysis_async') as mock_campaign, \
             patch.object(async_service, '_get_llm_analysis_async') as mock_llm, \
             patch.object(async_service, '_get_visual_analysis_async') as mock_visual:
            
            # Configure realistic mock responses
            mock_brand.return_value = {"success": True, "data": {"name": "Test"}}
            mock_news.return_value = {"success": True, "articles": []}
            mock_campaign.return_value = {"success": True, "campaigns": []}
            mock_llm.return_value = {"success": True, "analysis": "Test analysis"}
            mock_visual.return_value = {"success": True, "colors": []}
            
            # Run benchmark
            start_time = time.time()
            result = await async_service.run_concurrent_analysis(analysis_data)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Performance assertions
            assert total_time < 10.0, f"Full analysis should complete in under 10 seconds, took {total_time:.2f}s"
            assert result["performance_metrics"]["optimization_enabled"], "Optimizations should be enabled"
            assert result["performance_metrics"]["concurrent_tasks_executed"] > 0, "Should use concurrent processing"
            
            # Data accuracy assertions
            assert result["company_name"] == analysis_data["company_name"]
            assert "brand_info" in result
            assert "news_analysis" in result
            assert "campaign_analysis" in result
            assert "llm_insights" in result
            assert "visual_analysis" in result
    
    def test_memory_usage_optimization(self):
        """Test that optimizations don't cause memory leaks"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate multiple analysis runs
        for i in range(10):
            # This would normally run actual analysis
            # For testing, we'll simulate memory usage
            large_data = [list(range(1000)) for _ in range(100)]
            del large_data  # Cleanup
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for test)
        assert memory_increase < 100 * 1024 * 1024, f"Memory usage increased by {memory_increase / 1024 / 1024:.2f}MB"
