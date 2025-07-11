import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { ZoomIn, Download, Maximize2 } from 'lucide-react'

/**
 * Optimized Image Display Component with Progressive Loading
 * Implements lazy loading, progressive enhancement, and performance optimizations
 */
const OptimizedImageDisplay = ({ 
  src, 
  alt, 
  className = '', 
  sizes = 'medium',
  showControls = true,
  onLoad,
  onError,
  placeholder = true
}) => {
  const [imageState, setImageState] = useState({
    loading: true,
    error: false,
    loaded: false,
    currentSrc: null
  })
  
  const [isInView, setIsInView] = useState(false)
  const [showFullSize, setShowFullSize] = useState(false)
  const imgRef = useRef(null)
  const observerRef = useRef(null)

  // Progressive loading sources
  const getProgressiveSources = useCallback((baseSrc) => {
    if (!baseSrc) return {}
    
    const baseUrl = baseSrc.split('?')[0]
    const params = new URLSearchParams(baseSrc.split('?')[1] || '')
    
    return {
      thumbnail: `${baseUrl}?size=thumbnail&format=webp&${params.toString()}`,
      medium: `${baseUrl}?size=medium&format=webp&${params.toString()}`,
      large: `${baseUrl}?size=large&format=webp&${params.toString()}`,
      original: baseSrc
    }
  }, [])

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!imgRef.current) return

    observerRef.current = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observerRef.current?.disconnect()
        }
      },
      {
        rootMargin: '50px' // Start loading 50px before image comes into view
      }
    )

    observerRef.current.observe(imgRef.current)

    return () => {
      observerRef.current?.disconnect()
    }
  }, [])

  // Progressive image loading
  useEffect(() => {
    if (!isInView || !src) return

    const sources = getProgressiveSources(src)
    let isCancelled = false

    const loadImage = async () => {
      try {
        setImageState(prev => ({ ...prev, loading: true, error: false }))

        // Load thumbnail first for immediate feedback
        if (sources.thumbnail) {
          const thumbnailImg = new Image()
          thumbnailImg.onload = () => {
            if (!isCancelled) {
              setImageState(prev => ({ 
                ...prev, 
                currentSrc: sources.thumbnail,
                loaded: true 
              }))
            }
          }
          thumbnailImg.src = sources.thumbnail
        }

        // Then load the appropriate size
        const targetSrc = sources[sizes] || sources.medium || src
        const img = new Image()
        
        img.onload = () => {
          if (!isCancelled) {
            setImageState(prev => ({
              ...prev,
              loading: false,
              loaded: true,
              currentSrc: targetSrc
            }))
            onLoad?.(img)
          }
        }

        img.onerror = () => {
          if (!isCancelled) {
            setImageState(prev => ({
              ...prev,
              loading: false,
              error: true
            }))
            onError?.(new Error('Failed to load image'))
          }
        }

        img.src = targetSrc

      } catch (error) {
        if (!isCancelled) {
          setImageState(prev => ({
            ...prev,
            loading: false,
            error: true
          }))
          onError?.(error)
        }
      }
    }

    loadImage()

    return () => {
      isCancelled = true
    }
  }, [isInView, src, sizes, onLoad, onError, getProgressiveSources])

  const handleDownload = useCallback(async () => {
    if (!imageState.currentSrc) return

    try {
      const response = await fetch(imageState.currentSrc)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = alt || 'image'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }, [imageState.currentSrc, alt])

  const handleZoom = useCallback(() => {
    setShowFullSize(true)
  }, [])

  // Render loading placeholder
  if (!isInView || imageState.loading) {
    return (
      <div ref={imgRef} className={`relative ${className}`}>
        {placeholder && (
          <Skeleton className="w-full h-48 rounded-lg" />
        )}
        {imageState.currentSrc && (
          <img
            src={imageState.currentSrc}
            alt={alt}
            className={`absolute inset-0 w-full h-full object-cover rounded-lg transition-opacity duration-300 ${
              imageState.loading ? 'opacity-50' : 'opacity-100'
            }`}
          />
        )}
      </div>
    )
  }

  // Render error state
  if (imageState.error) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 rounded-lg p-8 ${className}`}>
        <div className="text-center">
          <div className="text-gray-400 mb-2">⚠️</div>
          <p className="text-sm text-gray-500">Failed to load image</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className={`relative group ${className}`}>
        <img
          ref={imgRef}
          src={imageState.currentSrc}
          alt={alt}
          className="w-full h-full object-cover rounded-lg transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
        
        {showControls && (
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 rounded-lg">
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={handleZoom}
                className="h-8 w-8 p-0"
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={handleDownload}
                className="h-8 w-8 p-0"
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Full-size modal */}
      {showFullSize && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setShowFullSize(false)}
        >
          <div className="relative max-w-full max-h-full">
            <img
              src={getProgressiveSources(src).original || imageState.currentSrc}
              alt={alt}
              className="max-w-full max-h-full object-contain"
            />
            <Button
              className="absolute top-4 right-4"
              variant="secondary"
              onClick={() => setShowFullSize(false)}
            >
              ✕
            </Button>
          </div>
        </div>
      )}
    </>
  )
}

/**
 * Image Gallery Component with Virtual Scrolling
 */
export const OptimizedImageGallery = ({ images, className = '' }) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 })
  const containerRef = useRef(null)

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return

      const container = containerRef.current
      const scrollTop = container.scrollTop
      const containerHeight = container.clientHeight
      const itemHeight = 200 // Approximate item height

      const start = Math.floor(scrollTop / itemHeight)
      const end = Math.min(images.length, start + Math.ceil(containerHeight / itemHeight) + 5)

      setVisibleRange({ start, end })
    }

    const container = containerRef.current
    if (container) {
      container.addEventListener('scroll', handleScroll)
      handleScroll() // Initial calculation
    }

    return () => {
      container?.removeEventListener('scroll', handleScroll)
    }
  }, [images.length])

  const visibleImages = images.slice(visibleRange.start, visibleRange.end)

  return (
    <div 
      ref={containerRef}
      className={`overflow-auto max-h-96 ${className}`}
    >
      <div style={{ height: images.length * 200 }}>
        <div 
          style={{ 
            transform: `translateY(${visibleRange.start * 200}px)`,
            position: 'relative'
          }}
        >
          {visibleImages.map((image, index) => (
            <div key={visibleRange.start + index} className="mb-4">
              <OptimizedImageDisplay
                src={image.src}
                alt={image.alt}
                className="h-48"
                sizes="medium"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default OptimizedImageDisplay
