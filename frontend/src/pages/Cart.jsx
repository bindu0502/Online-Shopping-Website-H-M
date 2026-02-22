import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await API.get('/cart/');
      console.log('Cart response:', response.data);
      setCart(response.data);
    } catch (err) {
      console.error('Cart error:', err);
      console.error('Cart error details:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (articleId) => {
    try {
      await API.post(`/cart/remove/${articleId}`);
      fetchCart();
    } catch (err) {
      console.error('Failed to remove item:', err);
      console.error('Remove error details:', err.response?.data);
    }
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading cart...</div>
      </div>
    );
  }

  const items = cart?.items || [];
  const total = cart?.total || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

      {items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 mb-4">Your cart is empty</p>
          <button
            onClick={() => navigate('/')}
            className="text-indigo-600 hover:text-indigo-800"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md">
            {items.map((item) => (
              <div
                key={item.article_id}
                className="flex items-center p-6 border-b last:border-b-0"
              >
                <div className="h-24 w-24 bg-gray-200 rounded flex-shrink-0">
                  {item.image_path ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${item.image_path}`}
                      alt={item.name}
                      className="h-full w-full object-cover rounded"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.innerHTML = '<div class="h-full w-full flex items-center justify-center text-gray-400">No Image</div>';
                      }}
                    />
                  ) : (
                    <div className="h-full w-full flex items-center justify-center text-gray-400">
                      No Image
                    </div>
                  )}
                </div>
                <div className="ml-6 flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {item.name || 'Product'}
                  </h3>
                  <p className="text-gray-600">{item.product_group_name}</p>
                  <p className="text-gray-600">Quantity: {item.quantity}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-indigo-600">
                    ${(item.price * item.quantity).toFixed(2)}
                  </p>
                  <button
                    onClick={() => handleRemove(item.article_id)}
                    className="text-red-600 hover:text-red-800 text-sm mt-2"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <span className="text-xl font-semibold">Total:</span>
              <span className="text-2xl font-bold text-indigo-600">
                ${total.toFixed(2)}
              </span>
            </div>
            <button
              onClick={handleCheckout}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-md hover:bg-indigo-700 font-medium text-lg"
            >
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Cart;
