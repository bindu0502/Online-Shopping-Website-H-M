import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { isAuthenticated, logout } from '../auth/auth';
import SearchBar from './SearchBar';
import API from '../api/axios';

function NavBar() {
  const navigate = useNavigate();
  const authenticated = isAuthenticated();
  const [categories, setCategories] = useState([]);
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);

  useEffect(() => {
    if (authenticated) {
      fetchCategories();
    }
  }, [authenticated]);

  const fetchCategories = async () => {
    try {
      const response = await API.get('/categories/');
      // Get top 10 categories
      setCategories(response.data.categories.slice(0, 10));
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold whitespace-nowrap">
              Project149
            </Link>
            {authenticated && (
              <>
                <Link to="/" className="hover:text-indigo-200 hidden md:block">
                  Products
                </Link>
                <div 
                  className="relative hidden md:block"
                  onMouseEnter={() => setShowCategoryDropdown(true)}
                  onMouseLeave={() => setShowCategoryDropdown(false)}
                >
                  <button className="hover:text-indigo-200 flex items-center gap-1">
                    Categories
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {showCategoryDropdown && categories.length > 0 && (
                    <div className="absolute top-full left-0 mt-2 w-56 bg-white rounded-md shadow-lg py-2 z-50">
                      {categories.map((category) => (
                        <Link
                          key={category.name}
                          to={`/category/${encodeURIComponent(category.name)}`}
                          className="block px-4 py-2 text-gray-800 hover:bg-indigo-50 hover:text-indigo-600"
                          onClick={() => setShowCategoryDropdown(false)}
                        >
                          {category.name}
                          <span className="text-xs text-gray-500 ml-2">({category.count})</span>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
                <Link to="/foryou" className="hover:text-indigo-200 hidden md:block">
                  For You
                </Link>
                <Link to="/wishlist" className="hover:text-indigo-200 hidden md:block">
                  ❤️ Wishlist
                </Link>
                <Link to="/orders" className="hover:text-indigo-200 hidden md:block">
                  Orders
                </Link>
                <Link to="/color-editor" className="hover:text-indigo-200 hidden md:block">
                  🎨 Colors
                </Link>
              </>
            )}
          </div>

          {/* Search Bar - Only show when authenticated */}
          {authenticated && (
            <div className="flex-1 max-w-2xl mx-4">
              <SearchBar />
            </div>
          )}

          <div className="flex items-center space-x-4">
            {authenticated ? (
              <>
                <Link
                  to="/cart"
                  className="bg-white text-indigo-600 px-4 py-2 rounded-md hover:bg-indigo-50 font-medium whitespace-nowrap"
                >
                  🛒 Cart
                </Link>
                <button
                  onClick={handleLogout}
                  className="hover:text-indigo-200 hidden md:block"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-indigo-200">
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-white text-indigo-600 px-4 py-2 rounded-md hover:bg-indigo-50 font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
