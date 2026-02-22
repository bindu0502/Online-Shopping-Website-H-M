import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from '../api/axios';
import { setToken } from './auth';

const CATEGORIES = [
  'Garment Upper body',
  'Garment Lower body',
  'Garment Full body',
  'Accessories',
  'Underwear',
  'Shoes',
  'Swimwear',
  'Socks & Tights',
  'Nightwear'
];

function Signup() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    age: '',
  });
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      if (selectedCategories.length < 3) {
        setSelectedCategories([...selectedCategories, category]);
      } else {
        setError('Maximum 3 categories can be selected');
        setTimeout(() => setError(''), 3000);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate categories
    if (selectedCategories.length === 0) {
      setError('Please select at least 1 category');
      return;
    }

    if (selectedCategories.length > 3) {
      setError('Maximum 3 categories allowed');
      return;
    }

    setLoading(true);

    try {
      const signupData = {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        preferred_categories: selectedCategories
      };

      await API.post('/auth/signup', signupData);

      // Auto-login after signup
      const loginResponse = await API.post('/auth/login', {
        email: formData.email,
        password: formData.password,
      });

      if (loginResponse.data.access_token) {
        setToken(loginResponse.data.access_token);
        setTimeout(() => navigate('/'), 50);
      } else {
        setError('Signup successful but login failed');
      }
    } catch (err) {
      console.error('Signup error:', err);
      
      let errorMessage = 'Signup failed';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => e.msg).join(', ');
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm space-y-4">
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Full Name"
            />
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Email address"
            />
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Password"
            />
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Age (optional)"
            />
          </div>

          {/* Category Selection */}
          <div className="border border-gray-300 rounded-md p-4 bg-white">
            <label className="block text-sm font-medium text-gray-900 mb-3">
              Preferred Categories <span className="text-red-500">*</span>
              <span className="text-xs text-gray-500 ml-2">(Select 1-3)</span>
            </label>
            <div className="space-y-2">
              {CATEGORIES.map((category) => (
                <label
                  key={category}
                  className="flex items-center p-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(category)}
                    onChange={() => handleCategoryToggle(category)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm text-gray-700">{category}</span>
                </label>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Selected: {selectedCategories.length}/3
            </p>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>

          <div className="text-center">
            <Link to="/login" className="text-indigo-600 hover:text-indigo-500">
              Already have an account? Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Signup;
