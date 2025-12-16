# Presentation Slide Images

This directory contains images for the interactive presentation in the main README.

## Generating Slide Images

### Option 1: Manual Screenshots (Recommended)

1. **Install presenterm:**
   ```bash
   brew install presenterm
   ```

2. **Run the presentation:**
   ```bash
   cd /path/to/agentgateway-webui-multi-llm-docker
   presenterm presentation.md
   ```

3. **Capture screenshots:**
   - Navigate through slides using `n` (next) or `Space`
   - Take a screenshot of each slide:
     - **macOS:** `Cmd+Shift+4`, then press `Space`, click window
     - **Linux:** Use `gnome-screenshot` or `scrot`
     - **Windows:** Use Snipping Tool or `Win+Shift+S`

4. **Save images:**
   - Name them sequentially: `slide-01.png`, `slide-02.png`, ..., `slide-18.png`
   - Save to this directory (`docs/slides/`)
   - Recommended size: 1200x675 pixels (16:9 ratio)

### Option 2: Automated with Terminal Screenshot Tool

1. **Install termshot:**
   ```bash
   npm install -g termshot
   ```

2. **Run the helper script:**
   ```bash
   ./scripts/generate-slide-images.sh
   ```

3. **Follow the script instructions** to automate screenshot capture

### Option 3: Convert Markdown to Images

1. **Use carbon-now-cli** for beautiful code screenshots:
   ```bash
   npm install -g carbon-now-cli
   ```

2. **Extract slide markdown** using the helper script:
   ```bash
   ./scripts/generate-slide-images.sh
   ```
   This creates individual markdown files in `docs/slides/markdown/`

3. **Convert to images** using your preferred tool

## Image Requirements

- **Format:** PNG (preferred) or JPG
- **Size:** 1200x675 pixels (16:9 ratio) or similar
- **Quality:** High resolution for GitHub display
- **Naming:** `slide-01.png` through `slide-18.png`
- **Background:** Dark theme recommended for consistency

## Slide List

1. `slide-01.png` - What This Platform Provides
2. `slide-02.png` - Service Architecture
3. `slide-03.png` - Quick Start - Environment Setup
4. `slide-04.png` - Default Users & Access
5. `slide-05.png` - Available AI Models
6. `slide-06.png` - Manual Model Configuration - Step 1
7. `slide-07.png` - Manual Model Configuration - Step 2
8. `slide-08.png` - Manual Model Configuration - Step 3
9. `slide-09.png` - Manual Model Configuration - Step 4
10. `slide-10.png` - Manual Model Configuration - Step 5
11. `slide-11.png` - Manual Model Configuration - Step 6
12. `slide-12.png` - Automated Configuration
13. `slide-13.png` - Monitoring & Observability
14. `slide-14.png` - SSO with Keycloak
15. `slide-15.png` - Making API Calls
16. `slide-16.png` - Troubleshooting - Models Not Appearing
17. `slide-17.png` - Troubleshooting - Gateway Errors
18. `slide-18.png` - Security Considerations

## Tips

- Use a consistent terminal theme across all slides
- Ensure text is readable at thumbnail size
- Include the slide number or title for easy identification
- Test images on GitHub after uploading to verify display

## GitHub Display

Once images are added to this directory, they will automatically appear in the README's interactive presentation section when viewed on GitHub.
