import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Camera, 
  Download, 
  ExternalLink, 
  Monitor, 
  Smartphone, 
  Tablet,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  X,
  Grid3X3,
  Eye,
  Layers,
  Target,
  Palette,
  Type,
  Layout,
  ChevronLeft,
  ChevronRight,
  Info,
  Star,
  Award,
  TrendingUp
} from 'lucide-react'

const EnhancedVisualGallery = ({ visualAnalysis, brandName, websiteUrl }) => {
  const [selectedImage, setSelectedImage] = useState(null)
  const [imageError, setImageError] = useState({})
  const [zoomLevel, setZoomLevel] = useState(1)
  const [showAnnotations, setShowAnnotations] = useState(true)
  const [viewMode, setViewMode] = useState('grid') // 'grid', 'carousel', 'comparison'
  const [selectedDeviceType, setSelectedDeviceType] = useState('all')
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const imageRef = useRef(null)

  // Extract comprehensive screenshot data
  const getVisualAssets = () => {
    if (!visualAnalysis) return null

    const screenshots = visualAnalysis.screenshots || {}
    const logos = visualAnalysis.logos || []
    const brandAssets = visualAnalysis.brand_assets || {}
    const visualScores = visualAnalysis.visual_scores || {}

    // Organize screenshots by device type
    const organizedScreenshots = {
      desktop: {},
      mobile: {},
      tablet: {},
      elements: {}
    }

    Object.entries(screenshots).forEach(([key, url]) => {
      if (key.includes('desktop')) {
        organizedScreenshots.desktop[key] = url
      } else if (key.includes('mobile')) {
        organizedScreenshots.mobile[key] = url
      } else if (key.includes('tablet')) {
        organizedScreenshots.tablet[key] = url
      } else if (key.includes('element') || key.includes('logo') || key.includes('header')) {
        organizedScreenshots.elements[key] = url
      } else {
        organizedScreenshots.desktop[key] = url // Default to desktop
      }
    })

    return {
      screenshots: organizedScreenshots,
      logos,
      brandAssets,
      visualScores,
      hasScreenshots: Object.keys(screenshots).length > 0,
      totalAssets: Object.keys(screenshots).length + logos.length
    }
  }

  const visualAssets = getVisualAssets()

  // Get all images for carousel mode
  const getAllImages = () => {
    if (!visualAssets) return []
    
    const images = []
    
    // Add screenshots
    Object.entries(visualAssets.screenshots).forEach(([deviceType, screenshots]) => {
      if (selectedDeviceType === 'all' || selectedDeviceType === deviceType) {
        Object.entries(screenshots).forEach(([key, url]) => {
          images.push({
            type: 'screenshot',
            deviceType,
            key,
            url,
            title: getScreenshotTitle(key, deviceType),
            annotations: getScreenshotAnnotations(key, deviceType)
          })
        })
      }
    })

    // Add logos
    visualAssets.logos.forEach((logo, index) => {
      if (logo.extracted_path) {
        images.push({
          type: 'logo',
          key: `logo_${index}`,
          url: logo.extracted_path,
          title: `Logo Detection ${index + 1}`,
          quality: logo.quality_score,
          method: logo.detection_method,
          annotations: getLogoAnnotations(logo)
        })
      }
    })

    return images
  }

  const allImages = getAllImages()

  const getScreenshotTitle = (key, deviceType) => {
    const titles = {
      homepage: 'Homepage',
      about: 'About Page',
      products: 'Products',
      contact: 'Contact',
      services: 'Services'
    }
    
    const baseName = key.replace(`_${deviceType}`, '').replace('_desktop', '').replace('_mobile', '')
    return titles[baseName] || baseName.charAt(0).toUpperCase() + baseName.slice(1)
  }

  const getScreenshotAnnotations = (key, deviceType) => {
    const annotations = []
    
    if (deviceType === 'desktop') {
      annotations.push({ type: 'device', text: 'Desktop View', icon: Monitor })
    } else if (deviceType === 'mobile') {
      annotations.push({ type: 'device', text: 'Mobile View', icon: Smartphone })
    }
    
    if (key.includes('homepage')) {
      annotations.push({ type: 'page', text: 'Primary Landing', icon: Target })
    }
    
    return annotations
  }

  const getLogoAnnotations = (logo) => {
    const annotations = []
    
    if (logo.quality_score) {
      annotations.push({ 
        type: 'quality', 
        text: `Quality: ${Math.round(logo.quality_score * 100)}%`, 
        icon: Award 
      })
    }
    
    if (logo.detection_method) {
      annotations.push({ 
        type: 'method', 
        text: logo.detection_method.replace('_', ' '), 
        icon: Eye 
      })
    }
    
    return annotations
  }

  const handleImageError = (key) => {
    setImageError(prev => ({ ...prev, [key]: true }))
  }

  const handleImageLoad = (key) => {
    setImageError(prev => ({ ...prev, [key]: false }))
  }

  const openImageModal = (image, index = 0) => {
    setSelectedImage(image)
    setCurrentImageIndex(index)
    setZoomLevel(1)
  }

  const closeImageModal = () => {
    setSelectedImage(null)
    setZoomLevel(1)
  }

  const navigateImage = (direction) => {
    const newIndex = direction === 'next' 
      ? (currentImageIndex + 1) % allImages.length
      : (currentImageIndex - 1 + allImages.length) % allImages.length
    
    setCurrentImageIndex(newIndex)
    setSelectedImage(allImages[newIndex])
    setZoomLevel(1)
  }

  const handleZoom = (direction) => {
    setZoomLevel(prev => {
      const newZoom = direction === 'in' ? prev * 1.2 : prev / 1.2
      return Math.max(0.5, Math.min(3, newZoom))
    })
  }

  const downloadImage = (url, filename) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  if (!visualAssets || !visualAssets.hasScreenshots) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5 text-gray-400" />
            Visual Asset Gallery
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Camera className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No visual assets available</p>
            <p className="text-sm text-gray-400">
              Visual processing required for screenshots and brand asset detection
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Gallery Header with Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-blue-600" />
              Visual Asset Gallery
              {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="text-sm">
                <Camera className="h-3 w-3 mr-1" />
                {visualAssets.totalAssets} Assets
              </Badge>
              {visualAssets.visualScores.overall_visual_score && (
                <Badge variant="secondary" className="text-sm">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Score: {Math.round(visualAssets.visualScores.overall_visual_score)}
                </Badge>
              )}
            </div>
          </div>
          
          {/* View Controls */}
          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3X3 className="h-4 w-4 mr-1" />
                Grid
              </Button>
              <Button
                variant={viewMode === 'carousel' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('carousel')}
              >
                <Layout className="h-4 w-4 mr-1" />
                Carousel
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <select
                value={selectedDeviceType}
                onChange={(e) => setSelectedDeviceType(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="all">All Devices</option>
                <option value="desktop">Desktop Only</option>
                <option value="mobile">Mobile Only</option>
                <option value="elements">Elements Only</option>
              </select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAnnotations(!showAnnotations)}
              >
                <Eye className="h-4 w-4 mr-1" />
                {showAnnotations ? 'Hide' : 'Show'} Info
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Gallery Content */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allImages.map((image, index) => (
            <Card key={image.key} className="group hover:shadow-lg transition-shadow">
              <CardContent className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 flex items-center gap-2">
                      {image.type === 'screenshot' ? (
                        image.deviceType === 'mobile' ? <Smartphone className="h-4 w-4" /> : <Monitor className="h-4 w-4" />
                      ) : (
                        <Target className="h-4 w-4" />
                      )}
                      {image.title}
                    </h4>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => downloadImage(image.url, `${brandName}-${image.key}.png`)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="relative">
                    {imageError[image.key] ? (
                      <div className="w-full h-48 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                        <div className="text-center">
                          <Camera className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-500">Failed to load asset</p>
                        </div>
                      </div>
                    ) : (
                      <div className="relative overflow-hidden rounded-lg border shadow-sm hover:shadow-md transition-shadow">
                        <img 
                          src={image.url}
                          alt={image.title}
                          className="w-full h-48 object-cover object-top cursor-pointer hover:scale-105 transition-transform duration-200"
                          onError={() => handleImageError(image.key)}
                          onLoad={() => handleImageLoad(image.key)}
                          onClick={() => openImageModal(image, index)}
                        />
                        
                        {/* Overlay with zoom icon */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                          <Maximize2 className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Annotations */}
                  {showAnnotations && image.annotations && (
                    <div className="flex flex-wrap gap-1">
                      {image.annotations.map((annotation, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          <annotation.icon className="h-3 w-3 mr-1" />
                          {annotation.text}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative max-w-7xl max-h-full">
            {/* Modal Header */}
            <div className="absolute top-4 left-4 right-4 flex items-center justify-between z-10">
              <div className="flex items-center gap-2 bg-black bg-opacity-50 rounded-lg px-3 py-2">
                <h3 className="text-white font-medium">{selectedImage.title}</h3>
                <Badge variant="secondary" className="text-xs">
                  {currentImageIndex + 1} of {allImages.length}
                </Badge>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleZoom('out')}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleZoom('in')}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setZoomLevel(1)}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={closeImageModal}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Navigation Arrows */}
            {allImages.length > 1 && (
              <>
                <Button
                  variant="ghost"
                  size="lg"
                  onClick={() => navigateImage('prev')}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 text-white hover:bg-white hover:bg-opacity-20 z-10"
                >
                  <ChevronLeft className="h-8 w-8" />
                </Button>
                <Button
                  variant="ghost"
                  size="lg"
                  onClick={() => navigateImage('next')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-white hover:bg-white hover:bg-opacity-20 z-10"
                >
                  <ChevronRight className="h-8 w-8" />
                </Button>
              </>
            )}
            
            {/* Image */}
            <img
              ref={imageRef}
              src={selectedImage.url}
              alt={selectedImage.title}
              className="max-w-full max-h-full object-contain transition-transform duration-200"
              style={{ transform: `scale(${zoomLevel})` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default EnhancedVisualGallery
