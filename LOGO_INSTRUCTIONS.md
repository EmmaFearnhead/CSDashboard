# 🏢 Adding Your Company Logo

## Quick Logo Setup

Your conservation dashboard is ready for your company logo! Here's how to add it:

### Option 1: Simple Replacement (Recommended)
1. **Prepare your logo file:**
   - Format: PNG, JPG, or SVG
   - Size: Recommended 120px wide x 80px tall
   - Background: Transparent PNG works best

2. **Add to your website:**
   - Save your logo as `logo.png` (or appropriate extension)
   - Place it in the `/app/frontend/public/` folder
   - Update the logo path in `/app/frontend/src/App.js`

### Option 2: Current Placeholder
The dashboard currently shows:
- **Placeholder URL:** `/api/placeholder/120/80` 
- **Fallback:** 🌿 nature emoji if logo fails to load

### Code Location to Update:
**File:** `/app/frontend/src/App.js`
**Line:** Around line 570

```javascript
<img 
  src="/logo.png"  // <- Change this to your logo path
  alt="Your Conservation Company Logo" 
  className="h-20 w-auto object-contain"
/>
```

### Logo Styling:
- **Current size:** 80px height (width auto-adjusts)
- **Hover effect:** Slight scale animation
- **Position:** Left side of the header, next to title

### Professional Logo Tips:
1. **Use SVG format** for crisp scaling
2. **Transparent background** for clean look
3. **Horizontal layout** works best with current design
4. **Green/natural colors** match the theme

### Alternative Logo Positions:
If you prefer your logo elsewhere, I can help move it to:
- Center of header (above title)
- Right side of header
- Navigation bar
- Favicon (browser tab icon)

## Need Help?
Just provide your logo file and let me know:
1. Preferred position
2. Size preferences  
3. Any special styling needs

I'll integrate it perfectly with your conservation dashboard! 🌍