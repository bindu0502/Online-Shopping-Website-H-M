import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

function Checkout() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await API.get('/cart/');
      setCart(response.data);
      if (!response.data.items || response.data.items.length === 0) {
        navigate('/cart');
      }
    } catch (err) {
      console.error('Checkout cart error:', err);
      setError('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    setProcessing(true);
    setError('');

    try {
      const response = await API.post('/orders/checkout', {
        address: '123 Main St', // Placeholder address
        payment_method: 'credit_card' // Placeholder payment method
      });
      navigate('/orders');
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err.response?.data?.detail || 'Checkout failed');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  const items = cart?.items || [];
  const total = cart?.total || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            {items.map((item) => (
              <div key={item.article_id} className="flex justify-between mb-4">
                <div>
                  <p className="font-medium">{item.name}</p>
                  <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                </div>
                <p className="font-semibold">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
              </div>
            ))}
            <div className="border-t pt-4 mt-4">
              <div className="flex justify-between text-xl font-bold">
                <span>Total:</span>
                <span className="text-indigo-600">${total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Payment Information</h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 mb-6">
              This is a demo checkout. Click the button below to complete your order.
            </p>
            <button
              onClick={handleCheckout}
              disabled={processing}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-md hover:bg-indigo-700 disabled:opacity-50 font-medium text-lg"
            >
              {processing ? 'Processing...' : 'Complete Order'}
            </button>
            <button
              onClick={() => navigate('/cart')}
              className="w-full mt-4 bg-gray-200 text-gray-700 py-3 px-6 rounded-md hover:bg-gray-300 font-medium"
            >
              Back to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Checkout;
