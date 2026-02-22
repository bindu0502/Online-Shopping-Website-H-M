import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

function ProductCard({ product }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [inWishlist, setInWishlist] = useState(false);
  const navigate = useNavigate();

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    setLoading(true);
    setMessage('');

    try {
      const response = await API.post('/cart/add', {
        article_id: product.article_id,
        quantity: 1,
      });
      
      // Only show success if status is 200
      if (response.status === 200) {
        setMessage('Added to cart!');
        setTimeout(() => setMessage(''), 2000);
      }
    } catch (err) {
      console.error('Add to cart error:', err);
      console.error(err.response?.data);
      
      // Handle 404 - product not found
      if (err.response?.status === 404) {
        setMessage(err.response.data?.detail || 'Product does not exist in database.');
      } else if (err.response?.data?.detail) {
        // Other backend errors with detail message
        setMessage(err.response.data.detail);
      } else {
        // Generic error
        setMessage('Failed to add');
      }
      
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleWishlist = async (e) => {
    e.stopPropagation();
    
    try {
      if (inWishlist) {
        await API.post(`/wishlist/remove/${product.article_id}`);
        setInWishlist(false);
      } else {
        await API.post('/wishlist/add', { article_id: product.article_id });
        setInWishlist(true);
      }
    } catch (err) {
      console.error('Wishlist error:', err);
    }
  };

  const handleClick = () => {
    navigate(`/product/${product.article_id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
    >
      <div className="h-48 bg-gray-200 flex items-center justify-center">
        {product.image_path ? (
          <img
            src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${product.image_path}`}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-cover"
            onError={(e) => {
              e.target.src = '/no-image.png';
              e.target.onerror = null;
            }}
          />
        ) : (
          <span className="text-gray-400">No Image</span>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 truncate">
          {product.name || 'Product'}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {product.product_group_name || 'Fashion Item'}
        </p>
        
        {/* Color Information - ALWAYS DISPLAYED */}
        <div className="mt-2 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-700">Color:</span>
            <span className="text-xs font-semibold text-indigo-600 capitalize">
              {product.matched_color || product.primary_color || product.colors?.split(',')[0] || 'Classic'}
            </span>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed">
            {product.color_description || 'Stylish color that complements any wardrobe'}
          </p>
        </div>
        
        {/* Product Description */}
        {product.description && (
          <p className="text-xs text-gray-500 mt-2 line-clamp-2 leading-relaxed">
            {product.description}
          </p>
        )}
        
        {/* Additional Colors (if multiple and not showing matched color) */}
        {product.colors && !product.matched_color && product.colors.split(',').length > 1 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {product.colors.split(',').slice(1, 3).map((color, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full capitalize"
              >
                {color.trim()}
              </span>
            ))}
            {product.colors.split(',').length > 3 && (
              <span className="inline-block px-2 py-1 text-xs font-medium bg-gray-100 text-gray-500 rounded-full">
                +{product.colors.split(',').length - 3}
              </span>
            )}
          </div>
        )}
        <div className="mt-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg font-bold text-indigo-600">
              ${product.price?.toFixed(2) || '0.00'}
            </span>
            <button
              onClick={handleWishlist}
              className={`text-2xl hover:scale-110 transition-transform ${inWishlist ? 'text-red-500' : 'text-gray-400'}`}
              title={inWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
            >
              {inWishlist ? '❤' : '♡'}
            </button>
          </div>
          <button
            onClick={handleAddToCart}
            disabled={loading}
            className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium"
          >
            {loading ? '...' : 'Add to Cart'}
          </button>
        </div>
        {message && (
          <p className={`text-sm mt-2 ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

export default ProductCard;
