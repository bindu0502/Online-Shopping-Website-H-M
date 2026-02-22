import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../api/axios';
import ProductCard from '../components/ProductCard';

function Product() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  const [buyingNow, setBuyingNow] = useState(false);
  const [showBuyNowModal, setShowBuyNowModal] = useState(false);
  const [inWishlist, setInWishlist] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProduct();
    trackView();
    fetchSimilarProducts();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await API.get(`/products/${id}`);
      setProduct(response.data);
    } catch (err) {
      console.error('Product error:', err);
      setMessage('Product not found');
    } finally {
      setLoading(false);
    }
  };

  const fetchSimilarProducts = async () => {
    try {
      const response = await API.get(`/products/${id}/similar`);
      setSimilarProducts(response.data || []);
    } catch (err) {
      console.error('Similar products error:', err);
      setSimilarProducts([]);
    }
  };

  const trackView = async () => {
    try {
      await API.post('/interactions/record', {
        article_id: id,
        event_type: 'view'
      });
    } catch (err) {
      console.log('Failed to track view');
    }
  };

  const handleAddToCart = async () => {
    setAddingToCart(true);
    setMessage('');

    try {
      await API.post('/cart/add', {
        article_id: id,
        quantity: quantity,
      });
      setMessage('Added to cart!');
      setTimeout(() => navigate('/cart'), 1500);
    } catch (err) {
      console.error('Add to cart error:', err);
      setMessage('Failed to add');
    } finally {
      setAddingToCart(false);
    }
  };

  const handleWishlist = async () => {
    try {
      if (inWishlist) {
        await API.post(`/wishlist/remove/${id}`);
        setInWishlist(false);
        setMessage('Removed from wishlist');
      } else {
        await API.post('/wishlist/add', { article_id: id });
        setInWishlist(true);
        setMessage('Added to wishlist!');
      }
      setTimeout(() => setMessage(''), 2000);
    } catch (err) {
      console.error('Wishlist error:', err);
      setMessage('Failed to update wishlist');
    }
  };

  const handleBuyNow = () => {
    setShowBuyNowModal(true);
  };

  const confirmBuyNow = async () => {
    setBuyingNow(true);
    setMessage('');

    try {
      const response = await API.post('/orders/buy_now', {
        article_id: id,
        qty: quantity,
        client_order_id: `buy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      });

      setMessage(`Order #${response.data.order_id} placed successfully!`);
      setShowBuyNowModal(false);
      
      // Redirect to orders page after 1.5 seconds
      setTimeout(() => {
        navigate('/orders');
      }, 1500);
    } catch (err) {
      console.error('Buy now error:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to place order';
      setMessage(errorMsg);
      setShowBuyNowModal(false);
    } finally {
      setBuyingNow(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-red-600">Product not found</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate(-1)}
        className="text-indigo-600 hover:text-indigo-800 mb-6"
      >
        ← Back
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-200 rounded-lg h-96 flex items-center justify-center">
          {product.image_path ? (
            <img
              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${product.image_path}`}
              alt={product.name}
              loading="lazy"
              className="h-full w-full object-cover rounded-lg"
              onError={(e) => {
                e.target.src = '/no-image.png';
                e.target.onerror = null;
              }}
            />
          ) : (
            <span className="text-gray-400 text-xl">No Image Available</span>
          )}
        </div>

        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {product.name || 'Product'}
          </h1>
          
          {/* Product Description */}
          {product.description && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
              <p className="text-gray-600 leading-relaxed">
                {product.description}
              </p>
            </div>
          )}
          
          <p className="text-2xl font-bold text-indigo-600 mb-4">
            ${product.price?.toFixed(2) || '0.00'}
          </p>

          <div className="space-y-2 mb-6">
            <p className="text-gray-700">
              <span className="font-semibold">Group:</span>{' '}
              {product.product_group_name || 'N/A'}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Department:</span>{' '}
              {product.department_no || 'N/A'}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Article ID:</span>{' '}
              {product.article_id}
            </p>
            
            {/* Color Information */}
            {product.colors && (
              <div className="pt-2">
                <p className="text-gray-700 mb-2">
                  <span className="font-semibold">Available Colors:</span>
                </p>
                <div className="flex flex-wrap gap-2">
                  {product.colors.split(',').map((color, index) => (
                    <span
                      key={index}
                      className="inline-block px-3 py-1 text-sm font-medium bg-indigo-100 text-indigo-800 rounded-full capitalize"
                    >
                      {color.trim()}
                    </span>
                  ))}
                </div>
                {product.color_description && (
                  <p className="text-sm text-gray-600 mt-2 italic">
                    {product.color_description}
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div className="space-y-3">
            <button
              onClick={handleBuyNow}
              disabled={buyingNow}
              className="w-full bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 disabled:opacity-50 font-medium text-lg shadow-md"
            >
              {buyingNow ? 'Processing...' : '⚡ Buy Now'}
            </button>

            <button
              onClick={handleAddToCart}
              disabled={addingToCart}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-md hover:bg-indigo-700 disabled:opacity-50 font-medium text-lg"
            >
              {addingToCart ? 'Adding...' : 'Add to Cart'}
            </button>

            <button
              onClick={handleWishlist}
              className={`w-full py-3 px-6 rounded-md font-medium text-lg border-2 transition-colors ${
                inWishlist
                  ? 'bg-red-50 border-red-500 text-red-600 hover:bg-red-100'
                  : 'bg-white border-gray-300 text-gray-700 hover:border-indigo-500 hover:text-indigo-600'
              }`}
            >
              {inWishlist ? '❤ Remove from Wishlist' : '♡ Add to Wishlist'}
            </button>
          </div>

          {message && (
            <div
              className={`mt-4 p-3 rounded ${
                message.includes('Failed')
                  ? 'bg-red-100 text-red-700'
                  : 'bg-green-100 text-green-700'
              }`}
            >
              {message}
            </div>
          )}
        </div>
      </div>

      {/* Buy Now Confirmation Modal */}
      {showBuyNowModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Confirm Purchase
            </h3>
            
            <div className="mb-6">
              <div className="flex items-center gap-4 mb-4">
                {product.image_path && (
                  <img
                    src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${product.image_path}`}
                    alt={product.name}
                    className="w-20 h-20 object-cover rounded"
                  />
                )}
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{product.name}</p>
                  <p className="text-sm text-gray-600">{product.product_group_name}</p>
                </div>
              </div>
              
              <div className="border-t border-gray-200 pt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Price:</span>
                  <span className="font-semibold">${product.price?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Quantity:</span>
                  <span className="font-semibold">{quantity}</span>
                </div>
                <div className="flex justify-between text-lg border-t border-gray-200 pt-2">
                  <span className="font-bold">Total:</span>
                  <span className="font-bold text-green-600">
                    ${(product.price * quantity).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowBuyNowModal(false)}
                disabled={buyingNow}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmBuyNow}
                disabled={buyingNow}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 font-medium"
              >
                {buyingNow ? 'Processing...' : 'Confirm Purchase'}
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-4 text-center">
              Payment will be processed immediately
            </p>
          </div>
        </div>
      )}

      {/* Similar Products Section */}
      {similarProducts.length > 0 && (
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Similar Products
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {similarProducts.map((similarProduct) => (
              <ProductCard key={similarProduct.article_id} product={similarProduct} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Product;
