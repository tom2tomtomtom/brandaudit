# Visual Reporting Specifications
## Comprehensive Visual Elements for Brand Audit Reports

### 🎨 **VISUAL ASSET REQUIREMENTS**

#### **1. Website Screenshots**
```python
# Screenshot Specifications
SCREENSHOT_CONFIG = {
    'desktop': {'width': 1920, 'height': 1080},
    'mobile': {'width': 375, 'height': 812},
    'tablet': {'width': 768, 'height': 1024},
    'format': 'PNG',
    'quality': 95,
    'full_page': True,
    'wait_for_load': 3000  # ms
}

# Capture Areas
CAPTURE_ZONES = [
    'homepage_hero',
    'navigation_header', 
    'footer',
    'about_page',
    'products_page',
    'contact_page'
]
```

#### **2. Brand Asset Extraction**
```python
# Color Analysis
COLOR_EXTRACTION = {
    'primary_colors': 3,      # Main brand colors
    'secondary_colors': 5,    # Supporting palette
    'accent_colors': 2,       # Highlight colors
    'format': 'HEX',
    'include_rgb': True,
    'color_names': True       # Human-readable names
}

# Logo Processing
LOGO_SPECS = {
    'formats': ['PNG', 'SVG', 'JPG'],
    'sizes': ['original', 'large', 'medium', 'small'],
    'background_removal': True,
    'variants': ['horizontal', 'vertical', 'icon'],
    'quality_check': True
}
```

#### **3. Typography Analysis**
```python
# Font Detection
TYPOGRAPHY_ANALYSIS = {
    'headings': ['h1', 'h2', 'h3'],
    'body_text': ['p', 'div', 'span'],
    'special_text': ['.hero', '.cta', '.quote'],
    'font_properties': [
        'font-family',
        'font-size', 
        'font-weight',
        'line-height',
        'letter-spacing'
    ]
}
```

---

### 📊 **CHART & VISUALIZATION SPECIFICATIONS**

#### **1. Brand Health Dashboard**
```javascript
// Key Metrics Visualization
const DASHBOARD_CHARTS = {
    overall_score: {
        type: 'radial_progress',
        colors: ['#ef4444', '#f59e0b', '#10b981'], // Red, Yellow, Green
        thresholds: [40, 70, 100]
    },
    competitive_matrix: {
        type: 'scatter_plot',
        axes: ['brand_strength', 'market_position'],
        bubble_size: 'market_share'
    },
    sentiment_trend: {
        type: 'line_chart',
        timeframe: '12_months',
        metrics: ['positive', 'neutral', 'negative']
    }
}
```

#### **2. Competitive Analysis Charts**
```javascript
// Visual Comparisons
const COMPETITIVE_VISUALS = {
    brand_comparison_table: {
        columns: ['Brand', 'Logo', 'Primary Colors', 'Score'],
        visual_elements: ['logo_thumbnail', 'color_swatches'],
        sorting: 'score_desc'
    },
    positioning_matrix: {
        type: '2x2_matrix',
        axes: ['innovation', 'tradition'],
        quadrants: ['Pioneers', 'Leaders', 'Followers', 'Niche']
    }
}
```

#### **3. Color Palette Displays**
```css
/* Color Swatch Styling */
.color-palette {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 12px;
}

.color-swatch {
    aspect-ratio: 1;
    border-radius: 8px;
    position: relative;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.color-info {
    position: absolute;
    bottom: -30px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 12px;
    font-weight: 500;
}
```

---

### 🖼️ **PRESENTATION TEMPLATE SPECIFICATIONS**

#### **1. Executive Summary Template**
```python
# Slide 1: Brand Overview
SLIDE_1_LAYOUT = {
    'title': 'Brand Audit Executive Summary',
    'brand_logo': {'position': 'top_right', 'size': 'medium'},
    'key_metrics': {
        'layout': '2x2_grid',
        'metrics': ['overall_score', 'visual_score', 'market_score', 'sentiment_score']
    },
    'screenshot': {'position': 'left_half', 'type': 'homepage'}
}

# Slide 2: Strategic Recommendations  
SLIDE_2_LAYOUT = {
    'title': 'Key Strategic Recommendations',
    'recommendations': {
        'format': 'numbered_list',
        'max_items': 5,
        'include_priority': True
    },
    'competitive_matrix': {'position': 'right_half'},
    'action_timeline': {'position': 'bottom'}
}
```

#### **2. Detailed Analysis Templates**
```python
# Brand Health Assessment
BRAND_HEALTH_TEMPLATE = {
    'visual_consistency': {
        'color_analysis': 'full_palette_display',
        'logo_variants': 'gallery_grid',
        'typography_samples': 'font_showcase'
    },
    'website_analysis': {
        'screenshots': 'before_after_comparison',
        'heatmap': 'user_attention_overlay',
        'mobile_responsive': 'device_comparison'
    }
}

# Competitive Landscape
COMPETITIVE_TEMPLATE = {
    'competitor_grid': {
        'layout': '3x2_grid',
        'elements': ['logo', 'screenshot', 'key_metrics'],
        'comparison_highlights': True
    },
    'positioning_map': {
        'type': 'interactive_scatter',
        'filters': ['industry', 'size', 'region']
    }
}
```

---

### 🎯 **VISUAL QUALITY STANDARDS**

#### **Image Quality Requirements**
- **Screenshots**: Minimum 1920x1080, PNG format, 95% quality
- **Logos**: Vector preferred (SVG), fallback to high-res PNG
- **Charts**: Minimum 300 DPI for print, responsive for web
- **Color Accuracy**: sRGB color space, calibrated extraction

#### **Accessibility Standards**
- **Color Contrast**: WCAG AA compliance (4.5:1 ratio minimum)
- **Alt Text**: Descriptive text for all visual elements
- **Font Sizes**: Minimum 12pt for body text, 16pt for headings
- **Color Blindness**: Patterns/textures in addition to color coding

#### **Brand Consistency**
- **Template Colors**: Professional blue/gray palette
- **Typography**: Clean, modern sans-serif fonts
- **Spacing**: Consistent margins and padding
- **Logo Usage**: Proper clear space and sizing

---

### 📱 **RESPONSIVE DESIGN SPECIFICATIONS**

#### **Desktop (1920px+)**
- Full-width layouts with sidebar navigation
- Large image galleries and detailed charts
- Multi-column content organization

#### **Tablet (768px - 1919px)**  
- Stacked layouts with collapsible sections
- Touch-friendly navigation elements
- Optimized image sizes for bandwidth

#### **Mobile (< 768px)**
- Single-column layouts
- Swipeable image carousels
- Condensed data tables with horizontal scroll

---

### 🔧 **IMPLEMENTATION TOOLS**

#### **Image Processing Stack**
```python
# Required Libraries
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from colorthief import ColorThief
from playwright.sync_api import sync_playwright
import webcolors
```

#### **Chart Generation**
```javascript
// Frontend Visualization
import { 
    BarChart, LineChart, ScatterChart, PieChart,
    ResponsiveContainer, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend
} from 'recharts'

// Custom Chart Components
import ColorPalette from './ColorPalette'
import BrandComparison from './BrandComparison'
import PositioningMatrix from './PositioningMatrix'
```

#### **Presentation Generation**
```python
# PowerPoint Generation
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# PDF Generation  
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
```

---

### ✅ **VISUAL DELIVERABLES CHECKLIST**

#### **Per Brand Analysis**
- [ ] Homepage screenshot (desktop + mobile)
- [ ] Logo extraction (all variants found)
- [ ] Color palette (5-8 colors with HEX codes)
- [ ] Typography samples (headings + body text)
- [ ] Key page screenshots (About, Products, Contact)
- [ ] Brand asset gallery
- [ ] Visual consistency score

#### **Per Competitor**
- [ ] Competitor screenshots
- [ ] Logo and color comparisons
- [ ] Side-by-side visual analysis
- [ ] Positioning matrix placement

#### **Final Presentation**
- [ ] Executive summary slides (2 slides)
- [ ] Detailed analysis slides (8-12 slides)
- [ ] Visual asset appendix
- [ ] Source attribution and methodology
- [ ] Downloadable PDF version
