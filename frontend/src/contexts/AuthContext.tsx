import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '../types';
import { apiGetMe, apiLogout } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('leafai_token');
    const savedUser = localStorage.getItem('leafai_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        
        // Verify token in background
        apiGetMe()
          .then((verifiedUser) => {
            setUser(verifiedUser);
            localStorage.setItem('leafai_user', JSON.stringify(verifiedUser));
          })
          .catch(() => {
            // Token expired or invalid
            localStorage.removeItem('leafai_token');
            localStorage.removeItem('leafai_user');
            setToken(null);
            setUser(null);
          })
          .finally(() => {
            setLoading(false);
          });
        return;
      } catch {
        localStorage.removeItem('leafai_token');
        localStorage.removeItem('leafai_user');
      }
    }
    setLoading(false);
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('leafai_token', newToken);
    localStorage.setItem('leafai_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    apiLogout().finally(() => {
      localStorage.removeItem('leafai_token');
      localStorage.removeItem('leafai_user');
      setToken(null);
      setUser(null);
    });
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!token,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
