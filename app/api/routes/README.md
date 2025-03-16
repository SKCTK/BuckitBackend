# Authentication Guide for Next.js + TypeScript Frontend

This document outlines how to implement authentication in your Next.js application using OAuth 2.0 Authorization Code flow with PKCE (Proof Key for Code Exchange).

## Overview of the Authentication Flow

1. Generate a code verifier and code challenge
2. Redirect the user to the authorization endpoint
3. Receive an authorization code
4. Exchange the code for an access token
5. Use the access token for authenticated API requests

## Example Implementation Steps

### 1. Create Authentication Utilities

Create a file `utils/auth.ts`:

```typescript
// Types for authentication
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Generate a random code verifier
export function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  window.crypto.getRandomValues(array);
  return base64URLEncode(array);
}

// Base64URL encode
export function base64URLEncode(buffer: ArrayBuffer): string {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// Create code challenge from verifier using SHA-256
export async function generateCodeChallenge(codeVerifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await window.crypto.subtle.digest('SHA-256', data);
  return base64URLEncode(digest);
}
```

### 2. Create a Custom Authentication Hook

Create a file `hooks/useAuth.ts`:

```typescript
import { useRouter } from 'next/router';
import { useCallback, useEffect, useState } from 'react';
import { generateCodeVerifier, generateCodeChallenge, TokenResponse } from '../utils/auth';

interface UseAuthReturn {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
}

export function useAuth(): UseAuthReturn {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if user is authenticated on component mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  // Handle login initialization
  const login = useCallback(async () => {
    try {
      // Generate and store the code verifier
      const codeVerifier = generateCodeVerifier();
      localStorage.setItem('code_verifier', codeVerifier);
      
      // Generate the code challenge
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      
      // Prepare auth request parameters
      const params = new URLSearchParams({
        client_id: 'your-client-id',
        redirect_uri: `${window.location.origin}/auth/callback`,
        code_challenge: codeChallenge
      });
      
      // Redirect to authorization endpoint
      router.push(`/api/authorize?${params.toString()}`);
    } catch (error) {
      console.error('Failed to initiate authentication:', error);
    }
  }, [router]);

  // Handle logout
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    router.push('/login');
  }, [router]);

  // Get the current token
  const getToken = useCallback((): string | null => {
    return localStorage.getItem('access_token');
  }, []);

  return {
    isAuthenticated,
    isLoading,
    login,
    logout,
    getToken
  };
}
```

### 3. Create a Callback Page

Create a page at `pages/auth/callback.tsx`:

```typescript
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { TokenResponse } from '../../utils/auth';

export default function AuthCallback() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Make sure router is ready and has query parameters
    if (!router.isReady) return;

    const { auth_code } = router.query;

    if (!auth_code || typeof auth_code !== 'string') {
      setError('No authorization code received');
      return;
    }

    const codeVerifier = localStorage.getItem('code_verifier');
    if (!codeVerifier) {
      setError('No code verifier found');
      return;
    }

    // Exchange code for token
    const exchangeCodeForToken = async () => {
      try {
        const formData = new FormData();
        formData.append('grant_type', 'authorization_code');
        formData.append('code', auth_code);
        formData.append('code_verifier', codeVerifier);

        const response = await fetch('/api/token', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const tokenData: TokenResponse = await response.json();
        localStorage.setItem('access_token', tokenData.access_token);
        localStorage.removeItem('code_verifier');
        
        // Redirect to the dashboard
        router.push('/dashboard');
      } catch (error) {
        console.error('Error exchanging code for token:', error);
        setError('Failed to authenticate');
      }
    };

    exchangeCodeForToken();
  }, [router]);

  if (error) {
    return <div className="error">{error}</div>;
  }

  return <div>Authenticating...</div>;
}
```

### 4. Create an Authentication Wrapper Component

Create a component at `components/AuthGuard.tsx`:

```typescript
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : null;
}
```

### 5. Create an API Client with Authentication

Create a file `utils/api.ts`:

```typescript
interface FetchOptions extends RequestInit {
  token?: string;
}

export async function fetchWithAuth<T>(
  url: string, 
  options: FetchOptions = {}
): Promise<T> {
  const token = options.token || localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No authentication token available');
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      throw new Error('Authentication expired');
    }
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}
```

### 6. Example Usage in a Protected Page

Example file `pages/dashboard.tsx`:

```typescript
import { useEffect, useState } from 'react';
import { NextPage } from 'next';
import AuthGuard from '../components/AuthGuard';
import { fetchWithAuth } from '../utils/api';

interface UserData {
  id: string;
  name: string;
  email: string;
}

const Dashboard: NextPage = () => {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const data = await fetchWithAuth<UserData>('/api/user');
        setUserData(data);
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  return (
    <AuthGuard>
      <div className="dashboard">
        <h1>Dashboard</h1>
        {loading ? (
          <p>Loading user data...</p>
        ) : userData ? (
          <div>
            <p>Welcome, {userData.name}!</p>
            <p>Email: {userData.email}</p>
          </div>
        ) : (
          <p>Failed to load user data</p>
        )}
      </div>
    </AuthGuard>
  );
};

export default Dashboard;
```

## Security Considerations

1. **Store tokens securely**: Consider using HttpOnly cookies via an API route instead of localStorage for better security.
2. **Token validation**: Always validate tokens on the server side for every protected request.
3. **SSR and Token Handling**: Remember that localStorage is not available during server-side rendering in Next.js.
4. **HTTPS**: Ensure all authentication traffic happens over HTTPS.
5. **Refresh Tokens**: Implement token refresh mechanisms for improved user experience.

## TypeScript Considerations

- Define proper types for all authentication-related data and functions
- Use type guards when handling API responses
- Consider using environment variables with proper typing for configuration values

For more information, refer to the [OAuth 2.0 PKCE specification](https://datatracker.ietf.org/doc/html/rfc7636) and the [Next.js Authentication Documentation](https://nextjs.org/docs/authentication).
