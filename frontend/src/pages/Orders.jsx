import { useState, useEffect } from 'react';
import API from '../api/axios';
import dayjs from 'dayjs';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await API.get('/orders/');
      console.log('Orders response:', response.data);
      if (response.data.orders && response.data.orders.length > 0) {
        console.log('First order items:', response.data.orders[0].items);
      }
      setOrders(response.data.orders || []);
    } catch (err) {
      console.error('Orders error:', err);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading orders...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Order History</h1>

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600">No orders yet</p>
          <p className="text-sm text-gray-500 mt-2">Your orders will appear here after purchase</p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.order_id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-lg font-semibold text-gray-900">
                    Order #{order.order_id}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {dayjs(order.created_at).format('MMM D, YYYY h:mm A')}
                  </p>
                  {order.payment_method && (
                    <p className="text-xs text-gray-500 mt-1">
                      Payment: {order.payment_method === 'buy_now_placeholder' ? 'Buy Now' : order.payment_method}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-indigo-600">
                    ${order.total_amount.toFixed(2)}
                  </p>
                  <span className={`inline-block mt-2 px-3 py-1 text-sm rounded-full ${
                    order.payment_status === 'paid' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {order.payment_status || 'Completed'}
                  </span>
                </div>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-3 text-gray-900">Items:</h3>
                <div className="space-y-3">
                  {order.items && order.items.length > 0 ? (
                    order.items.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                        {/* Product Image */}
                        <div className="w-20 h-20 flex-shrink-0 bg-gray-200 rounded-md overflow-hidden">
                          {item.image_path ? (
                            <img
                              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${item.image_path}`}
                              alt={item.name || item.article_id}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                console.error('Image load error:', item.image_path);
                                e.target.style.display = 'none';
                                e.target.parentElement.innerHTML = '<div class="w-full h-full flex flex-col items-center justify-center text-gray-400"><svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg><span class="text-xs mt-1">No Image</span></div>';
                              }}
                            />
                          ) : (
                            <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                              <span className="text-xs mt-1">No Image</span>
                            </div>
                          )}
                        </div>
                        
                        {/* Product Details */}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {item.name || `Article ${item.article_id}`}
                          </p>
                          {item.product_group_name && (
                            <p className="text-sm text-gray-500 mt-1">
                              {item.product_group_name}
                            </p>
                          )}
                          <p className="text-sm text-gray-600 mt-1">
                            Quantity: {item.qty}
                          </p>
                        </div>
                        
                        {/* Price */}
                        <div className="text-right flex-shrink-0">
                          <p className="font-semibold text-gray-900">
                            ${(item.price * item.qty).toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            ${item.price.toFixed(2)} each
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">No items</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Orders;
