import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Camera, 
  Monitor, 
  Smartphone, 
  Tablet, 
  ExternalLink, 
  Download,
  Eye,
  Maximize2,
  X
} from 'lucide-react'

const ScreenshotGallery = ({ visualAnalysis, brandName, websiteUrl }) => {
  const [selectedImage, setSelectedImage] = useState(null)
  const [imageError, setImageError] = useState({})

  // Extract screenshot data
  const getScreenshotData = () => {
    if (!visualAnalysis || !visualAnalysis.screenshots) {
      return null
    }

    const screenshots = visualAnalysis.screenshots
    return {
      screenshots,
      hasScreenshots: Object.keys(screenshots).length > 0,
      screenshotCount: Object.keys(screenshots).length
    }
  }

  const screenshotData = getScreenshotData()

  if (!screenshotData || !screenshotData.hasScreenshots) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5 text-gray-400" />
            Website Screenshots
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Camera className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No screenshots available</p>
            <p className="text-sm text-gray-400">
              Visual processing required for website screenshots
            </p>
            {websiteUrl && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-4"
                onClick={() => window.open(websiteUrl, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Visit Website
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  const getPageIcon = (pageName) => {
    switch (pageName.toLowerCase()) {
      case 'homepage':
        return <Monitor className="h-4 w-4" />
      case 'mobile':
        return <Smartphone className="h-4 w-4" />
      case 'tablet':
        return <Tablet className="h-4 w-4" />
      default:
        return <Eye className="h-4 w-4" />
    }
  }

  const getPageDisplayName = (pageName) => {
    return pageName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const handleImageError = (pageName) => {
    setImageError(prev => ({ ...prev, [pageName]: true }))
  }

  const handleImageLoad = (pageName) => {
    setImageError(prev => ({ ...prev, [pageName]: false }))
  }

  const openImageModal = (pageName, imageUrl) => {
    setSelectedImage({ pageName, imageUrl })
  }

  const closeImageModal = () => {
    setSelectedImage(null)
  }

  const downloadImage = (imageUrl, filename) => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5 text-green-600" />
            Website Screenshots
            {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="default" className="text-xs">
              <Eye className="h-3 w-3 mr-1" />
              {screenshotData.screenshotCount} Screenshots
            </Badge>
            {websiteUrl && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open(websiteUrl, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Visit Site
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(screenshotData.screenshots).map(([pageName, imageUrl]) => (
              <div key={pageName} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getPageIcon(pageName)}
                    <h4 className="font-medium text-gray-900">
                      {getPageDisplayName(pageName)}
                    </h4>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => downloadImage(imageUrl, `${brandName}-${pageName}.png`)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="group relative">
                  {imageError[pageName] ? (
                    <div className="w-full h-48 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                      <div className="text-center">
                        <Camera className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">Failed to load screenshot</p>
                      </div>
                    </div>
                  ) : (
                    <div className="relative overflow-hidden rounded-lg border shadow-sm hover:shadow-md transition-shadow">
                      <img 
                        src={imageUrl}
                        alt={`${getPageDisplayName(pageName)} screenshot`}
                        className="w-full h-48 object-cover object-top cursor-pointer hover:scale-105 transition-transform duration-200"
                        onError={() => handleImageError(pageName)}
                        onLoad={() => handleImageLoad(pageName)}
                        onClick={() => openImageModal(pageName, imageUrl)}
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100">
                        <Button variant="secondary" size="sm">
                          <Maximize2 className="h-4 w-4 mr-2" />
                          View Full Size
                        </Button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Captured automatically</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => downloadImage(imageUrl, `${brandName}-${pageName}.png`)}
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Download
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Screenshot Analysis Info */}
          <div className="mt-6 bg-green-50 p-4 rounded-lg">
            <h5 className="font-medium text-green-900 mb-2">Screenshot Analysis</h5>
            <div className="text-sm text-green-800 space-y-1">
              <p>✅ {screenshotData.screenshotCount} pages captured automatically</p>
              <p>📱 Full-page screenshots at 1920x1080 resolution</p>
              <p>🎨 Ready for color and visual element extraction</p>
              {websiteUrl && (
                <p>🔗 Source: <a href={websiteUrl} target="_blank" rel="noopener noreferrer" className="underline">{websiteUrl}</a></p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-6xl max-h-full">
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-4 right-4 z-10 bg-white hover:bg-gray-100"
              onClick={closeImageModal}
            >
              <X className="h-4 w-4" />
            </Button>
            <img 
              src={selectedImage.imageUrl}
              alt={`${getPageDisplayName(selectedImage.pageName)} full size`}
              className="max-w-full max-h-full object-contain rounded-lg"
            />
            <div className="absolute bottom-4 left-4 bg-white bg-opacity-90 px-3 py-2 rounded-lg">
              <p className="font-medium text-gray-900">
                {getPageDisplayName(selectedImage.pageName)}
              </p>
              <p className="text-sm text-gray-600">
                {brandName} - Website Screenshot
              </p>
            </div>
            <div className="absolute bottom-4 right-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => downloadImage(selectedImage.imageUrl, `${brandName}-${selectedImage.pageName}-full.png`)}
              >
                <Download className="h-4 w-4 mr-2" />
                Download Full Size
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ScreenshotGallery
