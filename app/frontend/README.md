# AI Tutor Frontend

This is the frontend interface for the application.

## Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   └── styles.css      # Main stylesheet
├── js/
│   ├── config.js       # API configuration
│   ├── api.js          # API service layer
│   └── app.js          # Main application logic
└── assets/
    ├── images/         # Image files
    └── fonts/          # Custom fonts
```

## Getting Started

1. Make sure your backend is running on `http://localhost:8000`

2. Open `index.html` in a browser, or serve it with a local server:
   ```bash
   # Using Python
   python -m http.server 3000
   
   # Or using Node.js http-server
   npx http-server -p 3000
   ```

3. Navigate to `http://localhost:3000` in your browser

## Configuration

Update the API base URL in `js/config.js` if your backend runs on a different port or host.

## Features

- Clean, modern chat interface
- Responsive design for mobile and desktop
- Real-time message streaming
- Loading indicators
- Error handling
