import requests
import os
from typing import Dict, List, Optional
from datetime import datetime

class BrandDataService:
    """Service for integrating with brand and company data APIs"""
    
    def __init__(self):
        self.brandfetch_api_key = os.getenv('BRANDFETCH_API_KEY')
        self.brandfetch_base_url = 'https://api.brandfetch.io/v2'
        self.opencorporates_api_key = os.getenv('OPENCORPORATES_API_KEY')
        self.opencorporates_base_url = 'https://api.opencorporates.com/v0.4'
        
    def get_brand_assets(self, domain: str) -> Dict:
        """Get brand assets from Brandfetch API"""
        try:
            if self.brandfetch_api_key:
                return self._fetch_brandfetch_data(domain)
            else:
                return self._get_mock_brand_assets(domain)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def get_company_info(self, company_name: str) -> Dict:
        """Get company information from OpenCorporates API"""
        try:
            if self.opencorporates_api_key:
                return self._fetch_opencorporates_data(company_name)
            else:
                return self._get_mock_company_info(company_name)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def search_companies(self, query: str, limit: int = 10) -> Dict:
        """Search for companies by name"""
        try:
            if self.opencorporates_api_key:
                return self._search_opencorporates(query, limit)
            else:
                return self._get_mock_company_search(query, limit)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'companies': []
            }
    
    def analyze_brand_consistency(self, brand_assets: Dict) -> Dict:
        """Analyze brand consistency from assets"""
        try:
            if not brand_assets or not brand_assets.get('success'):
                return {
                    'success': False,
                    'error': 'No brand assets provided for analysis'
                }
            
            assets = brand_assets.get('data', {})
            
            # Analyze logos
            logos = assets.get('logos', [])
            logo_consistency = self._analyze_logo_consistency(logos)
            
            # Analyze colors
            colors = assets.get('colors', [])
            color_consistency = self._analyze_color_consistency(colors)
            
            # Analyze fonts
            fonts = assets.get('fonts', [])
            font_consistency = self._analyze_font_consistency(fonts)
            
            # Calculate overall consistency score
            scores = [logo_consistency['score'], color_consistency['score'], font_consistency['score']]
            overall_score = sum(scores) / len(scores) if scores else 0
            
            return {
                'success': True,
                'overall_score': round(overall_score, 1),
                'logo_analysis': logo_consistency,
                'color_analysis': color_consistency,
                'font_analysis': font_consistency,
                'recommendations': self._generate_consistency_recommendations(
                    logo_consistency, color_consistency, font_consistency
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ''
        
        # Remove protocol
        if url.startswith('http://'):
            url = url[7:]
        elif url.startswith('https://'):
            url = url[8:]
        
        # Remove www
        if url.startswith('www.'):
            url = url[4:]
        
        # Remove path
        if '/' in url:
            url = url.split('/')[0]
        
        return url
    
    def _fetch_brandfetch_data(self, domain: str) -> Dict:
        """Fetch data from Brandfetch API"""
        headers = {
            'Authorization': f'Bearer {self.brandfetch_api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{self.brandfetch_base_url}/brands/{domain}',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'data': data
            }
        elif response.status_code == 404:
            return {
                'success': False,
                'error': 'Brand not found',
                'data': None
            }
        else:
            raise Exception(f"Brandfetch API error: {response.status_code} - {response.text}")
    
    def _fetch_opencorporates_data(self, company_name: str) -> Dict:
        """Fetch data from OpenCorporates API"""
        params = {
            'q': company_name,
            'format': 'json'
        }
        
        if self.opencorporates_api_key:
            params['api_token'] = self.opencorporates_api_key
        
        response = requests.get(
            f'{self.opencorporates_base_url}/companies/search',
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('results', {}).get('companies', [])
            
            if companies:
                # Return the first (most relevant) company
                company = companies[0]['company']
                return {
                    'success': True,
                    'data': company
                }
            else:
                return {
                    'success': False,
                    'error': 'Company not found',
                    'data': None
                }
        else:
            raise Exception(f"OpenCorporates API error: {response.status_code} - {response.text}")
    
    def _search_opencorporates(self, query: str, limit: int) -> Dict:
        """Search companies in OpenCorporates"""
        params = {
            'q': query,
            'format': 'json',
            'per_page': limit
        }
        
        if self.opencorporates_api_key:
            params['api_token'] = self.opencorporates_api_key
        
        response = requests.get(
            f'{self.opencorporates_base_url}/companies/search',
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('results', {}).get('companies', [])
            
            return {
                'success': True,
                'companies': [comp['company'] for comp in companies]
            }
        else:
            raise Exception(f"OpenCorporates API error: {response.status_code} - {response.text}")
    
    def _get_mock_brand_assets(self, domain: str) -> Dict:
        """Return mock brand assets data"""
        return {
            'success': True,
            'data': {
                'name': domain.replace('.com', '').title(),
                'domain': domain,
                'logos': [
                    {
                        'type': 'logo',
                        'theme': 'light',
                        'formats': [
                            {
                                'format': 'png',
                                'src': f'https://via.placeholder.com/200x100/0066CC/FFFFFF?text={domain.split(".")[0].upper()}',
                                'background': 'transparent',
                                'size': 5120
                            }
                        ]
                    },
                    {
                        'type': 'symbol',
                        'theme': 'light',
                        'formats': [
                            {
                                'format': 'png',
                                'src': f'https://via.placeholder.com/100x100/0066CC/FFFFFF?text={domain.split(".")[0][0].upper()}',
                                'background': 'transparent',
                                'size': 2048
                            }
                        ]
                    }
                ],
                'colors': [
                    {
                        'hex': '#0066CC',
                        'type': 'brand',
                        'brightness': 128
                    },
                    {
                        'hex': '#FFFFFF',
                        'type': 'accent',
                        'brightness': 255
                    },
                    {
                        'hex': '#333333',
                        'type': 'dark',
                        'brightness': 51
                    }
                ],
                'fonts': [
                    {
                        'name': 'Arial',
                        'type': 'sans-serif',
                        'origin': 'system'
                    },
                    {
                        'name': 'Helvetica',
                        'type': 'sans-serif',
                        'origin': 'system'
                    }
                ],
                'images': [
                    {
                        'type': 'banner',
                        'formats': [
                            {
                                'format': 'jpg',
                                'src': f'https://via.placeholder.com/1200x400/0066CC/FFFFFF?text={domain.split(".")[0].upper()}+Banner',
                                'size': 15360
                            }
                        ]
                    }
                ]
            }
        }
    
    def _get_mock_company_info(self, company_name: str) -> Dict:
        """Return mock company information"""
        return {
            'success': True,
            'data': {
                'name': company_name,
                'company_number': 'C123456789',
                'jurisdiction_code': 'us_de',
                'incorporation_date': '2010-01-15',
                'company_type': 'Corporation',
                'status': 'Active',
                'registered_address': {
                    'street_address': '123 Business St',
                    'locality': 'San Francisco',
                    'region': 'CA',
                    'postal_code': '94105',
                    'country': 'United States'
                },
                'officers': [
                    {
                        'name': 'John Smith',
                        'position': 'CEO',
                        'start_date': '2010-01-15'
                    },
                    {
                        'name': 'Jane Doe',
                        'position': 'CFO',
                        'start_date': '2012-03-01'
                    }
                ],
                'industry_codes': [
                    {
                        'code': '541511',
                        'description': 'Custom Computer Programming Services'
                    }
                ]
            }
        }
    
    def _get_mock_company_search(self, query: str, limit: int) -> Dict:
        """Return mock company search results"""
        companies = []
        for i in range(min(limit, 3)):
            companies.append({
                'name': f'{query} {["Inc", "Corp", "LLC"][i]}',
                'company_number': f'C{123456789 + i}',
                'jurisdiction_code': 'us_de',
                'incorporation_date': f'201{i}-01-15',
                'status': 'Active'
            })
        
        return {
            'success': True,
            'companies': companies
        }
    
    def _analyze_logo_consistency(self, logos: List[Dict]) -> Dict:
        """Analyze logo consistency"""
        if not logos:
            return {
                'score': 0,
                'issues': ['No logos found'],
                'recommendations': ['Upload brand logos for analysis']
            }
        
        # Mock analysis
        score = 85
        issues = []
        recommendations = []
        
        if len(logos) < 2:
            issues.append('Limited logo variations available')
            recommendations.append('Provide multiple logo variations (light, dark, symbol)')
        
        return {
            'score': score,
            'logo_count': len(logos),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_color_consistency(self, colors: List[Dict]) -> Dict:
        """Analyze color consistency"""
        if not colors:
            return {
                'score': 0,
                'issues': ['No brand colors found'],
                'recommendations': ['Define brand color palette']
            }
        
        # Mock analysis
        score = 90
        issues = []
        recommendations = []
        
        primary_colors = [c for c in colors if c.get('type') == 'brand']
        if not primary_colors:
            issues.append('No primary brand color defined')
            recommendations.append('Define primary brand color')
        
        return {
            'score': score,
            'color_count': len(colors),
            'primary_colors': len(primary_colors),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _analyze_font_consistency(self, fonts: List[Dict]) -> Dict:
        """Analyze font consistency"""
        if not fonts:
            return {
                'score': 0,
                'issues': ['No brand fonts found'],
                'recommendations': ['Define brand typography']
            }
        
        # Mock analysis
        score = 80
        issues = []
        recommendations = []
        
        if len(fonts) > 3:
            issues.append('Too many fonts may reduce consistency')
            recommendations.append('Limit to 2-3 primary fonts')
        
        return {
            'score': score,
            'font_count': len(fonts),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _generate_consistency_recommendations(self, logo_analysis: Dict, color_analysis: Dict, font_analysis: Dict) -> List[str]:
        """Generate overall consistency recommendations"""
        recommendations = []
        
        # Combine recommendations from all analyses
        for analysis in [logo_analysis, color_analysis, font_analysis]:
            recommendations.extend(analysis.get('recommendations', []))
        
        # Add general recommendations
        if logo_analysis['score'] < 80 or color_analysis['score'] < 80 or font_analysis['score'] < 80:
            recommendations.append('Create comprehensive brand guidelines document')
            recommendations.append('Conduct brand audit across all touchpoints')
        
        return list(set(recommendations))  # Remove duplicates

# Global instance
brand_data_service = BrandDataService()

