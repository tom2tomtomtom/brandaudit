import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Copy, Palette, Eye, BarChart3 } from 'lucide-react';

const ColorPalette = ({ colorData }) => {
  const [copiedColor, setCopiedColor] = useState(null);

  if (!colorData || colorData.error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Color Palette
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            {colorData?.error || 'Color analysis not available'}
          </p>
        </CardContent>
      </Card>
    );
  }

  const copyToClipboard = async (color) => {
    try {
      await navigator.clipboard.writeText(color.hex);
      setCopiedColor(color.hex);
      setTimeout(() => setCopiedColor(null), 2000);
    } catch (err) {
      console.error('Failed to copy color:', err);
    }
  };

  const ColorSwatch = ({ color, size = 'md' }) => {
    const sizeClasses = {
      sm: 'w-8 h-8',
      md: 'w-12 h-12',
      lg: 'w-16 h-16'
    };

    return (
      <div className="group cursor-pointer" onClick={() => copyToClipboard(color)}>
        <div className="space-y-2">
          <div 
            className={`${sizeClasses[size]} rounded-lg border-2 border-gray-200 shadow-sm group-hover:shadow-md transition-shadow relative overflow-hidden`}
            style={{ backgroundColor: color.hex }}
          >
            {copiedColor === color.hex && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <Copy className="h-4 w-4 text-white" />
              </div>
            )}
          </div>
          <div className="text-center space-y-1">
            <p className="text-sm font-medium">{color.name}</p>
            <p className="text-xs text-muted-foreground font-mono">{color.hex}</p>
            {color.consistency_score && (
              <Badge variant="outline" className="text-xs">
                {color.consistency_score}% consistent
              </Badge>
            )}
          </div>
        </div>
      </div>
    );
  };

  const ColorCategory = ({ title, colors, icon: Icon }) => (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4" />
        <h3 className="font-semibold">{title}</h3>
        <Badge variant="secondary">{colors.length}</Badge>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {colors.map((color, index) => (
          <ColorSwatch key={`${title}-${index}`} color={color} />
        ))}
      </div>
    </div>
  );

  const ColorInsights = ({ insights, consistency }) => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Color Consistency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress value={consistency?.overall_score || 0} className="h-2" />
              <p className="text-sm text-muted-foreground">
                {consistency?.overall_score || 0}% consistent across brand assets
              </p>
              {consistency?.consistency_details && (
                <div className="text-xs">
                  {consistency.consistency_details.highly_consistent && (
                    <Badge className="bg-green-100 text-green-800">Highly Consistent</Badge>
                  )}
                  {consistency.consistency_details.moderately_consistent && (
                    <Badge className="bg-yellow-100 text-yellow-800">Moderately Consistent</Badge>
                  )}
                  {consistency.consistency_details.low_consistency && (
                    <Badge className="bg-red-100 text-red-800">Low Consistency</Badge>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Color Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Total Colors:</span>
              <span className="font-medium">{insights?.total_unique_colors || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Temperature:</span>
              <Badge variant="outline" className="capitalize">
                {insights?.color_temperature?.temperature || 'neutral'}
              </Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span>Harmony:</span>
              <Badge variant="outline" className="capitalize">
                {insights?.color_harmony_type || 'unknown'}
              </Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span>Diversity Score:</span>
              <span className="font-medium">{insights?.color_diversity_score || 0}/100</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {consistency?.screenshots_analyzed > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Analysis Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Screenshots</p>
                <p className="font-medium">{consistency.screenshots_analyzed}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Unique Colors</p>
                <p className="font-medium">{consistency.unique_colors_count}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Consistent Colors</p>
                <p className="font-medium">{consistency.consistent_colors_count}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Color Instances</p>
                <p className="font-medium">{consistency.total_color_instances}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const swatches = colorData.color_swatches || [];
  const primaryColors = swatches.filter(s => s.category === 'primary');
  const secondaryColors = swatches.filter(s => s.category === 'secondary');
  const accentColors = swatches.filter(s => s.category === 'accent');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Brand Color Palette
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Click any color to copy its hex code
        </p>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="palette" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="palette" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Color Palette
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Insights
            </TabsTrigger>
          </TabsList>

          <TabsContent value="palette" className="space-y-6 mt-6">
            {primaryColors.length > 0 && (
              <ColorCategory 
                title="Primary Colors" 
                colors={primaryColors} 
                icon={Palette}
              />
            )}
            
            {secondaryColors.length > 0 && (
              <ColorCategory 
                title="Secondary Colors" 
                colors={secondaryColors} 
                icon={Eye}
              />
            )}
            
            {accentColors.length > 0 && (
              <ColorCategory 
                title="Accent Colors" 
                colors={accentColors} 
                icon={BarChart3}
              />
            )}

            {swatches.length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                No color swatches available
              </p>
            )}
          </TabsContent>

          <TabsContent value="insights" className="mt-6">
            <ColorInsights 
              insights={colorData.color_analysis} 
              consistency={colorData.color_consistency}
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default ColorPalette;
