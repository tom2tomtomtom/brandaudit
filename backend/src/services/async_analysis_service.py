"""
Async Analysis Service for Concurrent Brand Audit Processing
Optimizes performance by running independent analysis tasks concurrently
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time

from src.services.llm_service import LLMService
from src.services.news_service import NewsService
from src.services.brand_data_service import BrandDataService
from src.services.visual_analysis_service import VisualAnalysisService
from src.services.campaign_analysis_service import CampaignAnalysisService

import os


class AsyncAnalysisService:
    """
    Orchestrates concurrent brand analysis tasks for optimal performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_service = LLMService()
        self.news_service = NewsService()
        self.brand_data_service = BrandDataService()
        self.visual_analysis_service = VisualAnalysisService()
        self.campaign_analysis_service = CampaignAnalysisService()
        
        # Thread pool for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Semaphore to limit concurrent API calls
        self.api_semaphore = asyncio.Semaphore(3)
        
    async def run_concurrent_analysis(self, analysis_data: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """
        Run brand analysis with concurrent processing for independent tasks
        """
        start_time = time.time()
        self.logger.info(f"Starting concurrent analysis for {analysis_data['company_name']}")
        
        results = {
            "analysis_id": analysis_data.get("analysis_id"),
            "company_name": analysis_data["company_name"],
            "website": analysis_data.get("website"),
            "started_at": datetime.utcnow().isoformat(),
            "brand_health_score": 0,
            "key_findings": [],
            "performance_metrics": {},
            "errors": []
        }
        
        # Update progress
        if progress_callback:
            await progress_callback(10, "Initializing concurrent analysis...")
        
        try:
            # Create concurrent tasks for independent operations
            tasks = []
            
            # Task 1: Brand Information (prerequisite for other tasks)
            if analysis_data.get("website"):
                brand_info_task = self._get_brand_info_async(analysis_data)
                tasks.append(("brand_info", brand_info_task))
            
            # Task 2: News Analysis (independent)
            if analysis_data["analysis_options"].get("pressCoverage"):
                news_task = self._get_news_analysis_async(analysis_data)
                tasks.append(("news_analysis", news_task))
            
            # Task 3: Campaign Analysis (independent)
            if analysis_data["analysis_options"].get("competitiveAnalysis"):
                campaign_task = self._get_campaign_analysis_async(analysis_data)
                tasks.append(("campaign_analysis", campaign_task))
            
            # Execute first batch of independent tasks
            if progress_callback:
                await progress_callback(20, "Running concurrent data collection...")
            
            batch_results = await self._execute_task_batch(tasks)
            results.update(batch_results)
            
            # Task 4: LLM Analysis (can use brand_info if available)
            if analysis_data["analysis_options"].get("brandPerception"):
                if progress_callback:
                    await progress_callback(50, "Running AI analysis...")
                
                llm_task = self._get_llm_analysis_async(analysis_data, results.get("brand_info"))
                llm_result = await llm_task
                results["llm_insights"] = llm_result
            
            # Task 5: Visual Analysis (can run concurrently with LLM)
            if analysis_data["analysis_options"].get("visualAnalysis", True):
                if progress_callback:
                    await progress_callback(70, "Processing visual assets...")
                
                visual_task = self._get_visual_analysis_async(analysis_data, results.get("brand_info"))
                visual_result = await visual_task
                results["visual_analysis"] = visual_result
            
            # Calculate performance metrics
            end_time = time.time()
            results["performance_metrics"] = {
                "total_duration_seconds": round(end_time - start_time, 2),
                "concurrent_tasks_executed": len(tasks),
                "optimization_enabled": True
            }
            
            if progress_callback:
                await progress_callback(100, "Analysis complete!")
            
            self.logger.info(f"Concurrent analysis completed in {results['performance_metrics']['total_duration_seconds']}s")
            
        except Exception as e:
            self.logger.error(f"Concurrent analysis failed: {str(e)}")
            results["errors"].append(f"Analysis failed: {str(e)}")
            
        return results
    
    async def _execute_task_batch(self, tasks: List[tuple]) -> Dict[str, Any]:
        """Execute a batch of tasks concurrently"""
        if not tasks:
            return {}
        
        # Run tasks concurrently
        task_futures = [task[1] for task in tasks]
        task_names = [task[0] for task in tasks]
        
        try:
            results_list = await asyncio.gather(*task_futures, return_exceptions=True)
            
            batch_results = {}
            for i, result in enumerate(results_list):
                task_name = task_names[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Task {task_name} failed: {str(result)}")
                    batch_results[task_name] = {"error": str(result)}
                else:
                    batch_results[task_name] = result
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Batch execution failed: {str(e)}")
            return {}
    
    async def _get_brand_info_async(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get brand information asynchronously"""
        async with self.api_semaphore:
            try:
                # Run in thread pool since brand_data_service is synchronous
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self.brand_data_service.get_company_info,
                    analysis_data["company_name"]
                )
                return result
            except Exception as e:
                self.logger.error(f"Brand info async failed: {str(e)}")
                return {"error": str(e)}
    
    async def _get_news_analysis_async(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get news analysis asynchronously"""
        async with self.api_semaphore:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self.news_service.search_news,
                    analysis_data["company_name"],
                    30
                )
                return result
            except Exception as e:
                self.logger.error(f"News analysis async failed: {str(e)}")
                return {"error": str(e)}
    
    async def _get_campaign_analysis_async(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get campaign analysis asynchronously"""
        async with self.api_semaphore:
            try:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self.campaign_analysis_service.discover_campaigns,
                    analysis_data["company_name"]
                )
                return result
            except Exception as e:
                self.logger.error(f"Campaign analysis async failed: {str(e)}")
                return {"error": str(e)}
    
    async def _get_llm_analysis_async(self, analysis_data: Dict[str, Any], brand_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Get LLM analysis asynchronously"""
        async with self.api_semaphore:
            try:
                # Prepare context for LLM
                context = f"Brand analysis for {analysis_data['company_name']}"
                if brand_info and not brand_info.get("error"):
                    context += f" with additional context: {str(brand_info)[:500]}"
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self.llm_service.analyze_brand_sentiment,
                    context,
                    analysis_data["company_name"]
                )
                return result
            except Exception as e:
                self.logger.error(f"LLM analysis async failed: {str(e)}")
                return {"error": str(e)}
    
    async def _get_visual_analysis_async(self, analysis_data: Dict[str, Any], brand_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Get visual analysis asynchronously"""
        try:
            website_url = analysis_data.get("website", f"https://{analysis_data['company_name'].lower().replace(' ', '')}.com")
            
            # Visual analysis service is already async
            result = await self.visual_analysis_service.analyze_brand_visuals(
                analysis_data["company_name"],
                website_url,
                brand_info
            )
            return result
        except Exception as e:
            self.logger.error(f"Visual analysis async failed: {str(e)}")
            return {"error": str(e)}
    
    def __del__(self):
        """Cleanup thread pool"""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)

    def get_capabilities(self) -> Dict[str, bool]:
        """Return available async analysis capabilities"""
        return {
            'concurrent_processing': True,
            'async_llm_calls': bool(os.environ.get('OPENROUTER_API_KEY')),
            'async_news_search': bool(os.environ.get('NEWS_API_KEY')),
            'async_brand_data': bool(os.environ.get('BRANDFETCH_API_KEY')),
            'async_visual_analysis': True,
            'progress_tracking': True
        }


# Global instance
async_analysis_service = AsyncAnalysisService()

