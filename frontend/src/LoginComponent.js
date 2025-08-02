import React, { useState } from 'react';
import { useAuth } from './AuthContext';

const LoginComponent = () => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const result = await login(password);
    
    if (!result.success) {
      setError(result.error || 'Login failed');
      setPassword(''); // Clear password on error
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-nature-light via-green-50 to-sage-green flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo/Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-forest-dark mb-2">
            Conservation Solutions
          </h1>
          <h2 className="text-2xl font-semibold text-nature-green mb-2">
            Translocation Dashboard
          </h2>
          <p className="text-nature-brown">
            Tracking Wildlife Conservation Across Africa
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white p-8 rounded-xl shadow-2xl border-l-4 border-nature-green">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-forest-dark">
              Dashboard Access
            </h3>
            <p className="text-nature-brown mt-2">
              Enter password to access the conservation dashboard
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-forest-dark mb-2">
                Dashboard Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border-2 border-sage-green rounded-lg focus:border-nature-green focus:ring-2 focus:ring-forest-light transition-all duration-200 text-lg"
                placeholder="Enter dashboard password"
                required
                disabled={isLoading}
              />
            </div>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg">
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{error}</span>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !password.trim()}
              className={`w-full py-3 px-4 rounded-lg font-bold text-lg transition-all duration-300 transform ${
                isLoading || !password.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-nature-green to-forest-green text-white hover:from-forest-green hover:to-forest-dark hover:scale-105 shadow-lg'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Authenticating...
                </div>
              ) : (
                'Access Dashboard'
              )}
            </button>
          </form>

          {/* Security Notice */}
          <div className="mt-6 text-center">
            <div className="bg-nature-light p-4 rounded-lg border border-sage-green">
              <div className="flex items-center justify-center text-nature-brown text-sm">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
                <span>Secure access to conservation data</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-nature-brown text-sm">
          Protected conservation database • Authorized access only
        </div>
      </div>
    </div>
  );
};

export default LoginComponent;