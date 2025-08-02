import React from 'react';
import { useAuth } from './AuthContext';
import LoginComponent from './LoginComponent';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-nature-light flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-nature-green mx-auto mb-4"></div>
          <div className="text-xl font-semibold text-forest-dark">Loading Dashboard...</div>
          <div className="text-sm text-nature-brown mt-2">Verifying authentication</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginComponent />;
  }

  return children;
};

export default ProtectedRoute;