import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Presentation, 
  Globe, 
  Download, 
  Settings, 
  Palette,
  BarChart3,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

const ReportGenerator = ({ analysisResults, brandName, onReportGenerated }) => {
  const [selectedTemplate, setSelectedTemplate] = useState('detailed_analysis');
  const [selectedTheme, setSelectedTheme] = useState('corporate_blue');
  const [selectedFormats, setSelectedFormats] = useState(['pdf']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generatedReports, setGeneratedReports] = useState([]);
  const [error, setError] = useState(null);

  const templates = [
    {
      id: 'executive_summary',
      name: 'Executive Summary',
      description: 'Concise overview for C-suite presentation',
      icon: BarChart3,
      pages: '3-5 pages',
      audience: 'Executives'
    },
    {
      id: 'detailed_analysis',
      name: 'Detailed Analysis',
      description: 'Comprehensive brand audit report',
      icon: FileText,
      pages: '15-20 pages',
      audience: 'Marketing Teams'
    },
    {
      id: 'presentation_deck',
      name: 'Presentation Deck',
      description: 'Slide-based presentation format',
      icon: Presentation,
      pages: '10-15 slides',
      audience: 'Stakeholders'
    },
    {
      id: 'consulting_report',
      name: 'Consulting Report',
      description: 'Professional consulting-style analysis',
      icon: FileText,
      pages: '20-25 pages',
      audience: 'Board Members'
    },
    {
      id: 'strategic_brief',
      name: 'Strategic Brief',
      description: 'Action-focused strategic document',
      icon: BarChart3,
      pages: '5-8 pages',
      audience: 'Strategy Teams'
    }
  ];

  const themes = [
    {
      id: 'corporate_blue',
      name: 'Corporate Blue',
      description: 'Professional blue theme',
      colors: ['#1f4e79', '#2e5984', '#4472a8']
    },
    {
      id: 'modern_minimal',
      name: 'Modern Minimal',
      description: 'Clean and contemporary',
      colors: ['#2c3e50', '#34495e', '#3498db']
    },
    {
      id: 'consulting_premium',
      name: 'Consulting Premium',
      description: 'High-end consulting style',
      colors: ['#0f1419', '#1a2332', '#00a8cc']
    },
    {
      id: 'brand_focused',
      name: 'Brand Focused',
      description: 'Warm and approachable',
      colors: ['#8b5a3c', '#a0522d', '#cd853f']
    },
    {
      id: 'executive_dark',
      name: 'Executive Dark',
      description: 'Sophisticated dark theme',
      colors: ['#1a1a1a', '#333333', '#ff6b35']
    }
  ];

  const formats = [
    {
      id: 'pdf',
      name: 'PDF Report',
      description: 'Professional PDF document',
      icon: FileText,
      extension: '.pdf'
    },
    {
      id: 'pptx',
      name: 'PowerPoint',
      description: 'Editable presentation slides',
      icon: Presentation,
      extension: '.pptx'
    },
    {
      id: 'html',
      name: 'Interactive HTML',
      description: 'Web-based interactive report',
      icon: Globe,
      extension: '.html'
    }
  ];

  const handleFormatChange = (formatId, checked) => {
    if (checked) {
      setSelectedFormats([...selectedFormats, formatId]);
    } else {
      setSelectedFormats(selectedFormats.filter(f => f !== formatId));
    }
  };

  const generateReports = async () => {
    if (selectedFormats.length === 0) {
      setError('Please select at least one export format');
      return;
    }

    setIsGenerating(true);
    setGenerationProgress(0);
    setError(null);
    setGeneratedReports([]);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const response = await fetch('/api/brand-audit/report/generate-professional', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          brand_name: brandName,
          analysis_data: analysisResults,
          template: selectedTemplate,
          theme: selectedTheme,
          export_formats: selectedFormats
        })
      });

      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (!response.ok) {
        throw new Error('Failed to generate reports');
      }

      const result = await response.json();
      
      if (result.success) {
        setGeneratedReports(result.reports_generated || {});
        if (onReportGenerated) {
          onReportGenerated(result);
        }
      } else {
        throw new Error(result.error || 'Report generation failed');
      }

    } catch (err) {
      setError(err.message);
      setGenerationProgress(0);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadReport = (reportData, format) => {
    if (reportData.download_url) {
      window.open(reportData.download_url, '_blank');
    }
  };

  const selectedTemplateData = templates.find(t => t.id === selectedTemplate);
  const selectedThemeData = themes.find(t => t.id === selectedTheme);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Professional Report Generator</h2>
          <p className="text-gray-600">Create client-ready brand audit reports with professional templates</p>
        </div>
        <Badge variant="outline" className="text-lg px-3 py-1">
          {brandName}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Template Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Report Template
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
              <SelectTrigger>
                <SelectValue placeholder="Select template" />
              </SelectTrigger>
              <SelectContent>
                {templates.map(template => (
                  <SelectItem key={template.id} value={template.id}>
                    <div className="flex items-center gap-2">
                      <template.icon className="h-4 w-4" />
                      {template.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {selectedTemplateData && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-sm">{selectedTemplateData.name}</h4>
                <p className="text-xs text-gray-600 mt-1">{selectedTemplateData.description}</p>
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>{selectedTemplateData.pages}</span>
                  <span>{selectedTemplateData.audience}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Theme Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Visual Theme
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select value={selectedTheme} onValueChange={setSelectedTheme}>
              <SelectTrigger>
                <SelectValue placeholder="Select theme" />
              </SelectTrigger>
              <SelectContent>
                {themes.map(theme => (
                  <SelectItem key={theme.id} value={theme.id}>
                    {theme.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {selectedThemeData && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-sm">{selectedThemeData.name}</h4>
                <p className="text-xs text-gray-600 mt-1">{selectedThemeData.description}</p>
                <div className="flex gap-1 mt-2">
                  {selectedThemeData.colors.map((color, index) => (
                    <div
                      key={index}
                      className="w-4 h-4 rounded-full border border-gray-300"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Export Formats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Export Formats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {formats.map(format => (
              <div key={format.id} className="flex items-center space-x-2">
                <Checkbox
                  id={format.id}
                  checked={selectedFormats.includes(format.id)}
                  onCheckedChange={(checked) => handleFormatChange(format.id, checked)}
                />
                <div className="flex items-center gap-2 flex-1">
                  <format.icon className="h-4 w-4" />
                  <div>
                    <label htmlFor={format.id} className="text-sm font-medium cursor-pointer">
                      {format.name}
                    </label>
                    <p className="text-xs text-gray-600">{format.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Generation Controls */}
      <Card>
        <CardContent className="pt-6">
          {error && (
            <div className="flex items-center gap-2 text-red-600 mb-4">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          
          {isGenerating && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Generating reports...</span>
                <span className="text-sm text-gray-600">{generationProgress}%</span>
              </div>
              <Progress value={generationProgress} className="w-full" />
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
            </div>
            <Button 
              onClick={generateReports} 
              disabled={isGenerating || selectedFormats.length === 0}
              className="flex items-center gap-2"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              Generate Reports
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generated Reports */}
      {Object.keys(generatedReports).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Generated Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(generatedReports).map(([format, reportData]) => {
                const formatInfo = formats.find(f => f.id === format || format.includes(f.id));
                return (
                  <div key={format} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      {formatInfo && <formatInfo.icon className="h-5 w-5" />}
                      <div>
                        <div className="font-medium">{reportData.filename}</div>
                        <div className="text-sm text-gray-600">
                          {reportData.file_size ? `${Math.round(reportData.file_size / 1024)} KB` : 'Ready'}
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => downloadReport(reportData, format)}
                      className="flex items-center gap-2"
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ReportGenerator;
