# Smart Thermostat Automation System - Deployment Guide

This comprehensive guide provides step-by-step instructions for deploying the Smart Thermostat Automation System with Django backend and React frontend.

## Table of Contents
1. [Overview](#overview)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Integration](#frontend-integration)
4. [Business Analysis Page](#business-analysis-page)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)

## Overview

The Smart Thermostat Automation System consists of:

1. **Django Backend**: A robust, scalable API built with Django and Django REST Framework
2. **React Frontend**: Your existing React frontend, updated to work with the Django backend
3. **Business Analysis Page**: A visually compelling page showcasing the system's value proposition

This guide will walk you through deploying each component to Render, ensuring they work together seamlessly.

## Backend Deployment

### Option 1: Direct Deployment to Render

1. **Create a new Web Service on Render**:
   - Log in to your Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository or use "Deploy from public Git repository"
   - Enter the repository URL: `https://github.com/yourusername/smartstatback.git`

2. **Configure the Web Service**:
   - Name: `smartstatback` (or your preferred name)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start Command: `gunicorn thermostat_project.wsgi:application`
   - Select the appropriate instance type (at least 512 MB RAM recommended)

3. **Set Environment Variables**:
   - `PYTHON_VERSION`: `3.11.0`
   - `SECRET_KEY`: Generate a secure random string
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*.onrender.com,your-custom-domain.com` (if applicable)
   - `DATABASE_URL`: This will be automatically set if you use Render's PostgreSQL service

4. **Create a PostgreSQL Database** (recommended for production):
   - In your Render dashboard, go to "New" and select "PostgreSQL"
   - Configure your database with a name and user
   - Once created, note the internal connection string
   - Add it as an environment variable in your Web Service settings

5. **Deploy the Service**:
   - Click "Create Web Service"
   - Wait for the build and deployment to complete
   - Your backend will be available at `https://your-service-name.onrender.com`

### Option 2: GitHub Integration

1. **Fork the Repository**:
   - Fork the Django backend repository to your GitHub account
   - Clone it to your local machine

2. **Update the Repository**:
   - Replace the existing backend code with the Django project
   - Commit and push the changes to GitHub

3. **Deploy to Render**:
   - Follow the same steps as Option 1, but connect your GitHub repository instead of using the public URL

## Frontend Integration

### Update API Configuration

1. **Update API Base URL**:
   - Open `src/lib/api.ts` in your frontend project
   - Update the `API_BASE_URL` to point to your new Django backend:
     ```typescript
     const API_BASE_URL = 'https://your-backend-service.onrender.com/api';
     ```

2. **Update Authentication Flow**:
   - Follow the instructions in the `frontend_integration_guide.md` file to update your authentication flow
   - Ensure all API calls are updated to match the Django endpoints

### Deploy Updated Frontend

1. **Build the Frontend**:
   - Run `npm run build` to create a production build

2. **Deploy to Render**:
   - Log in to your Render dashboard
   - Go to your existing frontend service
   - Navigate to "Settings" > "Build & Deploy"
   - Trigger a manual deploy or push changes to your connected repository

3. **Verify Integration**:
   - Once deployed, visit your frontend URL
   - Test the login functionality
   - Verify that API calls are working correctly

## Business Analysis Page

The business analysis page is integrated into the Django backend as a standalone HTML page.

### Accessing the Business Analysis Page

- The page is available at: `https://your-backend-service.onrender.com/business-analysis/`
- This page can be shared with potential customers or investors

### Customizing the Business Analysis Page

1. **Update Content**:
   - Edit `templates/business_analysis.html` to update content
   - Modify charts and data in the JavaScript section

2. **Update Branding**:
   - Replace logo images in the `static/images/` directory
   - Update color scheme in `static/css/business_analysis.css`

3. **Add Testimonials**:
   - Add real customer testimonials in the testimonials section
   - Update testimonial images in the `static/images/` directory

## Testing & Verification

### Backend Testing

1. **API Endpoints**:
   - Test all API endpoints using the provided documentation
   - Verify authentication is working correctly
   - Check that data is being properly filtered by user

2. **Admin Interface**:
   - Access the Django admin at `https://your-backend-service.onrender.com/admin/`
   - Log in with the superuser credentials
   - Verify you can manage all models

### Frontend Testing

1. **Authentication**:
   - Test user registration
   - Test user login
   - Verify token refresh is working

2. **Data Management**:
   - Test creating, reading, updating, and deleting properties
   - Test thermostat management
   - Test calendar integration

3. **Responsive Design**:
   - Test the application on various devices and screen sizes
   - Verify the business analysis page is mobile-friendly

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Verify that `CORS_ALLOWED_ORIGINS` in Django settings includes your frontend domain
   - Check that API requests don't include `credentials: 'include'`

2. **Authentication Issues**:
   - Ensure tokens are being stored correctly in localStorage
   - Verify token format in API requests (should be `Bearer <token>`)
   - Check token expiration and refresh logic

3. **Database Migrations**:
   - If you encounter database errors, you may need to run migrations manually:
     ```
     python manage.py migrate
     ```

4. **Static Files**:
   - If static files aren't loading, verify `STATIC_URL` and `STATIC_ROOT` in settings
   - Run `python manage.py collectstatic` to collect all static files

### Getting Help

If you encounter any issues during deployment or integration, please:

1. Check the detailed logs in your Render dashboard
2. Refer to the API documentation and frontend integration guide
3. Contact our support team for assistance

## Next Steps

After successful deployment, consider:

1. Setting up a custom domain for your services
2. Implementing monitoring and alerting
3. Setting up regular database backups
4. Exploring additional features and integrations

---

Thank you for choosing the Smart Thermostat Automation System. We're confident this solution will provide significant value to your business and customers.
