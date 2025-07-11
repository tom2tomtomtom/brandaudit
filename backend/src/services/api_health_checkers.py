import requests
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from .api_types import APIStatus, APIHealthInfo


class OpenRouterHealthChecker:
    """Health checker specifically for OpenRouter API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = logging.getLogger(__name__)
    
    def check_health(self) -> APIHealthInfo:
        """Perform lightweight health check for OpenRouter API"""
        start_time = time.time()
        
        if not self.api_key:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="API key not configured"
            )
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://brand-audit-tool.com',
                'X-Title': 'Brand Audit Tool'
            }
            
            # Use models endpoint for lightweight check
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Verify we got actual model data
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    return APIHealthInfo(
                        status=APIStatus.HEALTHY,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        last_success=datetime.utcnow()
                    )
                else:
                    return APIHealthInfo(
                        status=APIStatus.DEGRADED,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        error_message="Empty response from models endpoint"
                    )
            
            elif response.status_code == 401:
                return APIHealthInfo(
                    status=APIStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Invalid API key"
                )
            
            elif response.status_code == 429:
                return APIHealthInfo(
                    status=APIStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Rate limit exceeded"
                )
            
            else:
                return APIHealthInfo(
                    status=APIStatus.DEGRADED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:100]}"
                )
        
        except requests.exceptions.Timeout:
            return APIHealthInfo(
                status=APIStatus.DEGRADED,
                last_check=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message="Request timeout"
            )
        
        except requests.exceptions.ConnectionError:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="Connection error"
            )
        
        except Exception as e:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message=f"Unexpected error: {str(e)[:100]}"
            )


class NewsAPIHealthChecker:
    """Health checker specifically for NewsAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.logger = logging.getLogger(__name__)
    
    def check_health(self) -> APIHealthInfo:
        """Perform lightweight health check for NewsAPI"""
        start_time = time.time()
        
        if not self.api_key:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="API key not configured"
            )
        
        try:
            headers = {
                'X-API-Key': self.api_key,
                'User-Agent': 'Brand Audit Tool/1.0'
            }
            
            # Use sources endpoint for lightweight check
            response = requests.get(
                f"{self.base_url}/sources",
                headers=headers,
                params={'pageSize': '1', 'language': 'en'},
                timeout=15
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok' and 'sources' in data:
                    return APIHealthInfo(
                        status=APIStatus.HEALTHY,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        last_success=datetime.utcnow()
                    )
                else:
                    return APIHealthInfo(
                        status=APIStatus.DEGRADED,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        error_message="Invalid response format"
                    )
            
            elif response.status_code == 401:
                return APIHealthInfo(
                    status=APIStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Invalid API key"
                )
            
            elif response.status_code == 429:
                return APIHealthInfo(
                    status=APIStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Rate limit exceeded"
                )
            
            else:
                return APIHealthInfo(
                    status=APIStatus.DEGRADED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:100]}"
                )
        
        except requests.exceptions.Timeout:
            return APIHealthInfo(
                status=APIStatus.DEGRADED,
                last_check=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message="Request timeout"
            )
        
        except requests.exceptions.ConnectionError:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="Connection error"
            )
        
        except Exception as e:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message=f"Unexpected error: {str(e)[:100]}"
            )


class BrandFetchHealthChecker:
    """Health checker specifically for BrandFetch API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.brandfetch.io/v2"
        self.logger = logging.getLogger(__name__)
    
    def check_health(self) -> APIHealthInfo:
        """Perform lightweight health check for BrandFetch API"""
        start_time = time.time()
        
        if not self.api_key:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="API key not configured"
            )
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Use search endpoint with a well-known domain for lightweight check
            response = requests.get(
                f"{self.base_url}/search/apple.com",
                headers=headers,
                params={'limit': '1'},
                timeout=20
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # BrandFetch returns different structures, just verify we got data
                try:
                    data = response.json()
                    return APIHealthInfo(
                        status=APIStatus.HEALTHY,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        last_success=datetime.utcnow()
                    )
                except ValueError:
                    return APIHealthInfo(
                        status=APIStatus.DEGRADED,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        error_message="Invalid JSON response"
                    )
            
            elif response.status_code == 401:
                return APIHealthInfo(
                    status=APIStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Invalid API key"
                )
            
            elif response.status_code == 429:
                return APIHealthInfo(
                    status=APIStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message="Rate limit exceeded"
                )
            
            else:
                return APIHealthInfo(
                    status=APIStatus.DEGRADED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}: {response.text[:100]}"
                )
        
        except requests.exceptions.Timeout:
            return APIHealthInfo(
                status=APIStatus.DEGRADED,
                last_check=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message="Request timeout"
            )
        
        except requests.exceptions.ConnectionError:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message="Connection error"
            )
        
        except Exception as e:
            return APIHealthInfo(
                status=APIStatus.UNAVAILABLE,
                last_check=datetime.utcnow(),
                error_message=f"Unexpected error: {str(e)[:100]}"
            )
