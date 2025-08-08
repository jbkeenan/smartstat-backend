# Frontend Integration Guide for Django Backend

This guide provides step-by-step instructions for integrating your existing React frontend with the new Django backend for the Smart Thermostat Automation System.

## Overview

The integration process involves:
1. Updating API utility files to point to the new Django endpoints
2. Modifying authentication flows to work with Django JWT
3. Adjusting data handling for any response format differences
4. Adding the business analysis component to the frontend

## 1. API Configuration

### Update API Base URL

First, update your API base URL in your API utility file:

```typescript
// src/lib/api.ts

// Old Flask backend URL
// const API_BASE_URL = 'https://smartstatback.onrender.com/api';

// New Django backend URL - update this to your deployed Django backend URL
const API_BASE_URL = 'https://your-django-backend.onrender.com/api';
```

### Authentication API Updates

Update your authentication API functions to match the Django JWT authentication:

```typescript
// src/lib/api.ts

export const authApi = {
  login: async (data: LoginRequest) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      return handleApiError(response);
    } catch (err) {
      console.error('Login API error:', err);
      throw err;
    }
  },

  register: async (data: RegisterRequest) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      return handleApiError(response);
    } catch (err) {
      console.error('Register API error:', err);
      throw err;
    }
  },

  getProfile: async (token: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/profile/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      return handleApiError(response);
    } catch (err) {
      console.error('Get profile API error:', err);
      throw err;
    }
  },

  refreshToken: async (refreshToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });
      
      return handleApiError(response);
    } catch (err) {
      console.error('Token refresh API error:', err);
      throw err;
    }
  },
};
```

### Update Authenticated Request Function

```typescript
// src/lib/api.ts

const authenticatedRequest = async (
  endpoint: string, 
  token: string, 
  options: RequestInit = {}
) => {
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    return handleApiError(response);
  } catch (err) {
    console.error(`API error for ${endpoint}:`, err);
    throw err;
  }
};
```

### Update Resource API Functions

Update your resource API functions to match the Django endpoints:

```typescript
// src/lib/api.ts

// Properties API
export const propertiesApi = {
  getAll: async (token: string) => {
    return authenticatedRequest('/properties/', token);
  },

  getById: async (token: string, id: number) => {
    return authenticatedRequest(`/properties/${id}/`, token);
  },

  create: async (token: string, data: Omit<Property, 'id' | 'user_id'>) => {
    return authenticatedRequest('/properties/', token, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  },

  update: async (token: string, id: number, data: Partial<Omit<Property, 'id' | 'user_id'>>) => {
    return authenticatedRequest(`/properties/${id}/`, token, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  },

  delete: async (token: string, id: number) => {
    return authenticatedRequest(`/properties/${id}/`, token, {
      method: 'DELETE',
    });
  },
};

// Similar updates for thermostatsApi, calendarsApi, schedulesApi, etc.
```

## 2. Authentication Flow Updates

### Update Authentication Context

Update your authentication context to work with Django JWT:

```typescript
// src/hooks/useAuth.tsx

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../lib/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem('refreshToken'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const userData = await authApi.getProfile(token);
          setUser(userData.user);
        } catch (error) {
          // Token might be expired, try to refresh
          if (refreshToken) {
            try {
              const refreshData = await authApi.refreshToken(refreshToken);
              setToken(refreshData.access);
              setRefreshToken(refreshData.refresh);
              localStorage.setItem('token', refreshData.access);
              localStorage.setItem('refreshToken', refreshData.refresh);
              
              // Try again with new token
              const userData = await authApi.getProfile(refreshData.access);
              setUser(userData.user);
            } catch (refreshError) {
              // Refresh failed, logout
              logout();
            }
          } else {
            // No refresh token, logout
            logout();
          }
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [token, refreshToken]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authApi.login({ username, password });
      setUser(data.user);
      setToken(data.access);
      setRefreshToken(data.refresh);
      localStorage.setItem('token', data.access);
      localStorage.setItem('refreshToken', data.refresh);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const response = await authApi.register(data);
      setUser(response.user);
      setToken(response.access);
      setRefreshToken(response.refresh);
      localStorage.setItem('token', response.access);
      localStorage.setItem('refreshToken', response.refresh);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setRefreshToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Update Login Component

```typescript
// src/components/LoginPage.tsx

import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      await login(username, password);
      // Explicitly navigate to dashboard after successful login
      navigate('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
      setError('Login failed. Please check your credentials and try again.');
    }
  };

  return (
    // Your login form JSX
  );
};

export default LoginPage;
```

## 3. Handling Pagination

The Django REST Framework uses pagination for list endpoints. Update your code to handle paginated responses:

```typescript
// Example of handling paginated responses
const fetchProperties = async () => {
  try {
    const response = await propertiesApi.getAll(token);
    // The response now has a structure like { count, next, previous, results }
    setProperties(response.results);
    setTotalCount(response.count);
    
    // If you need to handle pagination in the UI:
    setNextPageUrl(response.next);
    setPreviousPageUrl(response.previous);
  } catch (error) {
    console.error('Error fetching properties:', error);
    setError('Failed to load properties');
  }
};

// Function to load next page
const loadNextPage = async () => {
  if (!nextPageUrl) return;
  
  try {
    // Extract page number from URL
    const url = new URL(nextPageUrl);
    const page = url.searchParams.get('page');
    
    // Make request with page parameter
    const response = await authenticatedRequest(`/properties/?page=${page}`, token);
    setProperties(response.results);
    setNextPageUrl(response.next);
    setPreviousPageUrl(response.previous);
  } catch (error) {
    console.error('Error loading next page:', error);
  }
};
```

## 4. Adding Business Analysis Component

Create a new component for the business analysis page:

```typescript
// src/components/BusinessAnalysis.tsx

import React from 'react';
import { Container, Typography, Grid, Paper, Box } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Sample data for cost savings chart
const costSavingsData = [
  { name: 'Without System', savings: 0, cost: 100 },
  { name: 'With System', savings: 40, cost: 60 },
];

// Sample data for ROI chart
const roiData = [
  { name: '1 Property', roi: 50 },
  { name: '2 Properties', roi: 100 },
  { name: '3 Properties', roi: 150 },
  { name: '5 Properties', roi: 250 },
  { name: '10 Properties', roi: 500 },
];

const BusinessAnalysis = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Why Your Thermostat Automation SaaS Is So Good
      </Typography>
      
      {/* Section 1: Real Problem */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          1. It Solves a Real, Costly Problem for Hosts
        </Typography>
        <Typography paragraph>
          Airbnb and short-term rental hosts bleed money when HVAC systems run unnecessarily between guests.
          Manual control is unreliable. Cleaning crews forget. Guests check in early. AC runs for hours for no reason.
          Your system automates this — saving energy, money, and frustration without human error.
        </Typography>
        
        {/* Cost Savings Chart */}
        <Box sx={{ height: 300, mt: 4 }}>
          <Typography variant="h6" gutterBottom>HVAC Cost Comparison</Typography>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={costSavingsData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Monthly Cost ($)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="cost" name="Cost" fill="#8884d8" />
              <Bar dataKey="savings" name="Savings" fill="#82ca9d" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
      
      {/* Section 2: Cross-Brand */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          2. It Works Across Brands and Scales
        </Typography>
        <Typography paragraph>
          Hosts often own multiple thermostat types (Nest, Cielo, Pioneer, etc.).
          Your platform normalizes control across all brands in one dashboard.
          This is exactly what property managers with 10+ units need — centralized, brand-agnostic automation.
        </Typography>
        
        {/* Add brand logos or icons here */}
        <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
          <Grid item xs={4} md={2}>
            <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>Nest</Paper>
          </Grid>
          <Grid item xs={4} md={2}>
            <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>Cielo</Paper>
          </Grid>
          <Grid item xs={4} md={2}>
            <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>Pioneer</Paper>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Continue with other sections... */}
      
      {/* ROI Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          4. It Saves Money and Pays for Itself
        </Typography>
        <Typography paragraph>
          HVAC is often 40–60% of an Airbnb host's utility bill.
          Your system can easily save $20–50/month/unit or more.
          That means your SaaS pays for itself in 1 property, and generates net ROI with just 2–3 listings.
        </Typography>
        
        {/* ROI Chart */}
        <Box sx={{ height: 300, mt: 4 }}>
          <Typography variant="h6" gutterBottom>Return on Investment</Typography>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={roiData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Monthly ROI (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="roi" name="ROI %" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
      
      {/* Add more sections based on the business analysis */}
    </Container>
  );
};

export default BusinessAnalysis;
```

### Add Business Analysis Route

Update your routing to include the business analysis page:

```typescript
// src/App.tsx or your routing file

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import BusinessAnalysis from './components/BusinessAnalysis';
// Other imports...

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/business-analysis" element={<BusinessAnalysis />} />
          {/* Other routes... */}
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### Add Navigation Link

Add a link to the business analysis page in your navigation:

```typescript
// src/components/Navigation.tsx or similar

import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav>
      {/* Other navigation items */}
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/business-analysis">Business Analysis</Link>
      {/* Other navigation items */}
    </nav>
  );
};
```

## 5. Testing the Integration

After making these changes, test the integration thoroughly:

1. **Authentication Flow**:
   - Test user registration
   - Test user login
   - Test token refresh
   - Test protected routes

2. **API Endpoints**:
   - Test fetching properties
   - Test creating/updating/deleting resources
   - Test pagination handling

3. **Error Handling**:
   - Test invalid credentials
   - Test expired tokens
   - Test network errors

## 6. Deployment

Once testing is complete, deploy your updated frontend:

1. Build the production version:
   ```
   npm run build
   ```

2. Deploy to Render:
   - Upload the build directory to Render
   - Configure environment variables if needed
   - Set the correct backend API URL

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure the Django backend has CORS properly configured
   - Check that the frontend is using the correct API URL

2. **Authentication Issues**:
   - Verify token format (Bearer prefix)
   - Check token expiration and refresh logic

3. **Data Format Differences**:
   - Django REST Framework may return data in a slightly different format
   - Check response structures and adjust frontend code accordingly

### Debugging Tips

1. Use browser developer tools to inspect network requests
2. Add detailed logging for API calls
3. Implement error boundaries in React components
