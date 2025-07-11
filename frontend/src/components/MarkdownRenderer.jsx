import React from 'react'

const MarkdownRenderer = ({ content, className = "" }) => {
  if (!content) return null

  // Simple markdown parser for common formatting
  const parseMarkdown = (text) => {
    if (typeof text !== 'string') return text

    // Split by lines to handle different formatting
    const lines = text.split('\n')
    const elements = []
    let currentList = []
    let inList = false

    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      
      // Skip empty lines
      if (!trimmedLine) {
        if (inList && currentList.length > 0) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
          inList = false
        }
        elements.push(<br key={`br-${index}`} />)
        return
      }

      // Handle headers
      if (trimmedLine.startsWith('###')) {
        if (inList) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
          inList = false
        }
        elements.push(
          <h3 key={index} className="text-xl font-semibold text-gray-800 mt-6 mb-3">
            {formatInlineMarkdown(trimmedLine.replace(/^###\s*/, ''))}
          </h3>
        )
      } else if (trimmedLine.startsWith('##')) {
        if (inList) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
          inList = false
        }
        elements.push(
          <h2 key={index} className="text-2xl font-bold text-gray-900 mt-8 mb-4">
            {formatInlineMarkdown(trimmedLine.replace(/^##\s*/, ''))}
          </h2>
        )
      } else if (trimmedLine.startsWith('#')) {
        if (inList) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
          inList = false
        }
        elements.push(
          <h1 key={index} className="text-3xl font-bold text-gray-900 mt-8 mb-6">
            {formatInlineMarkdown(trimmedLine.replace(/^#\s*/, ''))}
          </h1>
        )
      }
      // Handle bullet points
      else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
        const listItem = trimmedLine.replace(/^[-*]\s*/, '')
        currentList.push(listItem)
        inList = true
      }
      // Handle numbered lists
      else if (/^\d+\.\s/.test(trimmedLine)) {
        if (inList && currentList.length > 0) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
        }
        const listItem = trimmedLine.replace(/^\d+\.\s*/, '')
        currentList.push(listItem)
        inList = true
      }
      // Regular paragraphs
      else {
        if (inList && currentList.length > 0) {
          elements.push(
            <ul key={`list-${index}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, i) => (
                <li key={i} className="text-gray-700 leading-relaxed">
                  {formatInlineMarkdown(item)}
                </li>
              ))}
            </ul>
          )
          currentList = []
          inList = false
        }
        elements.push(
          <p key={index} className="text-gray-700 leading-relaxed mb-4">
            {formatInlineMarkdown(trimmedLine)}
          </p>
        )
      }
    })

    // Handle any remaining list items
    if (inList && currentList.length > 0) {
      elements.push(
        <ul key="final-list" className="list-disc list-inside space-y-2 my-4 ml-4">
          {currentList.map((item, i) => (
            <li key={i} className="text-gray-700 leading-relaxed">
              {formatInlineMarkdown(item)}
            </li>
          ))}
        </ul>
      )
    }

    return elements
  }

  // Handle inline formatting like **bold** and *italic*
  const formatInlineMarkdown = (text) => {
    if (typeof text !== 'string') return text

    const parts = []
    let currentText = text
    let key = 0

    // Handle **bold** text
    while (currentText.includes('**')) {
      const startIndex = currentText.indexOf('**')
      const endIndex = currentText.indexOf('**', startIndex + 2)
      
      if (endIndex === -1) break
      
      // Add text before bold
      if (startIndex > 0) {
        parts.push(currentText.substring(0, startIndex))
      }
      
      // Add bold text
      const boldText = currentText.substring(startIndex + 2, endIndex)
      parts.push(
        <strong key={`bold-${key++}`} className="font-semibold text-gray-900">
          {boldText}
        </strong>
      )
      
      // Continue with remaining text
      currentText = currentText.substring(endIndex + 2)
    }
    
    // Add any remaining text
    if (currentText) {
      parts.push(currentText)
    }

    return parts.length > 1 ? parts : text
  }

  return (
    <div className={`prose prose-lg max-w-none ${className}`}>
      {parseMarkdown(content)}
    </div>
  )
}

export default MarkdownRenderer
