# How to Deploy Your Mario Game to the Web

Your game is now web-ready! Here are the best ways to distribute it:

## Option 1: Pygbag (Recommended - Easiest)

Pygbag converts your Pygame game to WebAssembly for browsers.

### Steps:

1. **Install Pygbag:**
   ```bash
   pip install pygbag
   ```

2. **Build for web:**
   ```bash
   pygbag mario.py
   ```

3. **Test locally:**
   - Pygbag will start a local server
   - Open your browser to the URL shown (usually http://localhost:8000)

4. **Deploy to itch.io:**
   - Create account at https://itch.io
   - Click "Upload New Project"
   - Select "HTML" as the project type
   - Upload the `build/web` folder that Pygbag created
   - Check "This file will be played in the browser"
   - Set viewport dimensions to 800x400 (or larger)
   - Publish!

### Alternative hosting for Pygbag output:

**GitHub Pages (Free):**
```bash
# Push your game to GitHub
git add .
git commit -m "Add web-ready game"
git push

# Enable GitHub Pages in repository settings
# Point it to the build/web folder
```

**Netlify/Vercel (Free):**
- Drag and drop the `build/web` folder
- Instant deployment!

## Option 2: Itch.io Desktop Download

If you want users to download instead of play in browser:

1. Create account at https://itch.io
2. Click "Upload New Project"
3. Upload `mario.py` as a zip file
4. Mark it as requiring Python/Pygame
5. Include instructions for users:
   ```
   Requirements:
   - Python 3.7+
   - pygame

   To run:
   pip install pygame
   python mario.py
   ```

## Option 3: PyInstaller (Standalone Executable)

Create a standalone .exe (Windows) or binary (Mac/Linux):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed mario.py
```

Upload the executable to itch.io or your own website.

## Recommended: Pygbag + itch.io

This gives you:
- ✅ No installation required for players
- ✅ Works on any device with a browser
- ✅ Free hosting
- ✅ Built-in community and discovery
- ✅ Easy updates (just re-upload)

## Tips for Web Distribution:

1. **Add a thumbnail** - Create a screenshot or banner art
2. **Write clear controls** - Let players know:
   - Arrow keys to move
   - Space to jump
3. **Test on mobile** - Pygbag works on touch devices too
4. **Add metadata** - Tags like "platformer", "retro", "arcade"

Good luck with your game!
