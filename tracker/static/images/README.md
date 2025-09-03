# Background Video for Signup Page

## How to Add Your Own Background Video

The signup page now supports a background video that plays behind the form. Here's how to add your own:

### Option 1: Replace the Default Video
1. Place your MP4 video file in this directory
2. Rename it to `expense_tracker_background.mp4`
3. Your video will automatically play in the background

### Option 2: Use a Different Filename
1. Place your video file in this directory
2. Update the `src` attribute in `tracker/templates/registration/signup.html`
3. Change line: `<source src="{% static 'images/YOUR_VIDEO_NAME.mp4' %}" type="video/mp4">`

### Video Requirements
- **Format**: MP4 (H.264 codec recommended)
- **Size**: Keep under 10MB for fast loading
- **Resolution**: 1920x1080 or lower for performance
- **Duration**: 10-30 seconds (will loop automatically)
- **Content**: Financial/expense tracking themed (charts, money, graphs, etc.)

### Fallback Animation
If no video is available or if it fails to load, the page will automatically show:
- Animated gradient background
- Floating financial icons (wallet, credit card, charts, etc.)
- Money particle effects
- Smooth color transitions

### Example Video Ideas
- Stock market ticker animations
- Financial charts and graphs
- Money counting or coin animations
- Budget planning visualizations
- Banking/financial services imagery

### Performance Notes
- Videos are muted and loop automatically
- Autoplay is enabled for better user experience
- Fallback animations ensure the page always looks engaging
- All animations are CSS-based for optimal performance
