import React from 'react';
import { AuthProvider } from './AuthContext';
import ProtectedRoute from './ProtectedRoute';
import Dashboard from './Dashboard'; // We'll rename the current App.js to Dashboard.js
import { useAuth } from './AuthContext';

// Logout Button Component
const LogoutButton = () => {
  const { logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  return (
    <button
      onClick={handleLogout}
      className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors shadow-md flex items-center"
      title="Logout from Dashboard"
    >
      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
      </svg>
      Logout
    </button>
  );
};

// Protected Dashboard Wrapper
const ProtectedDashboard = () => {
  return (
    <div>
      {/* Logout Button in Top Right */}
      <div className="fixed top-4 right-4 z-50">
        <LogoutButton />
      </div>
      
      {/* Main Dashboard */}
      <Dashboard />
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <ProtectedRoute>
          <ProtectedDashboard />
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
}

export default App;