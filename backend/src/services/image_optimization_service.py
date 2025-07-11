"""
Image Optimization Service for Brand Audit App
Handles image compression, format conversion, and progressive loading
"""

import os
import asyncio
import aiofiles
import logging
from PIL import Image, ImageOps
from io import BytesIO
import hashlib
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import cv2
import numpy as np


class ImageOptimizationService:
    """
    Service for optimizing images for performance while maintaining quality
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path("assets/optimized_images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Optimization settings
        self.quality_settings = {
            'thumbnail': {'size': (150, 150), 'quality': 85, 'format': 'WEBP'},
            'medium': {'size': (800, 600), 'quality': 90, 'format': 'WEBP'},
            'large': {'size': (1920, 1080), 'quality': 95, 'format': 'WEBP'},
            'original': {'quality': 100, 'format': 'PNG'}
        }
        
        # Supported formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
    async def optimize_image_async(self, image_path: str, optimization_level: str = 'medium') -> Dict[str, Any]:
        """
        Optimize a single image asynchronously
        """
        try:
            if not os.path.exists(image_path):
                return {"error": f"Image not found: {image_path}"}
            
            # Generate cache key
            cache_key = self._generate_cache_key(image_path, optimization_level)
            cached_path = self.cache_dir / f"{cache_key}.webp"
            
            # Check if optimized version exists
            if cached_path.exists():
                return await self._get_cached_image_info(cached_path, image_path)
            
            # Optimize image
            optimized_info = await self._optimize_single_image(image_path, optimization_level, cached_path)
            return optimized_info
            
        except Exception as e:
            self.logger.error(f"Image optimization failed for {image_path}: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_image_batch(self, image_paths: List[str], optimization_level: str = 'medium') -> Dict[str, Any]:
        """
        Optimize multiple images concurrently
        """
        if not image_paths:
            return {"optimized_images": [], "errors": []}
        
        # Create optimization tasks
        tasks = [
            self.optimize_image_async(path, optimization_level) 
            for path in image_paths
        ]
        
        # Execute concurrently with semaphore to limit resource usage
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent optimizations
        
        async def optimize_with_semaphore(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(
            *[optimize_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Separate successful optimizations from errors
        optimized_images = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Failed to optimize {image_paths[i]}: {str(result)}")
            elif result.get("error"):
                errors.append(f"Failed to optimize {image_paths[i]}: {result['error']}")
            else:
                optimized_images.append(result)
        
        return {
            "optimized_images": optimized_images,
            "errors": errors,
            "total_processed": len(image_paths),
            "successful": len(optimized_images)
        }
    
    async def create_progressive_variants(self, image_path: str) -> Dict[str, Any]:
        """
        Create multiple variants of an image for progressive loading
        """
        try:
            variants = {}
            
            # Create all variants concurrently
            tasks = [
                self.optimize_image_async(image_path, level)
                for level in ['thumbnail', 'medium', 'large']
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                level = ['thumbnail', 'medium', 'large'][i]
                if not isinstance(result, Exception) and not result.get("error"):
                    variants[level] = result
            
            return {
                "original_path": image_path,
                "variants": variants,
                "progressive_loading_ready": len(variants) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Progressive variants creation failed: {str(e)}")
            return {"error": str(e)}
    
    async def _optimize_single_image(self, image_path: str, optimization_level: str, output_path: Path) -> Dict[str, Any]:
        """
        Optimize a single image with specified settings
        """
        settings = self.quality_settings.get(optimization_level, self.quality_settings['medium'])
        
        # Read image asynchronously
        async with aiofiles.open(image_path, 'rb') as f:
            image_data = await f.read()
        
        # Process image in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self._process_image_sync, 
            image_data, 
            settings, 
            str(output_path)
        )
        
        return result
    
    def _process_image_sync(self, image_data: bytes, settings: Dict, output_path: str) -> Dict[str, Any]:
        """
        Synchronous image processing (runs in thread pool)
        """
        try:
            # Open image
            image = Image.open(BytesIO(image_data))
            original_size = image.size
            original_format = image.format
            original_size_bytes = len(image_data)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Handle transparency
                if settings['format'] == 'WEBP':
                    # WebP supports transparency
                    pass
                else:
                    # Convert to RGB with white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
            
            # Resize if size is specified
            if 'size' in settings:
                image = ImageOps.fit(image, settings['size'], Image.Resampling.LANCZOS)
            
            # Save optimized image
            save_kwargs = {
                'format': settings['format'],
                'quality': settings['quality'],
                'optimize': True
            }
            
            if settings['format'] == 'WEBP':
                save_kwargs['method'] = 6  # Best compression
            
            image.save(output_path, **save_kwargs)
            
            # Get optimized file info
            optimized_size_bytes = os.path.getsize(output_path)
            compression_ratio = (1 - optimized_size_bytes / original_size_bytes) * 100
            
            return {
                "original_path": None,  # Will be set by caller
                "optimized_path": output_path,
                "original_size": original_size,
                "optimized_size": image.size,
                "original_format": original_format,
                "optimized_format": settings['format'],
                "original_size_bytes": original_size_bytes,
                "optimized_size_bytes": optimized_size_bytes,
                "compression_ratio": round(compression_ratio, 2),
                "quality_level": settings['quality']
            }
            
        except Exception as e:
            raise Exception(f"Image processing failed: {str(e)}")
    
    async def _get_cached_image_info(self, cached_path: Path, original_path: str) -> Dict[str, Any]:
        """
        Get information about cached optimized image
        """
        try:
            stat = cached_path.stat()
            
            # Get original image info for comparison
            original_stat = os.stat(original_path)
            
            with Image.open(cached_path) as img:
                optimized_size = img.size
                optimized_format = img.format
            
            with Image.open(original_path) as img:
                original_size = img.size
                original_format = img.format
            
            compression_ratio = (1 - stat.st_size / original_stat.st_size) * 100
            
            return {
                "original_path": original_path,
                "optimized_path": str(cached_path),
                "original_size": original_size,
                "optimized_size": optimized_size,
                "original_format": original_format,
                "optimized_format": optimized_format,
                "original_size_bytes": original_stat.st_size,
                "optimized_size_bytes": stat.st_size,
                "compression_ratio": round(compression_ratio, 2),
                "cached": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cached image info: {str(e)}")
            return {"error": str(e)}
    
    def _generate_cache_key(self, image_path: str, optimization_level: str) -> str:
        """
        Generate cache key for optimized image
        """
        # Include file modification time and optimization level in hash
        try:
            stat = os.stat(image_path)
            key_data = f"{image_path}_{stat.st_mtime}_{optimization_level}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except:
            # Fallback to simple hash
            key_data = f"{image_path}_{optimization_level}"
            return hashlib.md5(key_data.encode()).hexdigest()
    
    async def cleanup_cache(self, max_age_days: int = 7) -> Dict[str, Any]:
        """
        Clean up old cached images
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            cleaned_files = []
            total_size_freed = 0
            
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                        total_size_freed += file_size
            
            return {
                "cleaned_files": len(cleaned_files),
                "total_size_freed_bytes": total_size_freed,
                "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {str(e)}")
            return {"error": str(e)}


# Global instance
image_optimization_service = ImageOptimizationService()
