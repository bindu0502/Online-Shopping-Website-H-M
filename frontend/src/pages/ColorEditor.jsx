import { useState, useEffect } from 'react';
import API from '../api/axios';

function ColorEditor() {
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [editForm, setEditForm] = useState({
    colors: '',
    primary_color: '',
    color_description: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await API.get('/color-editor/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const searchProducts = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await API.get(`/color-editor/search?q=${encodeURIComponent(searchQuery)}&limit=20`);
      setSearchResults(response.data.products);
    } catch (err) {
      console.error('Error searching products:', err);
      setMessage('Error searching products');
    } finally {
      setLoading(false);
    }
  };

  const loadEditableProducts = async () => {
    setLoading(true);
    try {
      const response = await API.get('/color-editor/list/editable?limit=50');
      setSearchResults(response.data.products);
      setSearchQuery('');
    } catch (err) {
      console.error('Error loading products:', err);
      setMessage('Error loading products');
    } finally {
      setLoading(false);
    }
  };

  const selectProduct = async (product) => {
    if (product.color_manually_edited) {
      setMessage('🔒 This product is permanently locked and cannot be edited.');
      return;
    }

    setSelectedProduct(product);
    setEditForm({
      colors: product.colors || '',
      primary_color: product.primary_color || '',
      color_description: product.color_description || ''
    });
    setMessage('');
  };

  const generateSuggestions = async () => {
    if (!selectedProduct) return;

    setLoading(true);
    try {
      const response = await API.post(`/color-editor/${selectedProduct.article_id}/generate-suggestions`);
      const suggestions = response.data.suggestions;
      
      setEditForm({
        colors: suggestions.colors,
        primary_color: suggestions.primary_color,
        color_description: suggestions.color_description
      });
      
      setMessage(`✨ Generated suggestions (confidence: ${(suggestions.confidence * 100).toFixed(0)}%)`);
    } catch (err) {
      console.error('Error generating suggestions:', err);
      setMessage('Error generating suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowConfirmModal(true);
  };

  const confirmSave = async () => {
    if (!selectedProduct) return;

    setLoading(true);
    try {
      const response = await API.put(`/color-editor/${selectedProduct.article_id}`, editForm);
      
      setMessage('🔒 SUCCESS: Product colors updated and PERMANENTLY LOCKED!');
      setSelectedProduct(null);
      setEditForm({ colors: '', primary_color: '', color_description: '' });
      setShowConfirmModal(false);
      
      // Refresh stats and search results
      fetchStats();
      if (searchResults.length > 0) {
        if (searchQuery) {
          searchProducts();
        } else {
          loadEditableProducts();
        }
      }
      
    } catch (err) {
      console.error('Error updating product:', err);
      if (err.response?.status === 403) {
        setMessage('🔒 This product is already locked and cannot be edited.');
      } else {
        setMessage('Error updating product colors');
      }
      setShowConfirmModal(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🔒 One-Time Color Editor
        </h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-yellow-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Important Warning
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>Each product can only be edited <strong>ONCE</strong>. After saving changes, the product will be <strong>permanently locked</strong> and cannot be changed again.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">📊</span>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Products
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.total_products.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">✅</span>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Editable Products
                      </dt>
                      <dd className="text-lg font-medium text-green-600">
                        {stats.editable_products.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🔒</span>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Locked Products
                      </dt>
                      <dd className="text-lg font-medium text-red-600">
                        {stats.locked_products.toLocaleString()}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">📈</span>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Lock Percentage
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {stats.lock_percentage.toFixed(1)}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Search and Product List */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Find Products to Edit</h2>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search products by name..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  onKeyPress={(e) => e.key === 'Enter' && searchProducts()}
                />
                <button
                  onClick={searchProducts}
                  disabled={loading || !searchQuery.trim()}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  Search
                </button>
              </div>
              
              <button
                onClick={loadEditableProducts}
                disabled={loading}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                Show All Editable Products
              </button>
            </div>
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Products ({searchResults.length})
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {searchResults.map((product) => (
                  <div
                    key={product.article_id}
                    onClick={() => selectProduct(product)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      product.color_manually_edited
                        ? 'border-red-200 bg-red-50'
                        : selectedProduct?.article_id === product.article_id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex gap-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0">
                        <div className="w-20 h-20 bg-gray-200 rounded-lg overflow-hidden">
                          {product.image_path ? (
                            <img
                              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${product.image_path}`}
                              alt={product.name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.target.src = '/no-image.png';
                                e.target.onerror = null;
                              }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                              No Image
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Product Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 truncate">{product.name}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-medium">ID:</span> {product.article_id}
                            </p>
                            <p className="text-sm text-gray-600">
                              <span className="font-medium">Category:</span> {product.product_group_name || 'N/A'}
                            </p>
                            {product.colors && (
                              <div className="mt-2">
                                <p className="text-xs text-indigo-600">
                                  <span className="font-medium">Colors:</span> {product.colors}
                                </p>
                                {product.color_description && (
                                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                    {product.color_description}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                          <div className="ml-3 flex-shrink-0">
                            {product.color_manually_edited ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                🔒 Locked
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                ✅ Editable
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Edit Form */}
        <div className="space-y-6">
          {selectedProduct ? (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Edit Colors - {selectedProduct.name}
              </h2>
              
              {/* Product Info with Image */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex gap-4">
                  {/* Product Image */}
                  <div className="flex-shrink-0">
                    <div className="w-24 h-24 bg-gray-200 rounded-lg overflow-hidden">
                      {selectedProduct.image_path ? (
                        <img
                          src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${selectedProduct.image_path}`}
                          alt={selectedProduct.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = '/no-image.png';
                            e.target.onerror = null;
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                          No Image
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Product Details */}
                  <div className="flex-1">
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-medium">Article ID:</span> {selectedProduct.article_id}
                    </p>
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-medium">Product Name:</span> {selectedProduct.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Category:</span> {selectedProduct.product_group_name || 'N/A'}
                    </p>
                    
                    {/* Current Colors */}
                    {selectedProduct.colors && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <p className="text-xs text-gray-500 mb-1">Current Colors:</p>
                        <div className="flex flex-wrap gap-1">
                          {selectedProduct.colors.split(',').map((color, index) => (
                            <span
                              key={index}
                              className="inline-block px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded-full capitalize"
                            >
                              {color.trim()}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Colors (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={editForm.colors}
                    onChange={(e) => setEditForm({...editForm, colors: e.target.value})}
                    placeholder="e.g., red, blue, white"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Primary Color
                  </label>
                  <input
                    type="text"
                    value={editForm.primary_color}
                    onChange={(e) => setEditForm({...editForm, primary_color: e.target.value})}
                    placeholder="e.g., red"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Color Description
                  </label>
                  <textarea
                    value={editForm.color_description}
                    onChange={(e) => setEditForm({...editForm, color_description: e.target.value})}
                    placeholder="e.g., Vibrant red with elegant appeal"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={generateSuggestions}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                  >
                    ✨ Generate Suggestions
                  </button>
                  
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 font-medium"
                  >
                    🔒 Save & Lock Forever
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">🔍</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a Product to Edit
                </h3>
                <p className="text-gray-500">
                  Search for products or browse the editable products list to get started.
                </p>
              </div>
            </div>
          )}

          {/* Message Display */}
          {message && (
            <div className={`p-4 rounded-lg ${
              message.includes('SUCCESS') || message.includes('🔒') 
                ? 'bg-green-50 text-green-800 border border-green-200'
                : message.includes('Error') || message.includes('locked')
                ? 'bg-red-50 text-red-800 border border-red-200'
                : 'bg-blue-50 text-blue-800 border border-blue-200'
            }`}>
              {message}
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="text-center">
              <span className="text-4xl mb-4 block">⚠️</span>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                PERMANENT LOCK WARNING
              </h3>
              
              <div className="text-left bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <div className="flex gap-4">
                  {/* Product Image in Modal */}
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                      {selectedProduct.image_path ? (
                        <img
                          src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${selectedProduct.image_path}`}
                          alt={selectedProduct.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = '/no-image.png';
                            e.target.onerror = null;
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                          No Image
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Product Details in Modal */}
                  <div className="flex-1">
                    <p className="text-sm text-yellow-800 mb-2">
                      <strong>You are about to permanently lock this product:</strong>
                    </p>
                    <p className="text-sm text-gray-700 mb-1">
                      <strong>Product:</strong> {selectedProduct?.name}
                    </p>
                    <p className="text-sm text-gray-700 mb-1">
                      <strong>Article ID:</strong> {selectedProduct?.article_id}
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Category:</strong> {selectedProduct?.product_group_name}
                    </p>
                    <div className="border-t border-yellow-300 pt-2">
                      <p className="text-sm text-gray-700 mb-1">
                        <strong>New Colors:</strong> {editForm.colors}
                      </p>
                      <p className="text-sm text-gray-700 mb-1">
                        <strong>Primary:</strong> {editForm.primary_color}
                      </p>
                      <p className="text-sm text-gray-700">
                        <strong>Description:</strong> {editForm.color_description}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <p className="text-red-600 font-medium mb-6">
                After saving, this product will be PERMANENTLY LOCKED and cannot be edited again!
              </p>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmSave}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 font-medium"
                >
                  {loading ? 'Saving...' : 'LOCK FOREVER'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ColorEditor;