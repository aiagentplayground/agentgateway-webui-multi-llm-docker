# Presentation Guide

This repository includes a terminal-based presentation created with [Presenterm](https://github.com/mfontanini/presenterm).

## Installing Presenterm

### macOS (Homebrew)
```bash
brew install presenterm
```

### Linux/Other
```bash
cargo install presenterm
```

## Running the Presentation

```bash
# From the repository root
presenterm presentation.md

# Or with specific theme
presenterm --theme dark presentation.md
```

## Navigation

- **Next slide:** `n`, `Space`, `→`, `Page Down`
- **Previous slide:** `p`, `←`, `Page Up`
- **First slide:** `gg` or `Home`
- **Last slide:** `G` or `End`
- **Quit:** `q` or `Ctrl+C`
- **Toggle slide index:** `Ctrl+P`

## Presentation Contents

The presentation covers:

1. **Platform Overview** - Architecture and features
2. **Quick Start** - Getting up and running
3. **Manual Model Configuration** - Step-by-step guide
4. **Automated Setup** - Using utility scripts
5. **Configuration Files** - Key files explained
6. **Monitoring & Observability** - Prometheus, Grafana, Jaeger
7. **SSO Setup** - Keycloak configuration
8. **API Usage** - Example API calls
9. **Troubleshooting** - Common issues and solutions
10. **Development Workflow** - Building and testing
11. **Security Considerations** - Production recommendations

## Presentation Features

- 📊 **40+ slides** covering all aspects
- 🎨 **Code examples** with syntax highlighting
- 📋 **Tables** for quick reference
- 🔤 **ASCII diagrams** showing architecture
- ✅ **Step-by-step instructions** for manual setup

## Tips

- Use **fullscreen** mode for best experience
- The presentation works great with **dark themes**
- **Code blocks** can be copied for quick testing
- **Tables** provide quick port and service reference

## Alternative Viewing

If you don't have presenterm installed, you can also read the presentation as a regular markdown file:

```bash
# View in terminal
cat presentation.md | less

# View in browser
open presentation.md

# Or just open in your favorite markdown viewer
```

## Creating Your Own Slides

The presentation is in standard Markdown with slide separators:

```markdown
<!-- slide -->
# Your Slide Title
Content here
<!-- end_slide -->
```

Edit `presentation.md` to customize or add slides!
