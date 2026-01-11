# Research: AI Query Visualization

This document captures the research process and findings for implementing data visualization capabilities in AI query responses.

---

## Table of Contents

- [Research Objective](#research-objective)
- [Problem Statement](#problem-statement)
- [Research Methodology](#research-methodology)
- [Technology Evaluation](#technology-evaluation)
- [Architecture Options](#architecture-options)
- [Proof of Concept](#proof-of-concept)
- [Recommendations](#recommendations)
- [Next Steps](#next-steps)

---

## Research Objective

**Goal:** Enable the AI query system to generate data visualizations (charts, graphs, plots) alongside textual reports.

**Success Criteria:**
1. Generate charts from tenant data queries
2. Embed visualizations in Markdown reports
3. Support PDF export with embedded charts
4. Maintain response time under 5 seconds

---

## Problem Statement

### Current State

The AI report agent generates Markdown text reports:

```markdown
# Occupancy Report - Building 11

| Metric | Value |
|--------|-------|
| Total Apartments | 40 |
| Occupied | 34 |
| Vacant | 6 |
| Occupancy Rate | 85% |
```

### Desired State

Reports include visual representations:

```markdown
# Occupancy Report - Building 11

## Occupancy by Building

![Occupancy Chart](data:image/png;base64,...)

| Building | Occupied | Vacant | Rate |
|----------|----------|--------|------|
| 11 | 34 | 6 | 85% |
| 13 | 32 | 3 | 91% |
| 15 | 36 | 4 | 90% |
| 17 | 30 | 5 | 86% |
```

### Visualization Types Needed

1. **Bar Charts** - Occupancy comparison across buildings
2. **Pie Charts** - Owner vs renter distribution
3. **Line Charts** - Move-in/move-out trends over time
4. **Stacked Bar** - Multi-metric comparisons
5. **Heatmaps** - Floor-by-floor occupancy visualization

---

## Research Methodology

### Phase 1: Library Evaluation

Evaluated Python visualization libraries:

| Library | Pros | Cons | Rating |
|---------|------|------|--------|
| **Matplotlib** | Mature, extensive, static images | Verbose API, steep learning curve | 7/10 |
| **Plotly** | Interactive, modern, easy API | Large bundle size, complexity | 8/10 |
| **Altair** | Declarative, clean syntax | Limited customization | 7/10 |
| **Seaborn** | Statistical charts, beautiful defaults | Built on matplotlib | 7/10 |
| **Bokeh** | Interactive, web-native | Server required for interaction | 6/10 |

### Phase 2: Integration Patterns

Researched patterns for AI + visualization:

1. **Post-processing Pattern**
   - AI generates data/instructions
   - Separate service creates charts
   - Combine in final report

2. **Prompt-Guided Pattern**
   - AI describes desired visualization
   - Template system interprets
   - Library generates chart

3. **Hybrid Pattern**
   - AI generates report with chart specifications
   - Renderer creates visuals and embeds
   - Best of both approaches

### Phase 3: Output Format Research

| Format | Use Case | Size | Quality |
|--------|----------|------|---------|
| PNG | Web display, PDF embed | Medium | Good |
| SVG | Scalable, editable | Small | Excellent |
| Base64 | Inline embedding | Large | Good |
| HTML Canvas | Interactive web | N/A | Excellent |

---

## Technology Evaluation

### Matplotlib (Recommended for MVP)

**Strengths:**
- No additional dependencies (already common)
- Reliable static image generation
- Extensive customization options
- Easy base64 encoding for embedding

**Sample Implementation:**

```python
import matplotlib.pyplot as plt
import io
import base64

def create_occupancy_chart(data: dict) -> str:
    """Create occupancy bar chart and return base64 encoded image."""
    buildings = list(data.keys())
    occupied = [d['occupied'] for d in data.values()]
    vacant = [d['vacant'] for d in data.values()]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(buildings))
    width = 0.35

    ax.bar([i - width/2 for i in x], occupied, width, label='Occupied', color='#4CAF50')
    ax.bar([i + width/2 for i in x], vacant, width, label='Vacant', color='#FF5722')

    ax.set_xlabel('Building')
    ax.set_ylabel('Apartments')
    ax.set_title('Occupancy by Building')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Building {b}' for b in buildings])
    ax.legend()

    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return f"data:image/png;base64,{image_base64}"
```

### Plotly (Recommended for Interactive)

**Strengths:**
- Interactive charts (zoom, hover, pan)
- Modern visual style
- Easy JSON serialization
- React integration available

**Sample Implementation:**

```python
import plotly.graph_objects as go
import plotly.io as pio

def create_interactive_occupancy(data: dict) -> str:
    """Create interactive plotly chart."""
    buildings = list(data.keys())

    fig = go.Figure(data=[
        go.Bar(name='Occupied', x=buildings, y=[d['occupied'] for d in data.values()]),
        go.Bar(name='Vacant', x=buildings, y=[d['vacant'] for d in data.values()])
    ])

    fig.update_layout(
        barmode='group',
        title='Occupancy by Building',
        xaxis_title='Building',
        yaxis_title='Apartments'
    )

    # Return as HTML div for embedding
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
```

---

## Architecture Options

### Option A: Server-Side Rendering (Recommended)

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                           │
│         "Show occupancy with charts"                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   MCP Server                            │
│                                                         │
│   ┌─────────────┐    ┌──────────────────┐             │
│   │ AI Agent    │───▶│ Chart Generator  │             │
│   │ (Text)      │    │ (Matplotlib)     │             │
│   └─────────────┘    └──────────────────┘             │
│         │                    │                         │
│         ▼                    ▼                         │
│   ┌─────────────────────────────────────┐             │
│   │     Report Composer                  │             │
│   │  (Markdown + Embedded Charts)        │             │
│   └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              React UI (Display)                         │
│         Rendered Markdown + Images                      │
└─────────────────────────────────────────────────────────┘
```

**Pros:**
- Consistent rendering across clients
- No client-side dependencies
- Easy PDF export with charts

**Cons:**
- Increased server load
- Static images (no interaction)

### Option B: Client-Side Rendering

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Server                            │
│   ┌─────────────────────────────────────┐             │
│   │      AI Agent returns:               │             │
│   │      - Markdown text                 │             │
│   │      - Chart specifications (JSON)   │             │
│   └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              React UI                                   │
│   ┌─────────────┐    ┌──────────────────┐             │
│   │ Markdown    │    │ Chart Component  │             │
│   │ Renderer    │    │ (Recharts/Plotly)│             │
│   └─────────────┘    └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

**Pros:**
- Interactive charts
- Reduced server load
- Smaller response payload

**Cons:**
- Client-side dependencies
- PDF export more complex
- Inconsistent rendering

### Option C: Hybrid (Future Enhancement)

- Server generates static charts for reports/PDF
- Client enhances with interactive versions
- Best of both worlds

---

## Proof of Concept

### Implemented Prototype

**File:** `src/ai_agent/visualizations.py` (proposed)

```python
"""Chart generation module for AI reports."""

import io
import base64
from typing import Any

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


class ChartGenerator:
    """Generate charts for tenant data visualization."""

    def __init__(self):
        """Initialize chart generator with default style."""
        plt.style.use('seaborn-v0_8-whitegrid')
        self._colors = {
            'primary': '#1976D2',
            'secondary': '#388E3C',
            'accent': '#F57C00',
            'error': '#D32F2F',
            'neutral': '#757575'
        }

    def create_occupancy_bar(self, data: dict[int, dict]) -> str:
        """Create occupancy bar chart.

        Args:
            data: Dict of building_number -> {'occupied': int, 'vacant': int}

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        buildings = [f"Bldg {b}" for b in sorted(data.keys())]
        occupied = [data[b]['occupied'] for b in sorted(data.keys())]
        vacant = [data[b]['vacant'] for b in sorted(data.keys())]

        x = range(len(buildings))
        width = 0.35

        bars1 = ax.bar([i - width/2 for i in x], occupied, width,
                       label='Occupied', color=self._colors['secondary'])
        bars2 = ax.bar([i + width/2 for i in x], vacant, width,
                       label='Vacant', color=self._colors['error'])

        ax.set_xlabel('Building', fontsize=12)
        ax.set_ylabel('Apartments', fontsize=12)
        ax.set_title('Occupancy by Building', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(buildings)
        ax.legend()

        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)

        return self._to_base64(fig)

    def create_pie_chart(self, data: dict[str, int], title: str) -> str:
        """Create pie chart for distribution data.

        Args:
            data: Dict of category -> count
            title: Chart title

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        labels = list(data.keys())
        sizes = list(data.values())
        colors = [self._colors['primary'], self._colors['secondary'],
                  self._colors['accent'], self._colors['neutral']][:len(labels)]

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=colors, explode=[0.02] * len(labels))
        ax.set_title(title, fontsize=14, fontweight='bold')

        return self._to_base64(fig)

    def create_trend_line(self, dates: list, values: list,
                          title: str, ylabel: str) -> str:
        """Create trend line chart.

        Args:
            dates: List of date strings
            values: List of corresponding values
            title: Chart title
            ylabel: Y-axis label

        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(dates, values, marker='o', linewidth=2,
                color=self._colors['primary'], markersize=8)
        ax.fill_between(dates, values, alpha=0.3, color=self._colors['primary'])

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return self._to_base64(fig)

    def _to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"
```

### Integration with ReportAgent

```python
# Proposed modification to src/ai_agent/reporter.py

class ReportAgent:
    def __init__(self, ...):
        # ... existing init ...
        self._chart_gen = ChartGenerator()

    def generate_occupancy_report(self, building: int = None) -> ReportResult:
        # Get occupancy data
        response = self._client.get_resource("/occupancy")
        occupancy_data = response.data

        # Generate text report via AI
        # ... existing AI call ...

        # Generate chart
        chart_data = {
            b['building']: {'occupied': b['occupied'], 'vacant': b['vacant']}
            for b in occupancy_data['buildings']
        }
        chart_base64 = self._chart_gen.create_occupancy_bar(chart_data)

        # Embed chart in markdown
        content_with_chart = f"""
{ai_content}

## Visualization

![Occupancy Chart]({chart_base64})
"""

        return ReportResult(content=content_with_chart)
```

---

## Recommendations

### Immediate Implementation (MVP)

1. **Use Matplotlib** for server-side chart generation
2. **Base64 encode** images for Markdown embedding
3. **Start with 3 chart types:**
   - Occupancy bar chart
   - Owner/renter pie chart
   - Monthly trend line

### Phase 2 (Interactive)

1. Add Plotly for interactive web charts
2. Implement chart specification JSON format
3. Create React chart components
4. Enable chart customization

### Phase 3 (Advanced)

1. Real-time dashboard charts
2. Drill-down capabilities
3. Export to various formats
4. Custom chart templates

---

## Next Steps

1. **Week 1:** Create `ChartGenerator` class with matplotlib
2. **Week 2:** Integrate with `ReportAgent`
3. **Week 3:** Add React rendering for base64 images
4. **Week 4:** PDF export with charts
5. **Week 5:** Testing and optimization

### Dependencies to Add

```txt
# requirements.txt additions
matplotlib>=3.7.0
```

### Configuration

```yaml
# config.yaml additions
visualization:
  enabled: true
  default_style: "seaborn-v0_8-whitegrid"
  dpi: 100
  chart_width: 10
  chart_height: 6
  colors:
    primary: "#1976D2"
    secondary: "#388E3C"
    accent: "#F57C00"
```

---

## Research References

1. Matplotlib Documentation: https://matplotlib.org/stable/
2. Plotly Python: https://plotly.com/python/
3. Base64 Image Embedding: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
4. React Markdown with Images: https://github.com/remarkjs/react-markdown

---

**Research Conducted By:** Development Team
**Date:** 2026-01-11
**Status:** Research Complete, Ready for Implementation
