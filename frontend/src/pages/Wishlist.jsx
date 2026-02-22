import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

function Wishlist() {
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchWishlist();
  }, []);

  const fetchWishlist = async () => {
    try {
      const response = await API.get('/wishlist/');
      console.log('Wishlist response:', response.data);
      setWishlist(response.data);
    } catch (err) {
      console.error('Wishlist error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (articleId) => {
    try {
      await API.post(`/wishlist/remove/${articleId}`);
      fetchWishlist(); // Refresh the list
    } catch (err) {
      console.error('Remove error:', err);
    }
  };

  const handleAddToCart = async (articleId) => {
    try {
      await API.post('/cart/add', {
        article_id: articleId,
        quantity: 1,
      });
      alert('Added to cart!');
    } catch (err) {
      console.error('Add to cart error:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading wishlist...</div>
      </div>
    );
  }

  const items = wishlist?.items || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        ❤️ My Wishlist ({items.length})
      </h1>

      {items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 mb-4">Your wishlist is empty</p>
          <button
            onClick={() => navigate('/')}
            className="text-indigo-600 hover:text-indigo-800"
          >
            Discover Products
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {items.map((product) => (
            <div
              key={product.article_id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow"
            >
              <div
                onClick={() => navigate(`/product/${product.article_id}`)}
                className="cursor-pointer"
              >
                <div className="h-48 bg-gray-200 flex items-center justify-center">
                  {product.image_path ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${product.image_path}`}
                      alt={product.name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <span className="text-gray-400">No Image</span>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {product.name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {product.product_group_name}
                  </p>
                  <p className="text-lg font-bold text-indigo-600 mt-2">
                    ${product.price?.toFixed(2)}
                  </p>
                </div>
              </div>
              <div className="p-4 pt-0 space-y-2">
                <button
                  onClick={() => handleAddToCart(product.article_id)}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 text-sm font-medium"
                >
                  Add to Cart
                </button>
                <button
                  onClick={() => handleRemove(product.article_id)}
                  className="w-full bg-red-100 text-red-600 px-4 py-2 rounded-md hover:bg-red-200 text-sm font-medium"
                >
                  Remove from Wishlist
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Wishlist;
