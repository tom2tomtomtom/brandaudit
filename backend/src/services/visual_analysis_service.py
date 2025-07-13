"""
Visual Analysis Service for Brand Audit Tool
Handles screenshot capture, color extraction, and visual asset processing
"""

import os
import json
import asyncio
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Import optimization services
try:
    from src.services.image_optimization_service import image_optimization_service
    from src.services.intelligent_cache_service import intelligent_cache
    OPTIMIZATION_SERVICES_AVAILABLE = True
except ImportError:
    OPTIMIZATION_SERVICES_AVAILABLE = False

# Visual processing imports (with fallbacks to prevent breaking existing functionality)
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available - screenshot capture disabled")

try:
    from PIL import Image, ImageDraw, ImageFont
    from colorthief import ColorThief
    import webcolors
    VISUAL_PROCESSING_AVAILABLE = True
except ImportError:
    VISUAL_PROCESSING_AVAILABLE = False
    logging.warning("Visual processing libraries not available - color extraction disabled")

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available - advanced image processing disabled")

try:
    from bs4 import BeautifulSoup
    import requests
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("Web scraping libraries not available - content analysis disabled")

# Import social media service for enhanced analysis
try:
    from .social_media_service import SocialMediaService
    SOCIAL_MEDIA_AVAILABLE = True
except ImportError:
    SOCIAL_MEDIA_AVAILABLE = False
    logging.warning("Social media service not available")


class VisualAnalysisService:
    """Service for visual brand analysis including screenshots, colors, and assets"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.assets_dir = os.path.join(os.getcwd(), 'src', 'static', 'brand_assets')
        self.ensure_assets_directory()

        # Initialize social media service if available
        if SOCIAL_MEDIA_AVAILABLE:
            self.social_service = SocialMediaService()
        else:
            self.social_service = None

        # Initialize database service for visual asset storage
        try:
            from src.services.database_service import DatabaseService
            self.db_service = DatabaseService()
            self.database_available = True
        except ImportError:
            self.db_service = None
            self.database_available = False
            self.logger.warning("Database service not available - visual assets won't be stored in database")
    
    def ensure_assets_directory(self):
        """Create assets directory structure if it doesn't exist"""
        try:
            os.makedirs(self.assets_dir, exist_ok=True)
            os.makedirs(os.path.join(self.assets_dir, 'screenshots'), exist_ok=True)
            os.makedirs(os.path.join(self.assets_dir, 'logos'), exist_ok=True)
            os.makedirs(os.path.join(self.assets_dir, 'colors'), exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create assets directory: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Return available visual analysis capabilities"""
        return {
            'screenshot_capture': PLAYWRIGHT_AVAILABLE,
            'color_extraction': VISUAL_PROCESSING_AVAILABLE,
            'image_processing': OPENCV_AVAILABLE,
            'web_scraping': WEB_SCRAPING_AVAILABLE,
            'social_media_analysis': SOCIAL_MEDIA_AVAILABLE
        }
    
    async def analyze_brand_visuals(self, brand_name: str, website_url: str, brand_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main visual analysis function - integrates Brandfetch data with visual analysis
        Returns enhanced visual data with real brand assets
        """
        self.logger.info(f"Starting visual analysis for {brand_name} at {website_url}")

        results = {
            'brand_name': brand_name,
            'website_url': website_url,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'visual_assets': {},
            'visual_scores': {},
            'errors': []
        }

        # Step 1: Integrate Brandfetch data if available
        if brand_data and not brand_data.get('error'):
            self.logger.info(f"Integrating Brandfetch data for {brand_name}")
            try:
                # Extract logos from Brandfetch
                brandfetch_logos = brand_data.get('logos', [])
                if brandfetch_logos:
                    results['visual_assets']['logos'] = brandfetch_logos
                    results['visual_scores']['logo_availability'] = 100
                    self.logger.info(f"Found {len(brandfetch_logos)} logos from Brandfetch")

                # Extract colors from Brandfetch
                brandfetch_colors = brand_data.get('colors', [])
                if brandfetch_colors:
                    results['visual_assets']['color_palette'] = {
                        'primary_colors': brandfetch_colors,
                        'source': 'brandfetch'
                    }
                    results['visual_scores']['color_consistency'] = self.calculate_color_consistency_score_from_brandfetch(brandfetch_colors)
                    self.logger.info(f"Found {len(brandfetch_colors)} colors from Brandfetch")

                # Extract fonts from Brandfetch
                brandfetch_fonts = brand_data.get('fonts', [])
                if brandfetch_fonts:
                    results['visual_assets']['fonts'] = brandfetch_fonts
                    results['visual_scores']['typography_consistency'] = 85  # Good score for having font data
                    self.logger.info(f"Found {len(brandfetch_fonts)} fonts from Brandfetch")

            except Exception as e:
                error_msg = f"Brandfetch data integration failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Screenshot capture (if available)
        if PLAYWRIGHT_AVAILABLE:
            try:
                screenshots = await self.capture_website_screenshots(website_url, brand_name)
                results['visual_assets']['screenshots'] = screenshots
                self.logger.info(f"Captured {len(screenshots)} screenshots for {brand_name}")
            except Exception as e:
                error_msg = f"Screenshot capture failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            results['errors'].append("Screenshot capture not available - Playwright not installed")
        
        # Color analysis (if screenshots available and processing enabled)
        if VISUAL_PROCESSING_AVAILABLE and 'screenshots' in results['visual_assets']:
            try:
                colors = await self.extract_brand_colors(results['visual_assets']['screenshots'])
                results['visual_assets']['color_palette'] = colors
                results['visual_scores']['color_consistency'] = self.calculate_color_consistency_score(colors)
                self.logger.info(f"Extracted {len(colors.get('primary_colors', []))} colors for {brand_name}")
            except Exception as e:
                error_msg = f"Color extraction failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            results['errors'].append("Color extraction not available - missing dependencies or screenshots")
        
        # Logo detection (if image processing available)
        if OPENCV_AVAILABLE and 'screenshots' in results['visual_assets']:
            try:
                logos = await self.detect_brand_logos(results['visual_assets']['screenshots'])
                results['visual_assets']['logos'] = logos
                results['visual_scores']['logo_quality'] = self.calculate_logo_quality_score(logos)
                self.logger.info(f"Detected {len(logos)} potential logos for {brand_name}")
            except Exception as e:
                error_msg = f"Logo detection failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)

        # Typography analysis (if screenshots available)
        if 'screenshots' in results['visual_assets']:
            try:
                typography = await self.detect_typography_patterns(
                    results['visual_assets']['screenshots'],
                    website_url
                )
                results['visual_assets']['typography'] = typography
                results['visual_scores']['typography_consistency'] = typography.get('font_consistency', {}).get('overall_score', 0)
                self.logger.info(f"Analyzed typography: found {len(typography.get('fonts_detected', []))} fonts")
            except Exception as e:
                error_msg = f"Typography analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            results['errors'].append("Typography analysis not available - no screenshots")

        # Web content analysis (if scraping available)
        if WEB_SCRAPING_AVAILABLE:
            try:
                content_analysis = await self.analyze_website_content(website_url)
                results['visual_assets']['content_analysis'] = content_analysis
                results['visual_scores']['content_quality'] = self.calculate_content_quality_score(content_analysis)
                self.logger.info(f"Analyzed website content for {brand_name}")
            except Exception as e:
                error_msg = f"Content analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)

        # Social media analysis (if service available)
        if self.social_service:
            try:
                social_analysis = await self.social_service.analyze_social_presence(brand_name, website_url)
                results['visual_assets']['social_media'] = social_analysis
                results['visual_scores']['social_presence'] = self.calculate_social_presence_score(social_analysis)
                self.logger.info(f"Analyzed social media presence for {brand_name}")
            except Exception as e:
                error_msg = f"Social media analysis failed: {str(e)}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)

        # Visual consistency analysis (comprehensive analysis of all assets)
        try:
            consistency_analysis = await self.analyze_visual_consistency(results['visual_assets'])
            results['visual_consistency'] = consistency_analysis
            results['visual_scores']['overall_consistency'] = consistency_analysis.get('overall_score', 0)
            self.logger.info(f"Visual consistency analysis completed for {brand_name}")
        except Exception as e:
            error_msg = f"Visual consistency analysis failed: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)

        # Calculate overall visual score
        results['visual_scores']['overall_visual_score'] = self.calculate_overall_visual_score(results['visual_scores'])

        return results
    
    async def capture_website_screenshots(self, website_url: str, brand_name: str) -> Dict[str, Any]:
        """
        Enhanced screenshot capture with responsive design and element targeting
        Returns comprehensive screenshot data with metadata
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {"error": "Playwright not available", "screenshots": {}}

        # Initialize result structure
        result = {
            "screenshots": {},
            "metadata": {},
            "responsive_captures": {},
            "element_captures": {},
            "capture_timestamp": datetime.utcnow().isoformat(),
            "errors": []
        }

        # Setup directory structure
        brand_folder = self._setup_screenshot_directories(brand_name)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            try:
                # Capture desktop version with fallback
                desktop_results = await self._capture_with_fallback(
                    browser, website_url, brand_name, brand_folder, "desktop"
                )
                result["responsive_captures"]["desktop"] = desktop_results

                # Capture mobile version with fallback
                mobile_results = await self._capture_with_fallback(
                    browser, website_url, brand_name, brand_folder, "mobile"
                )
                result["responsive_captures"]["mobile"] = mobile_results

                # Capture specific elements (using desktop viewport) with fallback
                element_results = await self._capture_elements_with_fallback(
                    browser, website_url, brand_name, brand_folder
                )
                result["element_captures"] = element_results

                # Merge all screenshots for backward compatibility
                all_screenshots = {}
                all_screenshots.update(desktop_results.get("screenshots", {}))
                all_screenshots.update(mobile_results.get("screenshots", {}))
                all_screenshots.update(element_results.get("screenshots", {}))
                result["screenshots"] = all_screenshots

                # Generate metadata
                result["metadata"] = self._generate_screenshot_metadata(result)

                # Log success summary
                total_screenshots = len(all_screenshots)
                self.logger.info(f"Screenshot capture completed for {brand_name}: {total_screenshots} total screenshots")

            except Exception as e:
                error_msg = f"Screenshot capture failed for {brand_name}: {str(e)}"
                self.logger.error(error_msg)
                result["errors"].append(error_msg)
            finally:
                await browser.close()

        return result

    def _setup_screenshot_directories(self, brand_name: str) -> str:
        """Setup organized directory structure for screenshots"""
        brand_slug = brand_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
        brand_folder = os.path.join(self.assets_dir, 'screenshots', brand_slug)

        # Create subdirectories for organization
        subdirs = ['desktop', 'mobile', 'elements', 'pages']
        for subdir in subdirs:
            os.makedirs(os.path.join(brand_folder, subdir), exist_ok=True)

        return brand_folder

    async def _capture_responsive_screenshots(self, browser, website_url: str, brand_name: str,
                                            brand_folder: str, device_type: str) -> Dict[str, Any]:
        """Capture screenshots for specific device type (desktop/mobile)"""
        result = {
            "screenshots": {},
            "metadata": {},
            "errors": []
        }

        # Device configurations
        device_configs = {
            "desktop": {"width": 1920, "height": 1080, "is_mobile": False},
            "mobile": {"width": 375, "height": 812, "is_mobile": True}  # iPhone X dimensions
        }

        config = device_configs.get(device_type, device_configs["desktop"])
        page = await browser.new_page()

        try:
            # Configure viewport
            await page.set_viewport_size({"width": config["width"], "height": config["height"]})
            if config["is_mobile"]:
                await page.emulate_media(media="screen")
                # Add mobile user agent
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
                })

            # Capture homepage
            await page.goto(website_url, wait_until='networkidle', timeout=10000)

            # Wait for page to fully load
            await page.wait_for_timeout(2000)

            # Homepage screenshot
            homepage_filename = f'homepage_{device_type}.png'
            homepage_path = os.path.join(brand_folder, device_type, homepage_filename)
            await page.screenshot(path=homepage_path, full_page=True)

            brand_slug = brand_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
            result["screenshots"][f"homepage_{device_type}"] = f"/static/brand_assets/screenshots/{brand_slug}/{device_type}/{homepage_filename}"

            # Capture additional pages
            common_pages = ['/about', '/products', '/services', '/contact', '/pricing', '/blog']
            for page_path in common_pages:
                try:
                    full_url = website_url.rstrip('/') + page_path
                    await page.goto(full_url, wait_until='networkidle', timeout=8000)
                    await page.wait_for_timeout(1500)

                    page_name = page_path.strip('/')
                    filename = f'{page_name}_{device_type}.png'
                    screenshot_path = os.path.join(brand_folder, device_type, filename)
                    await page.screenshot(path=screenshot_path, full_page=True)

                    result["screenshots"][f"{page_name}_{device_type}"] = f"/static/brand_assets/screenshots/{brand_slug}/{device_type}/{filename}"

                except Exception as e:
                    error_msg = f"Could not capture {page_path} for {brand_name} ({device_type}): {str(e)}"
                    self.logger.warning(error_msg)
                    result["errors"].append(error_msg)
                    continue

            # Store metadata
            result["metadata"] = {
                "device_type": device_type,
                "viewport": config,
                "pages_captured": len(result["screenshots"]),
                "capture_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = f"Failed to capture {device_type} screenshots for {brand_name}: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        finally:
            await page.close()

        return result

    async def _capture_page_elements(self, browser, website_url: str, brand_name: str,
                                   brand_folder: str) -> Dict[str, Any]:
        """Capture specific page elements like logos, headers, hero sections"""
        result = {
            "screenshots": {},
            "metadata": {},
            "elements_found": {},
            "errors": []
        }

        page = await browser.new_page()
        brand_slug = brand_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')

        try:
            # Use desktop viewport for element capture
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(website_url, wait_until='networkidle', timeout=10000)
            await page.wait_for_timeout(2000)

            # Define element selectors to look for
            element_selectors = {
                "logo": [
                    "img[alt*='logo' i]",
                    "img[src*='logo' i]",
                    "img[class*='logo' i]",
                    ".logo img",
                    "#logo img",
                    "header img:first-of-type",
                    "nav img:first-of-type",
                    ".navbar-brand img",
                    ".header-logo img"
                ],
                "header": [
                    "header",
                    ".header",
                    "#header",
                    ".site-header",
                    ".main-header",
                    "nav",
                    ".navbar",
                    ".navigation"
                ],
                "hero": [
                    ".hero",
                    ".hero-section",
                    ".banner",
                    ".jumbotron",
                    ".hero-banner",
                    ".main-banner",
                    ".landing-hero",
                    "section:first-of-type",
                    ".above-fold"
                ],
                "navigation": [
                    "nav",
                    ".nav",
                    ".navigation",
                    ".navbar",
                    ".menu",
                    ".main-nav",
                    "header nav",
                    ".primary-nav"
                ],
                "footer": [
                    "footer",
                    ".footer",
                    "#footer",
                    ".site-footer",
                    ".main-footer"
                ]
            }

            # Capture each element type
            for element_type, selectors in element_selectors.items():
                element_found = False

                for selector in selectors:
                    try:
                        # Check if element exists
                        element = await page.query_selector(selector)
                        if element:
                            # Get element bounding box
                            bounding_box = await element.bounding_box()
                            if bounding_box and bounding_box['width'] > 0 and bounding_box['height'] > 0:
                                # Capture element screenshot
                                filename = f'{element_type}_element.png'
                                element_path = os.path.join(brand_folder, 'elements', filename)
                                await element.screenshot(path=element_path)

                                result["screenshots"][f"{element_type}_element"] = f"/static/brand_assets/screenshots/{brand_slug}/elements/{filename}"
                                result["elements_found"][element_type] = {
                                    "selector": selector,
                                    "dimensions": bounding_box,
                                    "captured": True
                                }
                                element_found = True
                                break

                    except Exception as e:
                        continue

                if not element_found:
                    result["elements_found"][element_type] = {
                        "selector": "none",
                        "captured": False,
                        "reason": "Element not found with any selector"
                    }

            # Try to capture full viewport screenshot for reference
            viewport_filename = 'viewport_reference.png'
            viewport_path = os.path.join(brand_folder, 'elements', viewport_filename)
            await page.screenshot(path=viewport_path)
            result["screenshots"]["viewport_reference"] = f"/static/brand_assets/screenshots/{brand_slug}/elements/{viewport_filename}"

            result["metadata"] = {
                "elements_attempted": len(element_selectors),
                "elements_captured": len([e for e in result["elements_found"].values() if e.get("captured")]),
                "capture_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = f"Failed to capture page elements for {brand_name}: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        finally:
            await page.close()

        return result

    def _generate_screenshot_metadata(self, capture_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive metadata for screenshot capture session"""
        desktop_data = capture_result.get("responsive_captures", {}).get("desktop", {})
        mobile_data = capture_result.get("responsive_captures", {}).get("mobile", {})
        element_data = capture_result.get("element_captures", {})

        total_screenshots = len(capture_result.get("screenshots", {}))
        desktop_screenshots = len(desktop_data.get("screenshots", {}))
        mobile_screenshots = len(mobile_data.get("screenshots", {}))
        element_screenshots = len(element_data.get("screenshots", {}))

        elements_found = element_data.get("elements_found", {})
        elements_captured = len([e for e in elements_found.values() if e.get("captured")])

        return {
            "capture_summary": {
                "total_screenshots": total_screenshots,
                "desktop_screenshots": desktop_screenshots,
                "mobile_screenshots": mobile_screenshots,
                "element_screenshots": element_screenshots,
                "elements_captured": elements_captured,
                "elements_attempted": len(elements_found)
            },
            "responsive_analysis": {
                "desktop_pages": list(desktop_data.get("screenshots", {}).keys()),
                "mobile_pages": list(mobile_data.get("screenshots", {}).keys()),
                "responsive_comparison_available": desktop_screenshots > 0 and mobile_screenshots > 0
            },
            "element_analysis": {
                "elements_found": elements_found,
                "logo_captured": any(k.startswith("logo") for k in capture_result.get("screenshots", {})),
                "header_captured": any(k.startswith("header") for k in capture_result.get("screenshots", {})),
                "hero_captured": any(k.startswith("hero") for k in capture_result.get("screenshots", {}))
            },
            "capture_quality": {
                "success_rate": (total_screenshots / max(1, desktop_screenshots + mobile_screenshots + len(elements_found))) * 100,
                "desktop_success": desktop_screenshots > 0,
                "mobile_success": mobile_screenshots > 0,
                "element_success": elements_captured > 0
            },
            "errors": {
                "desktop_errors": desktop_data.get("errors", []),
                "mobile_errors": mobile_data.get("errors", []),
                "element_errors": element_data.get("errors", [])
            }
        }

    async def _capture_with_fallback(self, browser, website_url: str, brand_name: str,
                                   brand_folder: str, device_type: str) -> Dict[str, Any]:
        """Capture screenshots with multiple fallback strategies"""
        # Try primary capture method
        try:
            return await self._capture_responsive_screenshots(
                browser, website_url, brand_name, brand_folder, device_type
            )
        except Exception as primary_error:
            self.logger.warning(f"Primary {device_type} capture failed for {brand_name}: {primary_error}")

            # Fallback 1: Try with reduced timeout and simpler approach
            try:
                return await self._capture_responsive_screenshots_simple(
                    browser, website_url, brand_name, brand_folder, device_type
                )
            except Exception as fallback_error:
                self.logger.warning(f"Fallback {device_type} capture failed for {brand_name}: {fallback_error}")

                # Return minimal error result
                return {
                    "screenshots": {},
                    "metadata": {
                        "device_type": device_type,
                        "capture_failed": True,
                        "primary_error": str(primary_error),
                        "fallback_error": str(fallback_error)
                    },
                    "errors": [str(primary_error), str(fallback_error)]
                }

    async def _capture_responsive_screenshots_simple(self, browser, website_url: str, brand_name: str,
                                                   brand_folder: str, device_type: str) -> Dict[str, Any]:
        """Simplified screenshot capture with reduced features for fallback"""
        result = {
            "screenshots": {},
            "metadata": {},
            "errors": []
        }

        device_configs = {
            "desktop": {"width": 1280, "height": 720, "is_mobile": False},  # Smaller viewport
            "mobile": {"width": 375, "height": 667, "is_mobile": True}     # iPhone 8 dimensions
        }

        config = device_configs.get(device_type, device_configs["desktop"])
        page = await browser.new_page()

        try:
            # Configure viewport
            await page.set_viewport_size({"width": config["width"], "height": config["height"]})

            # Capture only homepage with reduced timeout
            await page.goto(website_url, wait_until='domcontentloaded', timeout=5000)
            await page.wait_for_timeout(1000)  # Reduced wait time

            # Homepage screenshot only
            homepage_filename = f'homepage_{device_type}_simple.png'
            homepage_path = os.path.join(brand_folder, device_type, homepage_filename)
            await page.screenshot(path=homepage_path, full_page=False)  # Viewport only

            brand_slug = brand_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
            result["screenshots"][f"homepage_{device_type}"] = f"/static/brand_assets/screenshots/{brand_slug}/{device_type}/{homepage_filename}"

            result["metadata"] = {
                "device_type": device_type,
                "viewport": config,
                "pages_captured": 1,
                "capture_method": "simple_fallback",
                "capture_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = f"Simple {device_type} capture failed for {brand_name}: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        finally:
            await page.close()

        return result

    async def _capture_elements_with_fallback(self, browser, website_url: str, brand_name: str,
                                            brand_folder: str) -> Dict[str, Any]:
        """Capture page elements with fallback strategies"""
        # Try primary element capture
        try:
            return await self._capture_page_elements(browser, website_url, brand_name, brand_folder)
        except Exception as primary_error:
            self.logger.warning(f"Primary element capture failed for {brand_name}: {primary_error}")

            # Fallback: Try simplified element capture
            try:
                return await self._capture_page_elements_simple(browser, website_url, brand_name, brand_folder)
            except Exception as fallback_error:
                self.logger.warning(f"Fallback element capture failed for {brand_name}: {fallback_error}")

                # Return minimal error result
                return {
                    "screenshots": {},
                    "metadata": {
                        "elements_attempted": 0,
                        "elements_captured": 0,
                        "capture_failed": True,
                        "primary_error": str(primary_error),
                        "fallback_error": str(fallback_error)
                    },
                    "elements_found": {},
                    "errors": [str(primary_error), str(fallback_error)]
                }

    async def _capture_page_elements_simple(self, browser, website_url: str, brand_name: str,
                                          brand_folder: str) -> Dict[str, Any]:
        """Simplified element capture for fallback"""
        result = {
            "screenshots": {},
            "metadata": {},
            "elements_found": {},
            "errors": []
        }

        page = await browser.new_page()
        brand_slug = brand_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')

        try:
            await page.set_viewport_size({"width": 1280, "height": 720})
            await page.goto(website_url, wait_until='domcontentloaded', timeout=5000)
            await page.wait_for_timeout(1000)

            # Try to capture just the most common elements with simple selectors
            simple_selectors = {
                "logo": ["img[alt*='logo' i]", ".logo img", "header img:first-of-type"],
                "header": ["header", ".header", "nav"]
            }

            for element_type, selectors in simple_selectors.items():
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            bounding_box = await element.bounding_box()
                            if bounding_box and bounding_box['width'] > 10 and bounding_box['height'] > 10:
                                filename = f'{element_type}_element_simple.png'
                                element_path = os.path.join(brand_folder, 'elements', filename)
                                await element.screenshot(path=element_path)

                                result["screenshots"][f"{element_type}_element"] = f"/static/brand_assets/screenshots/{brand_slug}/elements/{filename}"
                                result["elements_found"][element_type] = {
                                    "selector": selector,
                                    "captured": True,
                                    "method": "simple_fallback"
                                }
                                break
                    except Exception:
                        continue

                if element_type not in result["elements_found"]:
                    result["elements_found"][element_type] = {
                        "captured": False,
                        "method": "simple_fallback"
                    }

            result["metadata"] = {
                "elements_attempted": len(simple_selectors),
                "elements_captured": len([e for e in result["elements_found"].values() if e.get("captured")]),
                "capture_method": "simple_fallback",
                "capture_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            error_msg = f"Simple element capture failed for {brand_name}: {str(e)}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        finally:
            await page.close()

        return result
    
    async def extract_brand_colors(self, screenshots: Dict[str, str]) -> Dict[str, Any]:
        """
        Enhanced color palette extraction from screenshots
        Analyzes multiple screenshots to extract comprehensive brand color data
        """
        if not VISUAL_PROCESSING_AVAILABLE or not screenshots:
            return {
                'error': 'Visual processing not available or no screenshots provided',
                'primary_colors': [],
                'secondary_colors': [],
                'accent_colors': []
            }

        colors_data = {
            'primary_colors': [],
            'secondary_colors': [],
            'accent_colors': [],
            'color_analysis': {},
            'color_consistency': {},
            'color_swatches': [],
            'extraction_method': 'enhanced_colorthief',
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'screenshots_analyzed': [],
            'errors': []
        }

        all_colors = []  # Store all extracted colors for consistency analysis
        screenshot_colors = {}  # Store colors per screenshot for comparison

        # Process multiple screenshots for comprehensive analysis
        priority_screenshots = ['homepage_desktop', 'homepage', 'logo_element', 'header_element', 'hero_element']

        # Add all available screenshots to analysis queue
        screenshots_to_analyze = []
        for priority_name in priority_screenshots:
            if priority_name in screenshots:
                screenshot_path = screenshots[priority_name]
                # Handle both string paths and dict objects
                if isinstance(screenshot_path, str):
                    screenshots_to_analyze.append((priority_name, screenshot_path))
                elif isinstance(screenshot_path, dict) and 'path' in screenshot_path:
                    screenshots_to_analyze.append((priority_name, screenshot_path['path']))

        # Add remaining screenshots
        for name, path_data in screenshots.items():
            if name not in [s[0] for s in screenshots_to_analyze]:
                # Handle both string paths and dict objects
                if isinstance(path_data, str):
                    screenshots_to_analyze.append((name, path_data))
                elif isinstance(path_data, dict) and 'path' in path_data:
                    screenshots_to_analyze.append((name, path_data['path']))

        # Limit to first 5 screenshots to avoid excessive processing
        screenshots_to_analyze = screenshots_to_analyze[:5]

        for screenshot_name, screenshot_path in screenshots_to_analyze:
            try:
                # Handle string paths
                if isinstance(screenshot_path, str):
                    # Convert relative path to absolute
                    abs_path = screenshot_path.replace('/static/', 'src/static/')
                    if not os.path.exists(abs_path):
                        # Try alternative path resolution
                        abs_path = os.path.join(os.getcwd(), screenshot_path.lstrip('/'))

                    if os.path.exists(abs_path):
                        colors_data['screenshots_analyzed'].append(screenshot_name)
                        screenshot_colors[screenshot_name] = await self._extract_colors_from_image(abs_path, screenshot_name)
                        all_colors.extend(screenshot_colors[screenshot_name]['raw_colors'])

                    else:
                        colors_data['errors'].append(f"Screenshot not found: {abs_path}")
                else:
                    # Skip non-string paths (dict objects, etc.)
                    colors_data['errors'].append(f"Invalid screenshot path format for {screenshot_name}: {type(screenshot_path)}")

            except Exception as e:
                error_msg = f"Color extraction failed for {screenshot_name}: {str(e)}"
                self.logger.error(error_msg)
                colors_data['errors'].append(error_msg)

        if not all_colors:
            colors_data['error'] = 'No colors could be extracted from any screenshot'
            return colors_data

        # Analyze and categorize colors
        colors_data.update(await self._analyze_and_categorize_colors(all_colors, screenshot_colors))

        # Generate color swatches for frontend visualization
        colors_data['color_swatches'] = self._generate_color_swatches(colors_data)

        # Calculate color consistency scores
        colors_data['color_consistency'] = self._calculate_color_consistency_advanced(screenshot_colors)

        return colors_data

    async def _extract_colors_from_image(self, image_path: str, image_name: str) -> Dict[str, Any]:
        """Extract detailed color information from a single image"""
        try:
            color_thief = ColorThief(image_path)

            # Get dominant color
            dominant_color = color_thief.get_color(quality=1)

            # Get comprehensive palette (up to 10 colors)
            palette = color_thief.get_palette(color_count=10, quality=1)

            # Process colors with detailed information
            processed_colors = []
            for i, color in enumerate(palette):
                color_info = {
                    'rgb': color,
                    'hex': self.rgb_to_hex(color),
                    'name': self.get_color_name(color),
                    'hsl': self.rgb_to_hsl(color),
                    'brightness': self.calculate_brightness(color),
                    'is_dominant': i == 0,
                    'weight': max(0.1, 1.0 - (i * 0.1))  # Decreasing weight for less dominant colors
                }
                processed_colors.append(color_info)

            return {
                'image_name': image_name,
                'dominant_color': processed_colors[0] if processed_colors else None,
                'raw_colors': processed_colors,
                'color_count': len(processed_colors),
                'extraction_success': True
            }

        except Exception as e:
            self.logger.error(f"Failed to extract colors from {image_path}: {e}")
            return {
                'image_name': image_name,
                'dominant_color': None,
                'raw_colors': [],
                'color_count': 0,
                'extraction_success': False,
                'error': str(e)
            }

    async def _analyze_and_categorize_colors(self, all_colors: List[Dict[str, Any]],
                                           screenshot_colors: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and categorize colors into primary, secondary, and accent colors"""

        # Merge similar colors and calculate frequency
        color_frequency = {}
        for color in all_colors:
            hex_color = color['hex']
            if hex_color in color_frequency:
                color_frequency[hex_color]['frequency'] += color['weight']
                color_frequency[hex_color]['sources'].append(color.get('source', 'unknown'))
            else:
                color_frequency[hex_color] = {
                    'color_info': color,
                    'frequency': color['weight'],
                    'sources': [color.get('source', 'unknown')]
                }

        # Sort colors by frequency
        sorted_colors = sorted(color_frequency.items(), key=lambda x: x[1]['frequency'], reverse=True)

        # Categorize colors
        primary_colors = []
        secondary_colors = []
        accent_colors = []

        for i, (hex_color, data) in enumerate(sorted_colors):
            color_info = data['color_info'].copy()
            color_info['frequency_score'] = data['frequency']
            color_info['appears_in'] = list(set(data['sources']))
            color_info['consistency_score'] = len(color_info['appears_in']) * 20  # Higher if appears in multiple screenshots

            if i < 3:  # Top 3 most frequent colors as primary
                primary_colors.append(color_info)
            elif i < 8:  # Next 5 as secondary
                secondary_colors.append(color_info)
            else:  # Remaining as accent colors
                accent_colors.append(color_info)

        # Color analysis insights
        color_analysis = {
            'total_unique_colors': len(sorted_colors),
            'color_diversity_score': min(100, len(sorted_colors) * 5),
            'dominant_color_strength': sorted_colors[0][1]['frequency'] if sorted_colors else 0,
            'color_distribution': self._analyze_color_distribution(sorted_colors),
            'color_temperature': self._analyze_color_temperature(primary_colors + secondary_colors),
            'color_harmony_type': self._determine_color_harmony([c['color_info'] for _, c in sorted_colors[:5]])
        }

        return {
            'primary_colors': primary_colors,
            'secondary_colors': secondary_colors,
            'accent_colors': accent_colors,
            'color_analysis': color_analysis
        }

    def _generate_color_swatches(self, colors_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate color swatches for frontend visualization"""
        swatches = []

        # Add primary colors
        for i, color in enumerate(colors_data.get('primary_colors', [])):
            swatches.append({
                'id': f"primary_{i}",
                'category': 'primary',
                'hex': color['hex'],
                'rgb': color['rgb'],
                'hsl': color.get('hsl', [0, 0, 0]),
                'name': color['name'],
                'brightness': color.get('brightness', 0),
                'frequency_score': color.get('frequency_score', 0),
                'consistency_score': color.get('consistency_score', 0),
                'appears_in': color.get('appears_in', []),
                'is_dominant': color.get('is_dominant', False)
            })

        # Add secondary colors
        for i, color in enumerate(colors_data.get('secondary_colors', [])):
            swatches.append({
                'id': f"secondary_{i}",
                'category': 'secondary',
                'hex': color['hex'],
                'rgb': color['rgb'],
                'hsl': color.get('hsl', [0, 0, 0]),
                'name': color['name'],
                'brightness': color.get('brightness', 0),
                'frequency_score': color.get('frequency_score', 0),
                'consistency_score': color.get('consistency_score', 0),
                'appears_in': color.get('appears_in', [])
            })

        # Add top accent colors (limit to 3)
        for i, color in enumerate(colors_data.get('accent_colors', [])[:3]):
            swatches.append({
                'id': f"accent_{i}",
                'category': 'accent',
                'hex': color['hex'],
                'rgb': color['rgb'],
                'hsl': color.get('hsl', [0, 0, 0]),
                'name': color['name'],
                'brightness': color.get('brightness', 0),
                'frequency_score': color.get('frequency_score', 0),
                'consistency_score': color.get('consistency_score', 0),
                'appears_in': color.get('appears_in', [])
            })

        return swatches

    def _calculate_color_consistency_advanced(self, screenshot_colors: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate advanced color consistency metrics across screenshots"""
        if not screenshot_colors:
            return {'overall_score': 0, 'details': 'No screenshots analyzed'}

        # Collect all colors from all screenshots
        all_screenshot_colors = []
        for screenshot_name, data in screenshot_colors.items():
            if data.get('extraction_success') and data.get('raw_colors'):
                all_screenshot_colors.extend([
                    {'color': color, 'screenshot': screenshot_name}
                    for color in data['raw_colors'][:5]  # Top 5 colors per screenshot
                ])

        if not all_screenshot_colors:
            return {'overall_score': 0, 'details': 'No colors extracted successfully'}

        # Calculate consistency metrics
        unique_colors = set(color['color']['hex'] for color in all_screenshot_colors)
        total_color_instances = len(all_screenshot_colors)

        # Colors that appear in multiple screenshots
        color_appearances = {}
        for item in all_screenshot_colors:
            hex_color = item['color']['hex']
            if hex_color not in color_appearances:
                color_appearances[hex_color] = set()
            color_appearances[hex_color].add(item['screenshot'])

        consistent_colors = [color for color, screenshots in color_appearances.items()
                           if len(screenshots) > 1]

        # Calculate scores
        color_diversity_score = max(0, 100 - (len(unique_colors) * 5))  # Lower diversity = higher consistency
        cross_screenshot_consistency = (len(consistent_colors) / len(unique_colors)) * 100 if unique_colors else 0

        overall_score = int((color_diversity_score * 0.4) + (cross_screenshot_consistency * 0.6))

        return {
            'overall_score': overall_score,
            'unique_colors_count': len(unique_colors),
            'consistent_colors_count': len(consistent_colors),
            'color_diversity_score': color_diversity_score,
            'cross_screenshot_consistency': cross_screenshot_consistency,
            'screenshots_analyzed': len(screenshot_colors),
            'total_color_instances': total_color_instances,
            'consistency_details': {
                'highly_consistent': overall_score >= 80,
                'moderately_consistent': 60 <= overall_score < 80,
                'low_consistency': overall_score < 60
            }
        }

    def rgb_to_hex(self, rgb_tuple: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return "#{:02x}{:02x}{:02x}".format(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

    def rgb_to_hsl(self, rgb_tuple: Tuple[int, int, int]) -> List[int]:
        """Convert RGB to HSL"""
        r, g, b = [x / 255.0 for x in rgb_tuple]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Lightness
        l = (max_val + min_val) / 2

        if diff == 0:
            h = s = 0  # achromatic
        else:
            # Saturation
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)

            # Hue
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6

        return [int(h * 360), int(s * 100), int(l * 100)]

    def calculate_brightness(self, rgb_tuple: Tuple[int, int, int]) -> int:
        """Calculate perceived brightness of a color (0-100)"""
        r, g, b = rgb_tuple
        # Using relative luminance formula
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255 * 100
        return int(brightness)

    def get_color_name(self, rgb_tuple: Tuple[int, int, int]) -> str:
        """Get human-readable color name with fallback"""
        try:
            if VISUAL_PROCESSING_AVAILABLE:
                # Try exact match first
                try:
                    import webcolors
                    return webcolors.rgb_to_name(rgb_tuple)
                except ValueError:
                    # Find closest color name
                    min_colors = {}
                    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
                        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
                        rd = (r_c - rgb_tuple[0]) ** 2
                        gd = (g_c - rgb_tuple[1]) ** 2
                        bd = (b_c - rgb_tuple[2]) ** 2
                        min_colors[(rd + gd + bd)] = name
                    return min_colors[min(min_colors.keys())]
        except Exception:
            pass

        # Fallback to basic color description
        r, g, b = rgb_tuple
        if r > 200 and g > 200 and b > 200:
            return "Light Gray"
        elif r < 50 and g < 50 and b < 50:
            return "Dark Gray"
        elif r > g and r > b:
            return "Red-ish"
        elif g > r and g > b:
            return "Green-ish"
        elif b > r and b > g:
            return "Blue-ish"
        else:
            return f"RGB({r}, {g}, {b})"

    def _analyze_color_distribution(self, sorted_colors: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze the distribution of colors in the palette"""
        if not sorted_colors:
            return {'distribution_type': 'none', 'balance_score': 0}

        frequencies = [data['frequency'] for _, data in sorted_colors]
        total_frequency = sum(frequencies)

        if not total_frequency:
            return {'distribution_type': 'none', 'balance_score': 0}

        # Calculate distribution metrics
        dominant_ratio = frequencies[0] / total_frequency if frequencies else 0

        if dominant_ratio > 0.7:
            distribution_type = 'dominant'
            balance_score = 30  # Low balance, one color dominates
        elif dominant_ratio > 0.4:
            distribution_type = 'primary_focused'
            balance_score = 60  # Moderate balance
        else:
            distribution_type = 'balanced'
            balance_score = 90  # High balance

        return {
            'distribution_type': distribution_type,
            'balance_score': balance_score,
            'dominant_color_ratio': dominant_ratio,
            'color_count': len(sorted_colors)
        }

    def _analyze_color_temperature(self, colors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall color temperature of the palette"""
        if not colors:
            return {'temperature': 'neutral', 'warmth_score': 50}

        warm_count = 0
        cool_count = 0
        neutral_count = 0

        for color in colors:
            r, g, b = color['rgb']

            # Simple temperature analysis based on RGB values
            if r > g and r > b:  # Red dominant
                warm_count += 1
            elif b > r and b > g:  # Blue dominant
                cool_count += 1
            elif g > r and g > b:  # Green can be either
                if r > b:  # Yellow-green (warm)
                    warm_count += 1
                else:  # Blue-green (cool)
                    cool_count += 1
            else:
                neutral_count += 1

        total_colors = len(colors)
        warm_ratio = warm_count / total_colors
        cool_ratio = cool_count / total_colors

        if warm_ratio > cool_ratio + 0.2:
            temperature = 'warm'
            warmth_score = 70 + int(warm_ratio * 30)
        elif cool_ratio > warm_ratio + 0.2:
            temperature = 'cool'
            warmth_score = 30 - int(cool_ratio * 30)
        else:
            temperature = 'neutral'
            warmth_score = 50

        return {
            'temperature': temperature,
            'warmth_score': max(0, min(100, warmth_score)),
            'warm_colors': warm_count,
            'cool_colors': cool_count,
            'neutral_colors': neutral_count
        }

    def _determine_color_harmony(self, colors: List[Dict[str, Any]]) -> str:
        """Determine the type of color harmony in the palette"""
        if len(colors) < 2:
            return 'monochromatic'

        # Extract hue values from HSL
        hues = []
        for color in colors[:5]:  # Analyze top 5 colors
            hsl = color.get('hsl', [0, 0, 0])
            hues.append(hsl[0])

        if not hues:
            return 'unknown'

        # Analyze hue relationships
        hue_differences = []
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                diff = abs(hues[i] - hues[j])
                # Handle circular nature of hue (0-360)
                diff = min(diff, 360 - diff)
                hue_differences.append(diff)

        if not hue_differences:
            return 'monochromatic'

        avg_difference = sum(hue_differences) / len(hue_differences)

        # Classify harmony type based on average hue differences
        if avg_difference < 30:
            return 'monochromatic'
        elif avg_difference < 60:
            return 'analogous'
        elif 150 < avg_difference < 210:
            return 'complementary'
        elif 90 < avg_difference < 150:
            return 'triadic'
        else:
            return 'complex'

    def analyze_color_harmony(self, palette: List[Tuple[int, int, int]]) -> str:
        """Legacy method for backward compatibility"""
        if len(palette) < 2:
            return "insufficient_colors"

        # Convert to new format and use enhanced analysis
        colors = [{'rgb': color, 'hsl': self.rgb_to_hsl(color)} for color in palette]
        return self._determine_color_harmony(colors)

    async def detect_brand_logos(self, screenshots: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Advanced logo detection using computer vision techniques
        Combines multiple approaches for accurate brand asset extraction
        """
        if not OPENCV_AVAILABLE or not screenshots:
            return []

        logos = []
        self.logger.info(f"Starting logo detection on {len(screenshots)} screenshots")

        # Extract actual screenshot paths from the nested structure
        screenshot_paths = self._extract_screenshot_paths(screenshots)

        for screenshot_name, screenshot_path in screenshot_paths.items():
            try:
                # Convert relative path to absolute path
                if isinstance(screenshot_path, str) and screenshot_path.startswith('/static/'):
                    # Remove /static/ prefix and construct full path
                    relative_path = screenshot_path[8:]  # Remove '/static/'
                    full_path = os.path.join(os.getcwd(), 'src', 'static', relative_path)
                else:
                    full_path = screenshot_path

                if not os.path.exists(full_path):
                    self.logger.warning(f"Screenshot not found: {full_path}")
                    continue

                # Load image with OpenCV
                image = cv2.imread(full_path)
                if image is None:
                    self.logger.warning(f"Could not load image: {full_path}")
                    continue

                # Detect logos using multiple methods
                detected_logos = await self._detect_logos_in_image(image, screenshot_name, full_path)
                logos.extend(detected_logos)

            except Exception as e:
                self.logger.error(f"Logo detection failed for {screenshot_name}: {e}")
                continue

        # Post-process and deduplicate logos
        processed_logos = await self._process_detected_logos(logos)

        self.logger.info(f"Logo detection completed: found {len(processed_logos)} potential logos")
        return processed_logos

    def _extract_screenshot_paths(self, screenshots: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract actual screenshot file paths from the nested screenshot structure
        """
        paths = {}

        try:
            # Handle different screenshot data structures
            if isinstance(screenshots, dict):
                # Check if this is the nested structure from capture_website_screenshots
                if 'screenshots' in screenshots and isinstance(screenshots['screenshots'], dict):
                    # Extract from the nested screenshots dict
                    for name, path in screenshots['screenshots'].items():
                        if isinstance(path, str):
                            paths[name] = path

                # Also check responsive_captures
                if 'responsive_captures' in screenshots:
                    responsive = screenshots['responsive_captures']
                    for device_type, device_data in responsive.items():
                        if isinstance(device_data, dict) and 'screenshots' in device_data:
                            for name, path in device_data['screenshots'].items():
                                if isinstance(path, str):
                                    paths[f"{name}_{device_type}"] = path

                # Also check element_captures
                if 'element_captures' in screenshots:
                    element_data = screenshots['element_captures']
                    if isinstance(element_data, dict) and 'screenshots' in element_data:
                        for name, path in element_data['screenshots'].items():
                            if isinstance(path, str):
                                paths[f"element_{name}"] = path

                # Handle direct path mapping (fallback)
                for key, value in screenshots.items():
                    if isinstance(value, str) and (value.startswith('/static/') or value.endswith('.png')):
                        paths[key] = value

        except Exception as e:
            self.logger.error(f"Screenshot path extraction failed: {e}")

        return paths

    async def _detect_logos_in_image(self, image: np.ndarray, screenshot_name: str, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect logos in a single image using multiple computer vision techniques
        """
        logos = []

        try:
            # Method 1: Contour-based detection for distinct shapes
            contour_logos = await self._detect_logos_by_contours(image, screenshot_name, image_path)
            logos.extend(contour_logos)

            # Method 2: Template matching for common logo positions
            template_logos = await self._detect_logos_by_position(image, screenshot_name, image_path)
            logos.extend(template_logos)

            # Method 3: Edge detection for geometric logos
            edge_logos = await self._detect_logos_by_edges(image, screenshot_name, image_path)
            logos.extend(edge_logos)

            # Method 4: Color clustering for distinctive brand colors
            color_logos = await self._detect_logos_by_color_clustering(image, screenshot_name, image_path)
            logos.extend(color_logos)

        except Exception as e:
            self.logger.error(f"Logo detection methods failed for {screenshot_name}: {e}")

        return logos

    async def _detect_logos_by_contours(self, image: np.ndarray, screenshot_name: str, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect logos using contour analysis - good for distinct shapes and symbols
        """
        logos = []

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter contours by size and aspect ratio (typical logo characteristics)
            height, width = image.shape[:2]
            min_area = (width * height) * 0.001  # At least 0.1% of image
            max_area = (width * height) * 0.15   # At most 15% of image

            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)

                if min_area < area < max_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)

                    # Check aspect ratio (logos are usually not extremely elongated)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.3 <= aspect_ratio <= 3.0:

                        # Extract logo region
                        logo_region = image[y:y+h, x:x+w]

                        # Calculate logo quality metrics
                        quality_score = self._calculate_logo_quality_metrics(logo_region, contour)

                        if quality_score > 0.3:  # Minimum quality threshold
                            # Save extracted logo
                            logo_filename = await self._save_extracted_logo(
                                logo_region, screenshot_name, f"contour_{i}", image_path
                            )

                            logos.append({
                                'type': 'contour_detected',
                                'filename': logo_filename,
                                'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                                'area': int(area),
                                'aspect_ratio': round(aspect_ratio, 2),
                                'quality_score': round(quality_score, 2),
                                'detection_method': 'contour_analysis',
                                'source_screenshot': screenshot_name
                            })

        except Exception as e:
            self.logger.error(f"Contour-based logo detection failed: {e}")

        return logos

    async def _detect_logos_by_position(self, image: np.ndarray, screenshot_name: str, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect logos by analyzing common logo positions (header, top-left, etc.)
        """
        logos = []

        try:
            height, width = image.shape[:2]

            # Define common logo regions
            logo_regions = {
                'header_left': {'x': 0, 'y': 0, 'w': width//4, 'h': height//8},
                'header_center': {'x': width//3, 'y': 0, 'w': width//3, 'h': height//8},
                'top_left_corner': {'x': 0, 'y': 0, 'w': width//6, 'h': height//10},
                'navigation_area': {'x': 0, 'y': 0, 'w': width, 'h': height//6}
            }

            for region_name, region in logo_regions.items():
                x, y, w, h = region['x'], region['y'], region['w'], region['h']

                # Extract region
                roi = image[y:y+h, x:x+w]

                # Look for logo-like elements in this region
                potential_logos = await self._analyze_region_for_logos(roi, region_name, screenshot_name)

                for logo in potential_logos:
                    # Adjust coordinates to full image
                    logo['position']['x'] += x
                    logo['position']['y'] += y
                    logo['region'] = region_name
                    logos.append(logo)

        except Exception as e:
            self.logger.error(f"Position-based logo detection failed: {e}")

        return logos

    async def _detect_logos_by_edges(self, image: np.ndarray, screenshot_name: str, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect logos using edge detection - good for geometric and text-based logos
        """
        logos = []

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply different edge detection methods
            # Canny edge detection
            edges_canny = cv2.Canny(gray, 50, 150)

            # Sobel edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges_sobel = np.sqrt(sobelx**2 + sobely**2)
            edges_sobel = np.uint8(edges_sobel / edges_sobel.max() * 255)

            # Combine edge maps
            combined_edges = cv2.bitwise_or(edges_canny, edges_sobel)

            # Find connected components in edge map
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(combined_edges)

            height, width = image.shape[:2]
            min_area = (width * height) * 0.0005  # Minimum area threshold
            max_area = (width * height) * 0.1     # Maximum area threshold

            for i in range(1, num_labels):  # Skip background (label 0)
                area = stats[i, cv2.CC_STAT_AREA]

                if min_area < area < max_area:
                    x = stats[i, cv2.CC_STAT_LEFT]
                    y = stats[i, cv2.CC_STAT_TOP]
                    w = stats[i, cv2.CC_STAT_WIDTH]
                    h = stats[i, cv2.CC_STAT_HEIGHT]

                    # Check if this looks like a logo (aspect ratio, position, etc.)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.2 <= aspect_ratio <= 5.0:  # Reasonable aspect ratio

                        # Extract the region
                        logo_region = image[y:y+h, x:x+w]

                        # Calculate edge density (logos often have clean edges)
                        edge_density = self._calculate_edge_density(logo_region)

                        if edge_density > 0.1:  # Minimum edge density
                            logo_filename = await self._save_extracted_logo(
                                logo_region, screenshot_name, f"edge_{i}", image_path
                            )

                            logos.append({
                                'type': 'edge_detected',
                                'filename': logo_filename,
                                'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                                'area': int(area),
                                'aspect_ratio': round(aspect_ratio, 2),
                                'edge_density': round(edge_density, 3),
                                'detection_method': 'edge_analysis',
                                'source_screenshot': screenshot_name
                            })

        except Exception as e:
            self.logger.error(f"Edge-based logo detection failed: {e}")

        return logos

    async def _detect_logos_by_color_clustering(self, image: np.ndarray, screenshot_name: str, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect logos using color clustering - good for colorful brand logos
        """
        logos = []

        try:
            # Convert to RGB for color analysis
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Reshape image for k-means clustering
            pixel_values = rgb_image.reshape((-1, 3))
            pixel_values = np.float32(pixel_values)

            # Apply k-means clustering to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 8  # Number of color clusters
            _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Convert back to uint8 and reshape
            centers = np.uint8(centers)
            segmented_image = centers[labels.flatten()]
            segmented_image = segmented_image.reshape(rgb_image.shape)

            # Find regions with distinct color patterns (potential logos)
            height, width = image.shape[:2]

            # Create masks for each color cluster
            for i, color in enumerate(centers):
                # Create mask for this color
                lower = np.array([max(0, c-30) for c in color])
                upper = np.array([min(255, c+30) for c in color])
                mask = cv2.inRange(rgb_image, lower, upper)

                # Find contours in this color mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for j, contour in enumerate(contours):
                    area = cv2.contourArea(contour)
                    min_area = (width * height) * 0.001
                    max_area = (width * height) * 0.08

                    if min_area < area < max_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h if h > 0 else 0

                        if 0.3 <= aspect_ratio <= 3.0:
                            # Extract logo region
                            logo_region = image[y:y+h, x:x+w]

                            # Check color uniqueness (logos often have distinctive colors)
                            color_uniqueness = self._calculate_color_uniqueness(logo_region, rgb_image)

                            if color_uniqueness > 0.3:
                                logo_filename = await self._save_extracted_logo(
                                    logo_region, screenshot_name, f"color_{i}_{j}", image_path
                                )

                                logos.append({
                                    'type': 'color_clustered',
                                    'filename': logo_filename,
                                    'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                                    'area': int(area),
                                    'aspect_ratio': round(aspect_ratio, 2),
                                    'dominant_color': color.tolist(),
                                    'color_uniqueness': round(color_uniqueness, 3),
                                    'detection_method': 'color_clustering',
                                    'source_screenshot': screenshot_name
                                })

        except Exception as e:
            self.logger.error(f"Color clustering logo detection failed: {e}")

        return logos

    async def _analyze_region_for_logos(self, roi: np.ndarray, region_name: str, screenshot_name: str) -> List[Dict[str, Any]]:
        """
        Analyze a specific region for logo-like elements
        """
        logos = []

        try:
            if roi.size == 0:
                return logos

            # Convert to grayscale for analysis
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            roi_height, roi_width = roi.shape[:2]
            min_area = (roi_width * roi_height) * 0.01  # At least 1% of region
            max_area = (roi_width * roi_height) * 0.8   # At most 80% of region

            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)

                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0

                    if 0.2 <= aspect_ratio <= 4.0:
                        # Extract potential logo
                        logo_region = roi[y:y+h, x:x+w]

                        # Calculate logo-like characteristics
                        compactness = self._calculate_shape_compactness(contour)

                        if compactness > 0.2:  # Logos tend to be reasonably compact
                            logo_filename = await self._save_extracted_logo(
                                logo_region, screenshot_name, f"{region_name}_{i}", ""
                            )

                            logos.append({
                                'type': 'region_detected',
                                'filename': logo_filename,
                                'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                                'area': int(area),
                                'aspect_ratio': round(aspect_ratio, 2),
                                'compactness': round(compactness, 3),
                                'detection_method': 'region_analysis',
                                'source_screenshot': screenshot_name
                            })

        except Exception as e:
            self.logger.error(f"Region analysis failed for {region_name}: {e}")

        return logos

    def _calculate_logo_quality_metrics(self, logo_region: np.ndarray, contour: np.ndarray) -> float:
        """
        Calculate quality metrics for a potential logo region
        """
        try:
            if logo_region.size == 0:
                return 0.0

            # Calculate various quality metrics
            scores = []

            # 1. Contrast score (logos should have good contrast)
            gray = cv2.cvtColor(logo_region, cv2.COLOR_BGR2GRAY)
            contrast = gray.std()
            contrast_score = min(1.0, contrast / 50.0)  # Normalize to 0-1
            scores.append(contrast_score)

            # 2. Edge density (logos often have clean edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            edge_score = min(1.0, edge_density * 10)  # Normalize to 0-1
            scores.append(edge_score)

            # 3. Shape compactness
            compactness = self._calculate_shape_compactness(contour)
            scores.append(compactness)

            # 4. Size appropriateness (not too small, not too large)
            height, width = logo_region.shape[:2]
            size_score = 1.0 if 20 <= min(width, height) <= 200 else 0.5
            scores.append(size_score)

            # Return weighted average
            return sum(scores) / len(scores)

        except Exception as e:
            self.logger.error(f"Logo quality calculation failed: {e}")
            return 0.0

    def _calculate_shape_compactness(self, contour: np.ndarray) -> float:
        """
        Calculate shape compactness (4π*area/perimeter²)
        Perfect circle = 1.0, more irregular shapes < 1.0
        """
        try:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)

            if perimeter == 0:
                return 0.0

            compactness = (4 * np.pi * area) / (perimeter * perimeter)
            return min(1.0, compactness)

        except Exception:
            return 0.0

    def _calculate_edge_density(self, image_region: np.ndarray) -> float:
        """
        Calculate edge density in an image region
        """
        try:
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_pixels = np.sum(edges > 0)
            total_pixels = edges.size

            return edge_pixels / total_pixels if total_pixels > 0 else 0.0

        except Exception:
            return 0.0

    def _calculate_color_uniqueness(self, logo_region: np.ndarray, full_image: np.ndarray) -> float:
        """
        Calculate how unique the colors in the logo region are compared to the full image
        """
        try:
            # Get dominant colors from logo region
            logo_colors = self._get_dominant_colors(logo_region, k=3)

            # Get dominant colors from full image
            full_colors = self._get_dominant_colors(full_image, k=8)

            # Calculate color distance
            uniqueness_scores = []
            for logo_color in logo_colors:
                min_distance = float('inf')
                for full_color in full_colors:
                    distance = np.linalg.norm(np.array(logo_color) - np.array(full_color))
                    min_distance = min(min_distance, distance)

                # Normalize distance to 0-1 scale
                uniqueness_scores.append(min(1.0, min_distance / 255.0))

            return sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 0.0

        except Exception:
            return 0.0

    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """
        Get dominant colors from an image using k-means clustering
        """
        try:
            # Reshape image for k-means
            pixel_values = image.reshape((-1, 3))
            pixel_values = np.float32(pixel_values)

            # Apply k-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, _, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Convert to int and return as list
            return [center.astype(int).tolist() for center in centers]

        except Exception:
            return []

    async def _save_extracted_logo(self, logo_region: np.ndarray, screenshot_name: str, logo_id: str, source_path: str) -> str:
        """
        Save extracted logo with transparent background and return filename
        """
        try:
            if logo_region.size == 0:
                return ""

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logo_{screenshot_name}_{logo_id}_{timestamp}.png"

            # Ensure logos directory exists
            logos_dir = os.path.join(self.assets_dir, 'logos')
            os.makedirs(logos_dir, exist_ok=True)

            logo_path = os.path.join(logos_dir, filename)

            # Process logo for better quality
            processed_logo = await self._process_logo_for_extraction(logo_region)

            # Save as PNG to preserve transparency
            cv2.imwrite(logo_path, processed_logo)

            # Return relative path for web access
            return f"/static/brand_assets/logos/{filename}"

        except Exception as e:
            self.logger.error(f"Logo saving failed: {e}")
            return ""

    async def _process_logo_for_extraction(self, logo_region: np.ndarray) -> np.ndarray:
        """
        Process logo region to improve quality and create transparent background
        """
        try:
            # Resize if too small (improve visibility)
            height, width = logo_region.shape[:2]
            if min(height, width) < 50:
                scale_factor = 50 / min(height, width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                logo_region = cv2.resize(logo_region, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

            # Apply noise reduction
            denoised = cv2.bilateralFilter(logo_region, 9, 75, 75)

            # Enhance contrast
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

            # Attempt background removal (simple approach)
            processed_with_alpha = await self._remove_background_simple(enhanced)

            return processed_with_alpha

        except Exception as e:
            self.logger.error(f"Logo processing failed: {e}")
            return logo_region

    async def _remove_background_simple(self, image: np.ndarray) -> np.ndarray:
        """
        Simple background removal using color-based segmentation
        """
        try:
            # Convert to RGB
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Create mask for background (assuming corners are background)
            height, width = image.shape[:2]

            # Sample corner colors as potential background
            corner_colors = [
                rgb[0, 0],           # top-left
                rgb[0, width-1],     # top-right
                rgb[height-1, 0],    # bottom-left
                rgb[height-1, width-1]  # bottom-right
            ]

            # Create mask for background colors
            mask = np.zeros((height, width), dtype=np.uint8)

            for corner_color in corner_colors:
                # Create mask for similar colors
                lower = np.array([max(0, c-30) for c in corner_color])
                upper = np.array([min(255, c+30) for c in corner_color])
                color_mask = cv2.inRange(rgb, lower, upper)
                mask = cv2.bitwise_or(mask, color_mask)

            # Invert mask (we want to keep the logo, not the background)
            logo_mask = cv2.bitwise_not(mask)

            # Apply morphological operations to clean up the mask
            kernel = np.ones((3,3), np.uint8)
            logo_mask = cv2.morphologyEx(logo_mask, cv2.MORPH_CLOSE, kernel)
            logo_mask = cv2.morphologyEx(logo_mask, cv2.MORPH_OPEN, kernel)

            # Create 4-channel image (BGRA)
            bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            bgra[:, :, 3] = logo_mask  # Set alpha channel

            return bgra

        except Exception as e:
            self.logger.error(f"Background removal failed: {e}")
            # Return original image with full opacity
            bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            bgra[:, :, 3] = 255
            return bgra

    async def _process_detected_logos(self, logos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post-process detected logos: deduplicate, rank by quality, and enhance metadata
        """
        try:
            if not logos:
                return []

            # Remove duplicates based on position overlap
            unique_logos = []
            for logo in logos:
                is_duplicate = False
                logo_pos = logo['position']

                for existing_logo in unique_logos:
                    existing_pos = existing_logo['position']

                    # Calculate overlap
                    overlap = self._calculate_position_overlap(logo_pos, existing_pos)
                    if overlap > 0.7:  # 70% overlap threshold
                        # Keep the one with higher quality score
                        logo_quality = logo.get('quality_score', 0)
                        existing_quality = existing_logo.get('quality_score', 0)

                        if logo_quality > existing_quality:
                            # Replace existing with current
                            unique_logos.remove(existing_logo)
                            unique_logos.append(logo)

                        is_duplicate = True
                        break

                if not is_duplicate:
                    unique_logos.append(logo)

            # Sort by quality/confidence
            unique_logos.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

            # Add ranking and confidence scores
            for i, logo in enumerate(unique_logos):
                logo['rank'] = i + 1
                logo['confidence'] = self._calculate_logo_confidence(logo)

            # Limit to top 10 logos to avoid clutter
            return unique_logos[:10]

        except Exception as e:
            self.logger.error(f"Logo post-processing failed: {e}")
            return logos

    def _calculate_position_overlap(self, pos1: Dict, pos2: Dict) -> float:
        """
        Calculate overlap ratio between two rectangular positions
        """
        try:
            # Extract coordinates
            x1, y1, w1, h1 = pos1['x'], pos1['y'], pos1['width'], pos1['height']
            x2, y2, w2, h2 = pos2['x'], pos2['y'], pos2['width'], pos2['height']

            # Calculate intersection
            left = max(x1, x2)
            top = max(y1, y2)
            right = min(x1 + w1, x2 + w2)
            bottom = min(y1 + h1, y2 + h2)

            if left < right and top < bottom:
                intersection_area = (right - left) * (bottom - top)
                area1 = w1 * h1
                area2 = w2 * h2
                union_area = area1 + area2 - intersection_area

                return intersection_area / union_area if union_area > 0 else 0

            return 0

        except Exception:
            return 0

    def _calculate_logo_confidence(self, logo: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score for a detected logo
        """
        try:
            confidence_factors = []

            # Quality score factor
            quality_score = logo.get('quality_score', 0)
            confidence_factors.append(quality_score)

            # Detection method reliability
            method_scores = {
                'contour_analysis': 0.8,
                'edge_analysis': 0.7,
                'color_clustering': 0.6,
                'region_analysis': 0.9
            }
            method = logo.get('detection_method', '')
            method_score = method_scores.get(method, 0.5)
            confidence_factors.append(method_score)

            # Size appropriateness
            pos = logo.get('position', {})
            width = pos.get('width', 0)
            height = pos.get('height', 0)
            size_score = 1.0 if 30 <= min(width, height) <= 300 else 0.6
            confidence_factors.append(size_score)

            # Aspect ratio appropriateness
            aspect_ratio = logo.get('aspect_ratio', 0)
            aspect_score = 1.0 if 0.3 <= aspect_ratio <= 3.0 else 0.5
            confidence_factors.append(aspect_score)

            return sum(confidence_factors) / len(confidence_factors)

        except Exception:
            return 0.5

    async def detect_typography_patterns(self, screenshots: Dict[str, str], website_url: str) -> Dict[str, Any]:
        """
        Detect and analyze typography patterns from screenshots and web scraping
        """
        typography_data = {
            'fonts_detected': [],
            'typography_patterns': {},
            'font_consistency': {},
            'text_analysis': {},
            'detection_timestamp': datetime.now().isoformat(),
            'errors': []
        }

        try:
            # Method 1: Web scraping for CSS font information
            if WEB_SCRAPING_AVAILABLE:
                web_fonts = await self._extract_fonts_from_web(website_url)
                typography_data['fonts_detected'].extend(web_fonts)

            # Method 2: OCR-based font detection from screenshots
            if screenshots:
                ocr_fonts = await self._detect_fonts_from_screenshots(screenshots)
                typography_data['fonts_detected'].extend(ocr_fonts)

            # Method 3: Visual pattern analysis
            if screenshots:
                patterns = await self._analyze_typography_patterns(screenshots)
                typography_data['typography_patterns'] = patterns

            # Calculate consistency scores
            typography_data['font_consistency'] = self._calculate_typography_consistency(
                typography_data['fonts_detected']
            )

            # Deduplicate and rank fonts
            typography_data['fonts_detected'] = self._process_detected_fonts(
                typography_data['fonts_detected']
            )

        except Exception as e:
            error_msg = f"Typography detection failed: {str(e)}"
            self.logger.error(error_msg)
            typography_data['errors'].append(error_msg)

        return typography_data

    async def _extract_fonts_from_web(self, website_url: str) -> List[Dict[str, Any]]:
        """
        Extract font information by scraping CSS and analyzing web fonts
        """
        fonts = []

        try:
            # Get page content
            response = requests.get(website_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract inline styles and CSS links
            font_families = set()

            # Check inline styles
            for element in soup.find_all(style=True):
                style = element.get('style', '')
                if 'font-family' in style:
                    # Extract font-family value
                    font_match = re.search(r'font-family\s*:\s*([^;]+)', style)
                    if font_match:
                        font_families.add(font_match.group(1).strip())

            # Check CSS files
            for link in soup.find_all('link', rel='stylesheet'):
                href = link.get('href', '')
                if href:
                    try:
                        # Handle relative URLs
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif href.startswith('/'):
                            href = website_url.rstrip('/') + href
                        elif not href.startswith('http'):
                            href = website_url.rstrip('/') + '/' + href

                        css_response = requests.get(href, timeout=5)
                        css_content = css_response.text

                        # Extract font-family declarations
                        font_matches = re.findall(r'font-family\s*:\s*([^;}]+)', css_content)
                        for match in font_matches:
                            font_families.add(match.strip())

                    except Exception:
                        continue

            # Process found font families
            for font_family in font_families:
                # Clean up font family string
                cleaned_fonts = self._parse_font_family_string(font_family)
                for font_info in cleaned_fonts:
                    fonts.append({
                        'name': font_info['name'],
                        'type': font_info['type'],
                        'source': 'web_scraping',
                        'usage_context': 'css_declaration',
                        'detection_method': 'css_analysis'
                    })

        except Exception as e:
            self.logger.error(f"Web font extraction failed: {e}")

        return fonts

    def _parse_font_family_string(self, font_family_str: str) -> List[Dict[str, str]]:
        """
        Parse CSS font-family string and categorize fonts
        """
        fonts = []

        try:
            # Remove quotes and split by comma
            font_names = [f.strip().strip('"\'') for f in font_family_str.split(',')]

            # Common font categories
            serif_fonts = ['times', 'georgia', 'serif', 'times new roman', 'book antiqua']
            sans_serif_fonts = ['arial', 'helvetica', 'sans-serif', 'verdana', 'calibri', 'tahoma']
            monospace_fonts = ['courier', 'monaco', 'monospace', 'consolas', 'menlo']

            for font_name in font_names:
                font_name_lower = font_name.lower()

                # Determine font type
                font_type = 'custom'
                if any(serif in font_name_lower for serif in serif_fonts):
                    font_type = 'serif'
                elif any(sans in font_name_lower for sans in sans_serif_fonts):
                    font_type = 'sans-serif'
                elif any(mono in font_name_lower for mono in monospace_fonts):
                    font_type = 'monospace'
                elif 'google' in font_name_lower or 'typekit' in font_name_lower:
                    font_type = 'web_font'

                fonts.append({
                    'name': font_name,
                    'type': font_type
                })

        except Exception as e:
            self.logger.error(f"Font family parsing failed: {e}")

        return fonts

    async def _detect_fonts_from_screenshots(self, screenshots: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Detect fonts from screenshots using OCR and text analysis
        Note: This is a simplified approach - advanced OCR libraries like Tesseract could be added
        """
        fonts = []

        try:
            # Extract actual screenshot paths from the nested structure
            screenshot_paths = self._extract_screenshot_paths(screenshots)

            for screenshot_name, screenshot_path in screenshot_paths.items():
                # Convert relative path to absolute path
                if isinstance(screenshot_path, str) and screenshot_path.startswith('/static/'):
                    relative_path = screenshot_path[8:]
                    full_path = os.path.join(os.getcwd(), 'src', 'static', relative_path)
                else:
                    full_path = screenshot_path

                if not os.path.exists(full_path):
                    continue

                # Load image
                image = cv2.imread(full_path)
                if image is None:
                    continue

                # Detect text regions and analyze typography
                text_regions = await self._detect_text_regions(image)

                for region in text_regions:
                    font_characteristics = self._analyze_text_characteristics(region)
                    if font_characteristics:
                        fonts.append({
                            'name': font_characteristics.get('estimated_font', 'Unknown'),
                            'type': font_characteristics.get('font_type', 'unknown'),
                            'size_category': font_characteristics.get('size_category', 'medium'),
                            'weight': font_characteristics.get('weight', 'normal'),
                            'source': 'screenshot_analysis',
                            'detection_method': 'visual_analysis',
                            'source_screenshot': screenshot_name,
                            'characteristics': font_characteristics
                        })

        except Exception as e:
            self.logger.error(f"Screenshot font detection failed: {e}")

        return fonts

    async def _detect_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect text regions in an image using OpenCV
        """
        text_regions = []

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply MSER (Maximally Stable Extremal Regions) for text detection
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)

            # Filter regions that look like text
            for region in regions:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(region)

                # Filter by size and aspect ratio (text characteristics)
                if w > 10 and h > 8 and w < 500 and h < 100:
                    aspect_ratio = w / h
                    if 1.5 <= aspect_ratio <= 15:  # Typical text aspect ratios
                        text_region = {
                            'position': {'x': x, 'y': y, 'width': w, 'height': h},
                            'image_region': image[y:y+h, x:x+w],
                            'aspect_ratio': aspect_ratio
                        }
                        text_regions.append(text_region)

            # Also try contour-based text detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                if w > 15 and h > 10 and w < 400 and h < 80:
                    aspect_ratio = w / h
                    if 2 <= aspect_ratio <= 12:
                        text_region = {
                            'position': {'x': x, 'y': y, 'width': w, 'height': h},
                            'image_region': image[y:y+h, x:x+w],
                            'aspect_ratio': aspect_ratio,
                            'detection_method': 'contour'
                        }
                        text_regions.append(text_region)

        except Exception as e:
            self.logger.error(f"Text region detection failed: {e}")

        return text_regions

    def _analyze_text_characteristics(self, text_region: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze visual characteristics of text to estimate font properties
        """
        try:
            image_region = text_region['image_region']
            if image_region.size == 0:
                return {}

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)

            characteristics = {}

            # Estimate font size based on region height
            height = text_region['position']['height']
            if height < 12:
                characteristics['size_category'] = 'small'
            elif height < 20:
                characteristics['size_category'] = 'medium'
            elif height < 30:
                characteristics['size_category'] = 'large'
            else:
                characteristics['size_category'] = 'extra_large'

            # Estimate font weight based on stroke thickness
            # Calculate average stroke width using morphological operations
            kernel = np.ones((2,2), np.uint8)
            eroded = cv2.erode(gray, kernel, iterations=1)
            stroke_thickness = np.mean(gray - eroded)

            if stroke_thickness > 30:
                characteristics['weight'] = 'bold'
            elif stroke_thickness > 15:
                characteristics['weight'] = 'medium'
            else:
                characteristics['weight'] = 'light'

            # Estimate serif vs sans-serif based on edge characteristics
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size

            if edge_density > 0.15:
                characteristics['font_type'] = 'serif'
                characteristics['estimated_font'] = 'Serif Font'
            else:
                characteristics['font_type'] = 'sans-serif'
                characteristics['estimated_font'] = 'Sans-serif Font'

            # Calculate text quality metrics
            characteristics['edge_density'] = round(edge_density, 3)
            characteristics['stroke_thickness'] = round(stroke_thickness, 2)

            return characteristics

        except Exception as e:
            self.logger.error(f"Text characteristic analysis failed: {e}")
            return {}

    async def _analyze_typography_patterns(self, screenshots: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze typography patterns across screenshots
        """
        patterns = {
            'heading_patterns': [],
            'body_text_patterns': [],
            'consistency_score': 0,
            'pattern_analysis': {}
        }

        try:
            all_text_regions = []

            # Extract actual screenshot paths and collect text regions from all screenshots
            screenshot_paths = self._extract_screenshot_paths(screenshots)

            for screenshot_name, screenshot_path in screenshot_paths.items():
                if isinstance(screenshot_path, str) and screenshot_path.startswith('/static/'):
                    relative_path = screenshot_path[8:]
                    full_path = os.path.join(os.getcwd(), 'src', 'static', relative_path)
                else:
                    full_path = screenshot_path

                if not os.path.exists(full_path):
                    continue

                image = cv2.imread(full_path)
                if image is None:
                    continue

                text_regions = await self._detect_text_regions(image)
                for region in text_regions:
                    region['source_screenshot'] = screenshot_name
                    all_text_regions.append(region)

            # Categorize text regions by size (heading vs body)
            headings = []
            body_text = []

            for region in all_text_regions:
                height = region['position']['height']
                if height > 25:  # Likely headings
                    headings.append(region)
                else:  # Likely body text
                    body_text.append(region)

            # Analyze heading patterns
            if headings:
                heading_sizes = [r['position']['height'] for r in headings]
                patterns['heading_patterns'] = {
                    'count': len(headings),
                    'average_size': round(sum(heading_sizes) / len(heading_sizes), 1),
                    'size_range': [min(heading_sizes), max(heading_sizes)],
                    'size_consistency': self._calculate_size_consistency(heading_sizes)
                }

            # Analyze body text patterns
            if body_text:
                body_sizes = [r['position']['height'] for r in body_text]
                patterns['body_text_patterns'] = {
                    'count': len(body_text),
                    'average_size': round(sum(body_sizes) / len(body_sizes), 1),
                    'size_range': [min(body_sizes), max(body_sizes)],
                    'size_consistency': self._calculate_size_consistency(body_sizes)
                }

            # Calculate overall consistency
            heading_consistency = patterns.get('heading_patterns', {}).get('size_consistency', 0)
            body_consistency = patterns.get('body_text_patterns', {}).get('size_consistency', 0)
            patterns['consistency_score'] = (heading_consistency + body_consistency) / 2

        except Exception as e:
            self.logger.error(f"Typography pattern analysis failed: {e}")

        return patterns

    def _calculate_size_consistency(self, sizes: List[int]) -> float:
        """
        Calculate consistency score for text sizes (0-1, higher is more consistent)
        """
        if not sizes or len(sizes) < 2:
            return 1.0

        # Calculate coefficient of variation (std dev / mean)
        mean_size = sum(sizes) / len(sizes)
        variance = sum((size - mean_size) ** 2 for size in sizes) / len(sizes)
        std_dev = variance ** 0.5

        if mean_size == 0:
            return 0.0

        cv = std_dev / mean_size

        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0, 1 - cv)
        return round(consistency, 3)

    def _calculate_typography_consistency(self, fonts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate typography consistency metrics
        """
        consistency_data = {
            'overall_score': 0,
            'font_variety_score': 0,
            'size_consistency_score': 0,
            'weight_consistency_score': 0,
            'recommendations': []
        }

        try:
            if not fonts:
                return consistency_data

            # Count unique fonts
            unique_fonts = set(font.get('name', 'Unknown') for font in fonts)
            font_count = len(unique_fonts)

            # Font variety score (2-4 fonts is ideal)
            if font_count <= 1:
                consistency_data['font_variety_score'] = 0.5
                consistency_data['recommendations'].append("Consider using more font variety for hierarchy")
            elif 2 <= font_count <= 4:
                consistency_data['font_variety_score'] = 1.0
            elif font_count <= 6:
                consistency_data['font_variety_score'] = 0.8
                consistency_data['recommendations'].append("Consider reducing font variety for better consistency")
            else:
                consistency_data['font_variety_score'] = 0.4
                consistency_data['recommendations'].append("Too many fonts may reduce brand consistency")

            # Size consistency
            size_categories = [font.get('size_category', 'medium') for font in fonts]
            size_variety = len(set(size_categories))
            consistency_data['size_consistency_score'] = max(0.3, 1.0 - (size_variety * 0.1))

            # Weight consistency
            weights = [font.get('weight', 'normal') for font in fonts]
            weight_variety = len(set(weights))
            consistency_data['weight_consistency_score'] = max(0.4, 1.0 - (weight_variety * 0.15))

            # Overall score
            scores = [
                consistency_data['font_variety_score'],
                consistency_data['size_consistency_score'],
                consistency_data['weight_consistency_score']
            ]
            consistency_data['overall_score'] = round(sum(scores) / len(scores), 2)

        except Exception as e:
            self.logger.error(f"Typography consistency calculation failed: {e}")

        return consistency_data

    def _process_detected_fonts(self, fonts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and deduplicate detected fonts
        """
        try:
            if not fonts:
                return []

            # Group fonts by name and type
            font_groups = {}
            for font in fonts:
                key = (font.get('name', 'Unknown'), font.get('type', 'unknown'))
                if key not in font_groups:
                    font_groups[key] = []
                font_groups[key].append(font)

            # Create consolidated font list
            processed_fonts = []
            for (name, font_type), font_list in font_groups.items():
                # Merge information from multiple detections
                consolidated_font = {
                    'name': name,
                    'type': font_type,
                    'detection_count': len(font_list),
                    'sources': list(set(f.get('source', 'unknown') for f in font_list)),
                    'detection_methods': list(set(f.get('detection_method', 'unknown') for f in font_list)),
                    'confidence': min(1.0, len(font_list) * 0.2)  # Higher confidence for multiple detections
                }

                # Add additional characteristics if available
                characteristics = {}
                for font in font_list:
                    if 'characteristics' in font:
                        characteristics.update(font['characteristics'])

                if characteristics:
                    consolidated_font['characteristics'] = characteristics

                processed_fonts.append(consolidated_font)

            # Sort by confidence and detection count
            processed_fonts.sort(key=lambda x: (x['confidence'], x['detection_count']), reverse=True)

            return processed_fonts[:15]  # Limit to top 15 fonts

        except Exception as e:
            self.logger.error(f"Font processing failed: {e}")
            return fonts

    async def analyze_visual_consistency(self, visual_assets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall visual consistency across all detected brand assets
        """
        consistency_analysis = {
            'overall_score': 0,
            'color_consistency': {},
            'logo_consistency': {},
            'typography_consistency': {},
            'visual_harmony': {},
            'recommendations': [],
            'analysis_timestamp': datetime.now().isoformat()
        }

        try:
            scores = []

            # Color consistency analysis
            if 'color_palette' in visual_assets:
                color_data = visual_assets['color_palette']
                consistency_analysis['color_consistency'] = self._analyze_color_consistency(color_data)
                scores.append(consistency_analysis['color_consistency'].get('score', 0))

            # Logo consistency analysis
            if 'logos' in visual_assets:
                logos = visual_assets['logos']
                consistency_analysis['logo_consistency'] = self._analyze_logo_consistency_detailed(logos)
                scores.append(consistency_analysis['logo_consistency'].get('score', 0))

            # Typography consistency analysis
            if 'typography' in visual_assets:
                typography = visual_assets['typography']
                consistency_analysis['typography_consistency'] = typography.get('font_consistency', {})
                scores.append(consistency_analysis['typography_consistency'].get('overall_score', 0))

            # Visual harmony analysis (how well everything works together)
            consistency_analysis['visual_harmony'] = self._analyze_visual_harmony(visual_assets)
            scores.append(consistency_analysis['visual_harmony'].get('score', 0))

            # Calculate overall score
            if scores:
                consistency_analysis['overall_score'] = round(sum(scores) / len(scores), 2)

            # Generate recommendations
            consistency_analysis['recommendations'] = self._generate_visual_recommendations(consistency_analysis)

        except Exception as e:
            self.logger.error(f"Visual consistency analysis failed: {e}")
            consistency_analysis['error'] = str(e)

        return consistency_analysis

    def _analyze_color_consistency(self, color_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze color palette consistency
        """
        analysis = {
            'score': 0,
            'palette_size': 0,
            'color_harmony': 'unknown',
            'issues': [],
            'strengths': []
        }

        try:
            primary_colors = color_data.get('primary_colors', [])
            analysis['palette_size'] = len(primary_colors)

            if analysis['palette_size'] == 0:
                analysis['score'] = 0
                analysis['issues'].append("No primary colors detected")
            elif analysis['palette_size'] <= 3:
                analysis['score'] = 90
                analysis['strengths'].append("Focused color palette")
            elif analysis['palette_size'] <= 5:
                analysis['score'] = 75
                analysis['strengths'].append("Balanced color palette")
            else:
                analysis['score'] = 50
                analysis['issues'].append("Too many primary colors may reduce consistency")

            # Analyze color harmony if color analysis data is available
            color_analysis = color_data.get('color_analysis', {})
            if color_analysis.get('color_harmony_type'):
                analysis['color_harmony'] = color_analysis['color_harmony_type']
                analysis['score'] += 10  # Bonus for having color harmony

        except Exception as e:
            self.logger.error(f"Color consistency analysis failed: {e}")

        return analysis

    def _analyze_logo_consistency_detailed(self, logos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detailed logo consistency analysis
        """
        analysis = {
            'score': 0,
            'logo_count': len(logos),
            'quality_distribution': {},
            'detection_methods': [],
            'issues': [],
            'strengths': []
        }

        try:
            if not logos:
                analysis['score'] = 0
                analysis['issues'].append("No logos detected")
                return analysis

            # Analyze logo quality distribution
            quality_scores = [logo.get('quality_score', 0) for logo in logos if 'quality_score' in logo]
            if quality_scores:
                analysis['quality_distribution'] = {
                    'average': round(sum(quality_scores) / len(quality_scores), 2),
                    'highest': max(quality_scores),
                    'lowest': min(quality_scores)
                }

            # Analyze detection methods
            methods = [logo.get('detection_method', 'unknown') for logo in logos]
            analysis['detection_methods'] = list(set(methods))

            # Score based on logo count and quality
            if analysis['logo_count'] == 0:
                analysis['score'] = 0
            elif analysis['logo_count'] <= 3:
                analysis['score'] = 85
                analysis['strengths'].append("Good logo detection count")
            elif analysis['logo_count'] <= 6:
                analysis['score'] = 70
            else:
                analysis['score'] = 50
                analysis['issues'].append("Many logo detections may indicate inconsistent branding")

            # Bonus for high-quality logos
            if quality_scores and analysis['quality_distribution']['average'] > 0.7:
                analysis['score'] += 15
                analysis['strengths'].append("High-quality logo detections")

        except Exception as e:
            self.logger.error(f"Logo consistency analysis failed: {e}")

        return analysis

    def _analyze_visual_harmony(self, visual_assets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how well different visual elements work together
        """
        harmony = {
            'score': 0,
            'color_logo_harmony': 0,
            'typography_color_harmony': 0,
            'overall_cohesion': 0,
            'analysis': {}
        }

        try:
            scores = []

            # Color-Logo harmony
            if 'color_palette' in visual_assets and 'logos' in visual_assets:
                # Simple heuristic: if we have both colors and logos, they likely work together
                harmony['color_logo_harmony'] = 75
                scores.append(75)

            # Typography-Color harmony
            if 'typography' in visual_assets and 'color_palette' in visual_assets:
                # Simple heuristic: consistent typography with defined colors
                typography_score = visual_assets['typography'].get('font_consistency', {}).get('overall_score', 0)
                color_count = len(visual_assets['color_palette'].get('primary_colors', []))

                if typography_score > 0.7 and 2 <= color_count <= 5:
                    harmony['typography_color_harmony'] = 80
                else:
                    harmony['typography_color_harmony'] = 60

                scores.append(harmony['typography_color_harmony'])

            # Overall cohesion
            asset_count = sum(1 for key in ['color_palette', 'logos', 'typography'] if key in visual_assets)
            if asset_count >= 3:
                harmony['overall_cohesion'] = 85
                scores.append(85)
            elif asset_count == 2:
                harmony['overall_cohesion'] = 70
                scores.append(70)
            else:
                harmony['overall_cohesion'] = 40
                scores.append(40)

            # Calculate overall harmony score
            if scores:
                harmony['score'] = round(sum(scores) / len(scores), 2)

        except Exception as e:
            self.logger.error(f"Visual harmony analysis failed: {e}")

        return harmony

    def _generate_visual_recommendations(self, consistency_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on visual consistency analysis
        """
        recommendations = []

        try:
            overall_score = consistency_analysis.get('overall_score', 0)

            # Overall recommendations
            if overall_score < 50:
                recommendations.append("Consider a comprehensive brand identity review to improve visual consistency")
            elif overall_score < 70:
                recommendations.append("Good foundation - focus on refining specific visual elements")
            else:
                recommendations.append("Strong visual consistency - maintain current brand standards")

            # Color-specific recommendations
            color_consistency = consistency_analysis.get('color_consistency', {})
            if color_consistency.get('score', 0) < 60:
                recommendations.extend(color_consistency.get('issues', []))

            # Logo-specific recommendations
            logo_consistency = consistency_analysis.get('logo_consistency', {})
            if logo_consistency.get('score', 0) < 60:
                recommendations.extend(logo_consistency.get('issues', []))

            # Typography-specific recommendations
            typography_consistency = consistency_analysis.get('typography_consistency', {})
            typography_recs = typography_consistency.get('recommendations', [])
            recommendations.extend(typography_recs)

            # Visual harmony recommendations
            harmony = consistency_analysis.get('visual_harmony', {})
            if harmony.get('score', 0) < 60:
                recommendations.append("Improve coordination between visual elements (colors, logos, typography)")

        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")

        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def analyze_website_content(self, website_url: str) -> Dict[str, Any]:
        """Analyze website content for brand messaging"""
        if not WEB_SCRAPING_AVAILABLE:
            return {}
        
        try:
            response = requests.get(website_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc_content = meta_desc.get('content', '') if meta_desc else ''

            return {
                'title': soup.title.string if soup.title else '',
                'meta_description': meta_desc_content,
                'headings': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]],
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {}
    
    def calculate_color_consistency_score(self, colors: Dict[str, Any]) -> int:
        """Calculate color consistency score - enhanced version"""
        if not colors or not colors.get('primary_colors'):
            return 0

        # Use enhanced consistency calculation if available
        if 'color_consistency' in colors and isinstance(colors['color_consistency'], dict):
            return colors['color_consistency'].get('overall_score', 0)

        # Fallback to basic scoring for backward compatibility
        score = 30  # Base score

        # Score based on color palette completeness
        primary_count = len(colors.get('primary_colors', []))
        secondary_count = len(colors.get('secondary_colors', []))

        if primary_count >= 1:
            score += 20
        if primary_count >= 3:
            score += 20
        if secondary_count >= 3:
            score += 30

        # Bonus for color analysis data
        if colors.get('color_analysis', {}).get('color_harmony_type'):
            score += 10

        return min(100, score)

    def calculate_logo_quality_score(self, logos: List[Dict[str, Any]]) -> int:
        """Calculate logo quality score"""
        if not logos:
            return 0

        # Calculate average quality score from detected logos
        quality_scores = [logo.get('quality_score', 0) for logo in logos if 'quality_score' in logo]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            return int(avg_quality * 100)  # Convert to 0-100 scale

        # Fallback scoring based on logo count and detection methods
        score = min(50, len(logos) * 10)  # Base score from logo count

        # Bonus for diverse detection methods
        methods = set(logo.get('detection_method', 'unknown') for logo in logos)
        if len(methods) > 1:
            score += 20

        return min(100, score)
    
    def calculate_content_quality_score(self, content: Dict[str, Any]) -> int:
        """Calculate content quality score"""
        if not content:
            return 0
        
        score = 0
        if content.get('title'):
            score += 25
        if content.get('meta_description'):
            score += 25
        if content.get('headings'):
            score += 50
        
        return min(100, score)

    def calculate_social_presence_score(self, social_analysis: Dict[str, Any]) -> int:
        """Calculate social media presence score"""
        if not social_analysis or social_analysis.get('error'):
            return 0

        score = 0
        social_platforms = social_analysis.get('social_platforms', {})

        # Base score for having social media presence
        if social_platforms:
            score += 30

        # Additional points for platform diversity
        platform_count = len(social_platforms)
        if platform_count >= 3:
            score += 40
        elif platform_count >= 2:
            score += 25
        elif platform_count >= 1:
            score += 15

        # Points for social insights quality
        social_insights = social_analysis.get('social_insights', {})
        if social_insights and not social_insights.get('error'):
            score += 30

        return min(100, score)

    def calculate_overall_visual_score(self, visual_scores: Dict[str, int]) -> int:
        """Calculate overall visual analysis score"""
        scores = [score for score in visual_scores.values() if isinstance(score, int)]
        return int(sum(scores) / len(scores)) if scores else 0

    def calculate_color_consistency_score_from_brandfetch(self, colors: List[Dict[str, Any]]) -> int:
        """Calculate color consistency score from Brandfetch color data"""
        if not colors:
            return 0

        # Score based on number of colors and their organization
        color_count = len(colors)

        if color_count >= 3:
            return 90  # Good color palette
        elif color_count >= 2:
            return 75  # Decent color palette
        elif color_count >= 1:
            return 60  # Minimal color palette
        else:
            return 0   # No colors found

    async def store_visual_assets_in_database(self, brand_name: str, analysis_id: str, visual_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store visual assets in database for persistence and future retrieval
        Integrates with existing Brand and Analysis models
        """
        storage_result = {
            'success': False,
            'stored_assets': {},
            'errors': [],
            'database_available': self.database_available
        }

        if not self.database_available or not self.db_service:
            storage_result['errors'].append("Database service not available")
            return storage_result

        try:
            # Get or create brand record
            brand_record = self.db_service.get_or_create_brand(brand_name)
            if not brand_record:
                storage_result['errors'].append("Failed to create/retrieve brand record")
                return storage_result

            # Get analysis record
            analysis_record = self.db_service.get_analysis(analysis_id)
            if not analysis_record:
                storage_result['errors'].append("Analysis record not found")
                return storage_result

            # Store visual assets data in analysis results
            visual_assets = visual_results.get('visual_assets', {})
            visual_scores = visual_results.get('visual_scores', {})

            # Update analysis with visual data
            if analysis_record.results:
                analysis_record.results.update({
                    'visual_analysis': visual_results,
                    'visual_assets': visual_assets,
                    'visual_scores': visual_scores
                })
            else:
                analysis_record.results = {
                    'visual_analysis': visual_results,
                    'visual_assets': visual_assets,
                    'visual_scores': visual_scores
                }

            # Update brand record with visual information
            if 'color_palette' in visual_assets:
                colors = visual_assets['color_palette'].get('primary_colors', [])
                if colors and len(colors) > 0:
                    # Store primary color in brand record
                    primary_color = colors[0]
                    if isinstance(primary_color, dict) and 'hex' in primary_color:
                        brand_record.primary_color = primary_color['hex']
                    elif isinstance(primary_color, str):
                        brand_record.primary_color = primary_color

            # Store logo URL if available
            if 'logos' in visual_assets:
                logos = visual_assets['logos']
                if logos and len(logos) > 0:
                    logo = logos[0]
                    if isinstance(logo, dict) and 'filename' in logo:
                        brand_record.logo_url = logo['filename']
                    elif isinstance(logo, str):
                        brand_record.logo_url = logo

            # Save changes to database
            self.db_service.save_analysis(analysis_record)
            self.db_service.save_brand(brand_record)

            storage_result['success'] = True
            storage_result['stored_assets'] = {
                'brand_id': brand_record.id,
                'analysis_id': analysis_record.id,
                'visual_assets_count': len(visual_assets),
                'visual_scores_count': len(visual_scores),
                'primary_color_stored': bool(brand_record.primary_color),
                'logo_url_stored': bool(brand_record.logo_url)
            }

            self.logger.info(f"Visual assets stored in database for {brand_name}")

        except Exception as e:
            error_msg = f"Database storage failed: {str(e)}"
            self.logger.error(error_msg)
            storage_result['errors'].append(error_msg)

        return storage_result

    async def retrieve_visual_assets_from_database(self, brand_name: str, analysis_id: str = None) -> Dict[str, Any]:
        """
        Retrieve stored visual assets from database
        Can retrieve by brand name or specific analysis ID
        """
        retrieval_result = {
            'success': False,
            'visual_assets': {},
            'visual_scores': {},
            'brand_info': {},
            'errors': [],
            'database_available': self.database_available
        }

        if not self.database_available or not self.db_service:
            retrieval_result['errors'].append("Database service not available")
            return retrieval_result

        try:
            if analysis_id:
                # Retrieve specific analysis
                analysis_record = self.db_service.get_analysis(analysis_id)
                if not analysis_record:
                    retrieval_result['errors'].append("Analysis record not found")
                    return retrieval_result

                if analysis_record.results:
                    visual_analysis = analysis_record.results.get('visual_analysis', {})
                    retrieval_result['visual_assets'] = visual_analysis.get('visual_assets', {})
                    retrieval_result['visual_scores'] = visual_analysis.get('visual_scores', {})

                # Get brand info
                brand_record = self.db_service.get_brand_by_id(analysis_record.brand_id)
                if brand_record:
                    retrieval_result['brand_info'] = {
                        'name': brand_record.name,
                        'website': brand_record.website,
                        'primary_color': brand_record.primary_color,
                        'logo_url': brand_record.logo_url,
                        'industry': brand_record.industry
                    }

            else:
                # Retrieve latest analysis for brand
                brand_record = self.db_service.get_brand_by_name(brand_name)
                if not brand_record:
                    retrieval_result['errors'].append("Brand record not found")
                    return retrieval_result

                # Get latest analysis for this brand
                latest_analysis = self.db_service.get_latest_analysis_for_brand(brand_record.id)
                if latest_analysis and latest_analysis.results:
                    visual_analysis = latest_analysis.results.get('visual_analysis', {})
                    retrieval_result['visual_assets'] = visual_analysis.get('visual_assets', {})
                    retrieval_result['visual_scores'] = visual_analysis.get('visual_scores', {})

                retrieval_result['brand_info'] = {
                    'name': brand_record.name,
                    'website': brand_record.website,
                    'primary_color': brand_record.primary_color,
                    'logo_url': brand_record.logo_url,
                    'industry': brand_record.industry
                }

            retrieval_result['success'] = True
            self.logger.info(f"Visual assets retrieved from database for {brand_name}")

        except Exception as e:
            error_msg = f"Database retrieval failed: {str(e)}"
            self.logger.error(error_msg)
            retrieval_result['errors'].append(error_msg)

        return retrieval_result

    async def get_cached_visual_analysis(self, brand_name: str, website_url: str) -> Dict[str, Any]:
        """
        Get cached visual analysis if available, otherwise perform new analysis
        Integrates with intelligent cache service if available
        """
        cache_key = f"visual_analysis_{brand_name}_{hash(website_url)}"

        # Try to get from cache first
        if OPTIMIZATION_SERVICES_AVAILABLE:
            try:
                cached_result = intelligent_cache.get(cache_key)
                if cached_result:
                    self.logger.info(f"Retrieved cached visual analysis for {brand_name}")
                    cached_result['cache_hit'] = True
                    return cached_result
            except Exception as e:
                self.logger.warning(f"Cache retrieval failed: {e}")

        # No cache hit, perform new analysis
        self.logger.info(f"Performing new visual analysis for {brand_name}")
        result = await self.analyze_brand_visuals(brand_name, website_url)
        result['cache_hit'] = False

        # Store in cache for future use
        if OPTIMIZATION_SERVICES_AVAILABLE and not result.get('errors'):
            try:
                # Cache for 24 hours
                intelligent_cache.set(cache_key, result, ttl=86400)
                self.logger.info(f"Cached visual analysis for {brand_name}")
            except Exception as e:
                self.logger.warning(f"Cache storage failed: {e}")

        return result

    async def optimize_visual_assets(self, visual_assets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize visual assets using image optimization service if available
        """
        optimization_result = {
            'success': False,
            'optimized_assets': {},
            'optimization_stats': {},
            'errors': []
        }

        if not OPTIMIZATION_SERVICES_AVAILABLE:
            optimization_result['errors'].append("Optimization services not available")
            return optimization_result

        try:
            optimized_assets = {}
            optimization_stats = {
                'screenshots_optimized': 0,
                'logos_optimized': 0,
                'total_size_reduction': 0,
                'optimization_time': 0
            }

            start_time = time.time()

            # Optimize screenshots
            screenshots = visual_assets.get('screenshots', {})
            if isinstance(screenshots, dict):
                optimized_screenshots = {}

                # Handle nested screenshot structure
                if 'screenshots' in screenshots:
                    screenshot_paths = screenshots['screenshots']
                else:
                    screenshot_paths = screenshots

                for name, path in screenshot_paths.items():
                    if isinstance(path, str) and path.startswith('/static/'):
                        try:
                            # Convert to absolute path
                            abs_path = path.replace('/static/', 'src/static/')
                            if os.path.exists(abs_path):
                                optimized_path = await image_optimization_service.optimize_image(
                                    abs_path,
                                    quality=85,
                                    max_width=1920
                                )
                                if optimized_path:
                                    optimized_screenshots[name] = optimized_path.replace('src/static/', '/static/')
                                    optimization_stats['screenshots_optimized'] += 1
                                else:
                                    optimized_screenshots[name] = path
                            else:
                                optimized_screenshots[name] = path
                        except Exception as e:
                            self.logger.warning(f"Screenshot optimization failed for {name}: {e}")
                            optimized_screenshots[name] = path

                optimized_assets['screenshots'] = optimized_screenshots

            # Optimize logos
            logos = visual_assets.get('logos', [])
            if isinstance(logos, list):
                optimized_logos = []

                for logo in logos:
                    if isinstance(logo, dict) and 'filename' in logo:
                        logo_path = logo['filename']
                        if isinstance(logo_path, str) and logo_path.startswith('/static/'):
                            try:
                                abs_path = logo_path.replace('/static/', 'src/static/')
                                if os.path.exists(abs_path):
                                    optimized_path = await image_optimization_service.optimize_image(
                                        abs_path,
                                        quality=90,
                                        max_width=500
                                    )
                                    if optimized_path:
                                        logo_copy = logo.copy()
                                        logo_copy['filename'] = optimized_path.replace('src/static/', '/static/')
                                        logo_copy['optimized'] = True
                                        optimized_logos.append(logo_copy)
                                        optimization_stats['logos_optimized'] += 1
                                    else:
                                        optimized_logos.append(logo)
                                else:
                                    optimized_logos.append(logo)
                            except Exception as e:
                                self.logger.warning(f"Logo optimization failed: {e}")
                                optimized_logos.append(logo)
                        else:
                            optimized_logos.append(logo)
                    else:
                        optimized_logos.append(logo)

                optimized_assets['logos'] = optimized_logos

            # Copy other assets without modification
            for key, value in visual_assets.items():
                if key not in ['screenshots', 'logos']:
                    optimized_assets[key] = value

            optimization_stats['optimization_time'] = time.time() - start_time

            optimization_result['success'] = True
            optimization_result['optimized_assets'] = optimized_assets
            optimization_result['optimization_stats'] = optimization_stats

            self.logger.info(f"Visual asset optimization completed: {optimization_stats}")

        except Exception as e:
            error_msg = f"Visual asset optimization failed: {str(e)}"
            self.logger.error(error_msg)
            optimization_result['errors'].append(error_msg)

        return optimization_result

    async def analyze_brand_visuals_with_fallback(self, brand_name: str, website_url: str, brand_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced visual analysis with comprehensive error handling and fallback strategies
        Ensures robust operation even when some components fail
        """
        self.logger.info(f"Starting robust visual analysis for {brand_name}")

        results = {
            'brand_name': brand_name,
            'website_url': website_url,
            'analysis_timestamp': datetime.now().isoformat(),
            'capabilities_used': self.get_capabilities(),
            'visual_assets': {},
            'visual_scores': {},
            'fallback_strategies_used': [],
            'errors': [],
            'warnings': []
        }

        # Strategy 1: Try full analysis first
        try:
            full_result = await self.analyze_brand_visuals(brand_name, website_url, brand_data)
            if not full_result.get('errors') or len(full_result.get('errors', [])) < 3:
                # Full analysis succeeded or had minimal errors
                return full_result
            else:
                # Full analysis had significant errors, continue with fallback strategies
                results['warnings'].append("Full analysis had errors, using fallback strategies")
                results['errors'].extend(full_result.get('errors', []))
        except Exception as e:
            results['errors'].append(f"Full analysis failed: {str(e)}")
            results['warnings'].append("Using fallback strategies due to full analysis failure")

        # Strategy 2: Try individual components with error isolation
        await self._analyze_with_component_isolation(brand_name, website_url, brand_data, results)

        # Strategy 3: Use cached or database data if available
        await self._use_cached_or_stored_data(brand_name, results)

        # Strategy 4: Generate minimal analysis from available data
        await self._generate_minimal_analysis(brand_name, website_url, brand_data, results)

        # Calculate final scores based on available data
        results['visual_scores']['overall_visual_score'] = self.calculate_overall_visual_score(results['visual_scores'])

        self.logger.info(f"Robust visual analysis completed for {brand_name} with {len(results['fallback_strategies_used'])} fallback strategies")
        return results

    async def _analyze_with_component_isolation(self, brand_name: str, website_url: str, brand_data: Dict[str, Any], results: Dict[str, Any]):
        """Analyze individual components with error isolation"""

        # Component 1: Screenshot capture (most critical)
        try:
            if PLAYWRIGHT_AVAILABLE:
                screenshots = await self.capture_website_screenshots(website_url, brand_name)
                if screenshots and not screenshots.get('error'):
                    results['visual_assets']['screenshots'] = screenshots
                    results['fallback_strategies_used'].append('isolated_screenshot_capture')
                    self.logger.info("Screenshot capture succeeded in isolation")
        except Exception as e:
            results['errors'].append(f"Isolated screenshot capture failed: {str(e)}")

        # Component 2: Brandfetch integration (if available)
        try:
            if brand_data and not brand_data.get('error'):
                # Extract Brandfetch data safely
                if brand_data.get('logos'):
                    results['visual_assets']['logos'] = brand_data['logos']
                    results['visual_scores']['logo_availability'] = 100
                    results['fallback_strategies_used'].append('brandfetch_logo_extraction')

                if brand_data.get('colors'):
                    results['visual_assets']['color_palette'] = {
                        'primary_colors': brand_data['colors'],
                        'source': 'brandfetch'
                    }
                    results['visual_scores']['color_consistency'] = self.calculate_color_consistency_score_from_brandfetch(brand_data['colors'])
                    results['fallback_strategies_used'].append('brandfetch_color_extraction')

                if brand_data.get('fonts'):
                    results['visual_assets']['fonts'] = brand_data['fonts']
                    results['visual_scores']['typography_consistency'] = 85
                    results['fallback_strategies_used'].append('brandfetch_font_extraction')

                self.logger.info("Brandfetch data integration succeeded in isolation")
        except Exception as e:
            results['errors'].append(f"Isolated Brandfetch integration failed: {str(e)}")

        # Component 3: Color analysis (if screenshots available)
        try:
            if VISUAL_PROCESSING_AVAILABLE and 'screenshots' in results['visual_assets']:
                colors = await self.extract_brand_colors(results['visual_assets']['screenshots'])
                if colors and not colors.get('error'):
                    # Merge with existing color data if available
                    existing_colors = results['visual_assets'].get('color_palette', {})
                    if existing_colors:
                        # Combine colors from different sources
                        combined_colors = self._merge_color_data(existing_colors, colors)
                        results['visual_assets']['color_palette'] = combined_colors
                    else:
                        results['visual_assets']['color_palette'] = colors

                    results['visual_scores']['color_consistency'] = self.calculate_color_consistency_score(colors)
                    results['fallback_strategies_used'].append('isolated_color_analysis')
                    self.logger.info("Color analysis succeeded in isolation")
        except Exception as e:
            results['errors'].append(f"Isolated color analysis failed: {str(e)}")

        # Component 4: Basic web content analysis
        try:
            if WEB_SCRAPING_AVAILABLE:
                content_analysis = await self.analyze_website_content(website_url)
                if content_analysis:
                    results['visual_assets']['content_analysis'] = content_analysis
                    results['visual_scores']['content_quality'] = self.calculate_content_quality_score(content_analysis)
                    results['fallback_strategies_used'].append('isolated_content_analysis')
                    self.logger.info("Content analysis succeeded in isolation")
        except Exception as e:
            results['errors'].append(f"Isolated content analysis failed: {str(e)}")

    async def _use_cached_or_stored_data(self, brand_name: str, results: Dict[str, Any]):
        """Try to use cached or stored data as fallback"""

        # Try database retrieval
        try:
            stored_data = await self.retrieve_visual_assets_from_database(brand_name)
            if stored_data.get('success') and stored_data.get('visual_assets'):
                # Merge stored data with current results
                stored_assets = stored_data['visual_assets']
                stored_scores = stored_data.get('visual_scores', {})

                for key, value in stored_assets.items():
                    if key not in results['visual_assets'] and value:
                        results['visual_assets'][key] = value
                        results['fallback_strategies_used'].append(f'database_{key}')

                for key, value in stored_scores.items():
                    if key not in results['visual_scores'] and value:
                        results['visual_scores'][key] = value

                self.logger.info("Used stored database data as fallback")
        except Exception as e:
            results['errors'].append(f"Database fallback failed: {str(e)}")

        # Try cache retrieval (if different from database)
        if OPTIMIZATION_SERVICES_AVAILABLE:
            try:
                cache_key = f"visual_analysis_fallback_{brand_name}"
                cached_result = intelligent_cache.get(cache_key)
                if cached_result and cached_result.get('visual_assets'):
                    cached_assets = cached_result['visual_assets']

                    for key, value in cached_assets.items():
                        if key not in results['visual_assets'] and value:
                            results['visual_assets'][key] = value
                            results['fallback_strategies_used'].append(f'cache_{key}')

                    self.logger.info("Used cached data as fallback")
            except Exception as e:
                results['errors'].append(f"Cache fallback failed: {str(e)}")

    async def _generate_minimal_analysis(self, brand_name: str, website_url: str, brand_data: Dict[str, Any], results: Dict[str, Any]):
        """Generate minimal analysis from whatever data is available"""

        # Ensure we have at least basic structure
        if 'visual_assets' not in results:
            results['visual_assets'] = {}
        if 'visual_scores' not in results:
            results['visual_scores'] = {}

        # Generate basic scores based on available data
        asset_count = len(results['visual_assets'])
        if asset_count > 0:
            results['visual_scores']['data_availability'] = min(100, asset_count * 25)
            results['fallback_strategies_used'].append('minimal_scoring')

        # Add basic metadata
        results['visual_assets']['analysis_metadata'] = {
            'brand_name': brand_name,
            'website_url': website_url,
            'analysis_type': 'fallback_analysis',
            'components_analyzed': list(results['visual_assets'].keys()),
            'fallback_strategies': results['fallback_strategies_used']
        }

        self.logger.info(f"Generated minimal analysis with {asset_count} visual assets")

    def _merge_color_data(self, existing_colors: Dict[str, Any], new_colors: Dict[str, Any]) -> Dict[str, Any]:
        """Merge color data from different sources"""
        merged = existing_colors.copy()

        # Merge primary colors
        existing_primary = existing_colors.get('primary_colors', [])
        new_primary = new_colors.get('primary_colors', [])

        # Combine and deduplicate colors
        all_colors = existing_primary + new_primary
        unique_colors = []
        seen_colors = set()

        for color in all_colors:
            color_key = color.get('hex', str(color)) if isinstance(color, dict) else str(color)
            if color_key not in seen_colors:
                unique_colors.append(color)
                seen_colors.add(color_key)

        merged['primary_colors'] = unique_colors[:10]  # Limit to top 10
        merged['sources'] = list(set([
            existing_colors.get('source', 'unknown'),
            new_colors.get('source', 'unknown')
        ]))

        return merged
