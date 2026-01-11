"""PDF generator for tenant management reports.

Converts Markdown reports to PDF format using reportlab.
"""

from io import BytesIO
from typing import Optional
from dataclasses import dataclass
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


@dataclass
class PDFConfig:
    """Configuration for PDF generation."""

    page_size: tuple = A4
    margin: float = 2.0
    title_font_size: int = 18
    heading_font_size: int = 14
    body_font_size: int = 10


class PDFGenerator:
    """Generator for converting Markdown reports to PDF."""

    def __init__(self, config: PDFConfig = None):
        """Initialize PDF generator."""
        self._config = config or PDFConfig()
        self._styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Set up custom paragraph styles."""
        self._styles.add(ParagraphStyle(
            name='ReportTitle',
            fontSize=self._config.title_font_size,
            spaceAfter=20,
            alignment=1
        ))
        self._styles.add(ParagraphStyle(
            name='ReportHeading',
            fontSize=self._config.heading_font_size,
            spaceAfter=10,
            spaceBefore=15
        ))

    def generate(self, markdown_content: str, title: str = "Report") -> bytes:
        """Generate PDF from Markdown content."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self._config.page_size,
            leftMargin=self._config.margin * cm,
            rightMargin=self._config.margin * cm,
            topMargin=self._config.margin * cm,
            bottomMargin=self._config.margin * cm
        )
        elements = self._parse_markdown(markdown_content, title)
        doc.build(elements)
        return buffer.getvalue()

    def _parse_markdown(self, content: str, title: str) -> list:
        """Parse Markdown and convert to reportlab elements."""
        elements = []
        elements.append(Paragraph(title, self._styles['ReportTitle']))
        elements.append(Spacer(1, 0.5 * cm))
        lines = content.split('\n')
        table_lines = []
        in_table = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_table and table_lines:
                    elements.append(self._create_table(table_lines))
                    table_lines = []
                    in_table = False
                continue
            if line.startswith('|'):
                in_table = True
                table_lines.append(line)
                continue
            if in_table and table_lines:
                elements.append(self._create_table(table_lines))
                table_lines = []
                in_table = False
            if line.startswith('# '):
                elements.append(Paragraph(line[2:], self._styles['ReportTitle']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], self._styles['ReportHeading']))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], self._styles['Heading3']))
            elif line.startswith('- ') or line.startswith('* '):
                elements.append(Paragraph(f"• {line[2:]}", self._styles['Normal']))
            else:
                text = self._clean_markdown(line)
                elements.append(Paragraph(text, self._styles['Normal']))

        if in_table and table_lines:
            elements.append(self._create_table(table_lines))
        return elements

    def _clean_markdown(self, text: str) -> str:
        """Remove Markdown formatting."""
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        return text

    def _create_table(self, lines: list) -> Optional[Table]:
        """Create table from Markdown table lines."""
        if len(lines) < 2:
            return Spacer(1, 0.2 * cm)
        rows = []
        for line in lines:
            if '---' in line:
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells:
                rows.append(cells)
        if not rows:
            return Spacer(1, 0.2 * cm)
        table = Table(rows)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        return table

    def save_to_file(self, markdown_content: str, filepath: str, title: str = "Report") -> None:
        """Save PDF to file."""
        pdf_bytes = self.generate(markdown_content, title)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
