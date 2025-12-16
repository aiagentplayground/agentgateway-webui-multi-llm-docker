#!/bin/bash

# Script to generate slide images from presentation.md
# This script helps capture screenshots of each slide

echo "📸 Slide Image Generator for AgentGateway Presentation"
echo "======================================================"
echo ""
echo "This script will help you generate images for each slide."
echo ""
echo "Option 1: Manual Screenshots with Presenterm"
echo "---------------------------------------------"
echo "1. Install presenterm: brew install presenterm"
echo "2. Run: presenterm presentation.md"
echo "3. Navigate to each slide and take screenshots:"
echo "   - macOS: Cmd+Shift+4 (select window)"
echo "   - Linux: Use 'scrot' or 'gnome-screenshot'"
echo "4. Save screenshots to: docs/slides/"
echo "   - Name them: slide-01.png, slide-02.png, etc."
echo ""
echo "Option 2: Automated with terminal screenshot tool"
echo "-------------------------------------------------"
echo "Install 'termshot' or similar tool:"
echo "  npm install -g termshot"
echo ""
echo "Then run presenterm and capture each slide programmatically"
echo ""
echo "Option 3: Use this helper to extract slides"
echo "------------------------------------------"
echo "Extract individual slides from presentation.md for conversion:"

# Create individual slide files
SLIDE_DIR="docs/slides/markdown"
mkdir -p "$SLIDE_DIR"

# Extract slides from presentation.md
awk '
BEGIN { slide=0; in_slide=0 }
/^---$/ && NR > 5 { next }
/^<!-- end_slide -->/ { in_slide=0; next }
/^#/ && in_slide==0 {
    slide++;
    in_slide=1;
    file=sprintf("'"$SLIDE_DIR"'/slide-%02d.md", slide)
}
in_slide { print > file }
' ../presentation.md

echo ""
echo "✅ Individual slide markdown files created in: $SLIDE_DIR"
echo ""
echo "You can now convert these to images using tools like:"
echo "  - mdpdf (markdown to PDF)"
echo "  - carbon-now-cli (for code screenshots)"
echo "  - pandoc + wkhtmltopdf"
echo ""
echo "Recommended image size: 1200x675 (16:9 ratio)"
echo "Save final images to: docs/slides/ as PNG files"
