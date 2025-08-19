# Vercel Frontend Deployment Guide

## Overview

This guide provides detailed instructions for deploying the RAG AI-Agent React frontend to Vercel. The frontend is built with Vite and requires proper configuration to communicate with the FastAPI backend deployed on Hugging Face Spaces.

## Prerequisites

Before starting the deployment process, ensure you have:

- [ ] **Vercel Account**: Sign up at [vercel.com](https://vercel.com/)
- [ ] **GitHub Repository**: Your code should be pushed to a GitHub repository
- [ ] **Backend Deployed**: FastAPI backend should be deployed to Hugging Face Spaces
- [ ] **Backend URL**: Note your Hugging Face Space URL (e.g., `https://username-spacename.hf.space`)

## Vercel Account Setup

### 1. Create Vercel Account

1. Go to [vercel.com](https://vercel.com/)
2. Click "Sign Up"
3. Choose "Continue with GitHub" for seamless integration
4. Authorize Vercel to access your GitHub repositories
5. Complete the account setup process

### 2. Connect GitHub Repository

1. In your Vercel dashboard, click "New Project"
2. Import your GitHub repository containing the RAG AI-Agent code
3. Vercel will automatically detect it as a monorepo

## Project Configuration

### 1. Vite Project Setup

The frontend uses Vite as the build tool. Verify your `package.json` configuration:

```json
{
  "name": "agent-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tailwindcss/vite": "^4.1.4",
    "axios": "^1.9.0",
    "bootstrap": "^5.3.5",
    "react": "^19.0.0",
    "react-bootstrap": "^2.10.9",
    "react-dom": "^19.0.0",
    "react-icons": "^5.5.0",
    "react-router-bootstrap": "^0.26.3",
    "react-router-dom": "^7.5.2",
    "react-toastify": "^11.0.5",
    "tailwindcss": "^4.1.4"
  }
}
```

### 2. Vite Configuration

Ensure your `vite.config.js` is properly configured:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser'
  },
  server: {
    port: 5174,
    host: true
  }
})
```

## API Proxy Setup for Backend Communication

### 1. Create Vercel Configuration

Create or update `vercel.json` in the `agent-frontend` directory:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ]
}
```

**Important**: Replace `YOUR-USERNAME-YOUR-SPACE-NAME` with your actual Hugging Face Space URL.

### 2. Update Frontend API Configuration

Ensure your frontend API client is configured to use relative URLs. In your `AppClient.jsx` or similar file:

```javascript
import axios from 'axios';

const API_BASE_URL = '/api'; // Use relative URL for Vercel proxy

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

## Deployment Process

### 1. Import Project to Vercel

1. In Vercel dashboard, click "New Project"
2. Select "Import Git Repository"
3. Choose your GitHub repository
4. Vercel will detect the framework automatically

### 2. Configure Build Settings

When importing, configure the following settings:

- **Framework Preset**: Vite (should be auto-detected)
- **Root Directory**: `RAG-AI-Agent/agent-frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`
- **Node.js Version**: 18.x (recommended)

### 3. Environment Variables (if needed)

For the frontend, most configuration is handled through the `vercel.json` proxy. However, if you need build-time environment variables:

1. Go to your project settings in Vercel
2. Navigate to "Environment Variables"
3. Add any required variables (prefix with `VITE_` for Vite projects)

Example:
```
VITE_APP_NAME=RAG AI-Agent
VITE_APP_VERSION=1.0.0
```

### 4. Deploy

1. Click "Deploy" to start the deployment process
2. Vercel will:
   - Install dependencies (`npm install`)
   - Build the project (`npm run build`)
   - Deploy the static files
   - Configure the proxy rules

### 5. Verify Deployment

After deployment completes:

1. **Check Deployment URL**: Vercel provides a unique URL (e.g., `https://your-app.vercel.app`)
2. **Test Application Loading**: Visit the URL and verify the React app loads
3. **Test API Connectivity**: Open browser developer tools and check network requests

## Build Configuration Best Practices

### 1. Optimize Build Performance

Update your `vite.config.js` for production optimization:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['react-bootstrap', 'bootstrap']
        }
      }
    }
  },
  server: {
    port: 5174,
    host: true
  }
})
```

### 2. Configure Build Environment

Create a `.env.production` file in the `agent-frontend` directory:

```env
VITE_NODE_ENV=production
VITE_BUILD_TIME=__BUILD_TIME__
```

### 3. Optimize Bundle Size

Add bundle analysis to your build process by updating `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:analyze": "vite build --mode analyze",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

## Proxy Configuration Details

### 1. Understanding the Proxy Setup

The `vercel.json` configuration creates a proxy that:

- Intercepts all requests to `/api/*` on your frontend domain
- Forwards them to your Hugging Face Space backend
- Handles CORS headers automatically
- Maintains session state and cookies

### 2. Advanced Proxy Configuration

For more complex setups, you can configure multiple proxy rules:

```json
{
  "rewrites": [
    {
      "source": "/api/health",
      "destination": "https://your-backend.hf.space/health"
    },
    {
      "source": "/api/:path*",
      "destination": "https://your-backend.hf.space/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization, X-Requested-With"
        },
        {
          "key": "Access-Control-Max-Age",
          "value": "86400"
        }
      ]
    }
  ]
}
```

### 3. Testing Proxy Configuration

To test if your proxy is working correctly:

1. Open browser developer tools (F12)
2. Go to the Network tab
3. Perform an action that makes an API call
4. Check that requests to `/api/*` return successful responses
5. Verify the request URL shows your Vercel domain, not the backend domain

## Troubleshooting Common Issues

### Build Failures

**Issue**: Build fails with dependency errors
```
Solution:
1. Delete node_modules and package-lock.json
2. Run npm install
3. Ensure all dependencies are in package.json
4. Check for version conflicts
```

**Issue**: Build fails with memory errors
```
Solution:
1. Increase Node.js memory limit in vercel.json:
{
  "build": {
    "env": {
      "NODE_OPTIONS": "--max-old-space-size=4096"
    }
  }
}
```

### Proxy Issues

**Issue**: API calls return 404 errors
```
Solution:
1. Verify vercel.json proxy configuration
2. Check that backend URL is correct and accessible
3. Ensure API endpoints exist on the backend
4. Test backend directly in browser
```

**Issue**: CORS errors despite proxy setup
```
Solution:
1. Check vercel.json headers configuration
2. Verify backend CORS settings
3. Test with browser developer tools
4. Check for preflight OPTIONS requests
```

### Deployment Issues

**Issue**: Deployment succeeds but app doesn't load
```
Solution:
1. Check build logs for errors
2. Verify index.html is in the dist folder
3. Check for JavaScript errors in browser console
4. Verify all assets are loading correctly
```

**Issue**: Environment variables not working
```
Solution:
1. Ensure variables are prefixed with VITE_
2. Check Vercel project settings
3. Redeploy after adding variables
4. Verify variables in build logs
```

## Performance Optimization

### 1. Enable Compression

Vercel automatically enables gzip compression, but you can optimize further:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/index.html",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ]
}
```

### 2. Optimize Images and Assets

1. Use WebP format for images
2. Implement lazy loading for images
3. Minimize bundle size with tree shaking
4. Use dynamic imports for code splitting

### 3. Monitor Performance

1. Use Vercel Analytics to monitor performance
2. Check Core Web Vitals in Vercel dashboard
3. Use Lighthouse for performance auditing
4. Monitor bundle size with webpack-bundle-analyzer

## Security Considerations

### 1. Environment Variables

- Never expose sensitive API keys in frontend environment variables
- Use the proxy configuration to hide backend URLs
- Implement proper authentication if needed

### 2. Content Security Policy

Add CSP headers in `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        }
      ]
    }
  ]
}
```

### 3. HTTPS Enforcement

Vercel automatically provides HTTPS, but you can enforce it:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ]
}
```

## Maintenance and Updates

### 1. Automatic Deployments

Vercel automatically deploys when you push to your main branch:

1. Push changes to GitHub
2. Vercel detects the changes
3. Builds and deploys automatically
4. Provides preview URLs for pull requests

### 2. Manual Deployments

For manual deployments:

1. Use Vercel CLI: `vercel --prod`
2. Or trigger from Vercel dashboard
3. Monitor deployment logs
4. Test after deployment

### 3. Rollback Procedures

If a deployment fails:

1. Go to Vercel dashboard
2. Navigate to your project
3. Click on "Deployments"
4. Find a previous successful deployment
5. Click "Promote to Production"

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure analytics** to monitor usage
3. **Set up monitoring** for uptime and performance
4. **Implement CI/CD** for automated testing
5. **Configure branch deployments** for staging environments

## Support Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vite Documentation**: [vitejs.dev](https://vitejs.dev/)
- **React Documentation**: [react.dev](https://react.dev/)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)

For project-specific issues, refer to the main deployment guide or contact the project maintainer.
