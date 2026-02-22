import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../api/axios';
import ProductCard from '../components/ProductCard';

function Category() {
  const { categoryName } = useParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  // Ref for intersection observer
  const observer = useRef();
  const lastProductRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    });
    
    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  // Reset when category changes
  useEffect(() => {
    setProducts([]);
    setPage(1);
    setHasMore(true);
    setTotal(0);
    setError(null);
  }, [categoryName]);

  // Fetch products when page changes
  useEffect(() => {
    fetchCategoryProducts();
  }, [page, categoryName]);

  const fetchCategoryProducts = async (isRefresh = false) => {
    if (loading && !isRefresh) return;
    
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const response = await API.get(`/categories/${encodeURIComponent(categoryName)}/products`, {
        params: {
          skip: (page - 1) * 20,
          limit: 20
        }
      });
      
      if (response.data && response.data.products) {
        if (page === 1) {
          setProducts(response.data.products);
        } else {
          setProducts(prev => [...prev, ...response.data.products]);
        }
        
        setTotal(response.data.total);
        const loadedCount = page === 1 ? response.data.products.length : products.length + response.data.products.length;
        setHasMore(loadedCount < response.data.total);
      }
    } catch (err) {
      console.error('Category products error:', err);
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load products');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setPage(1);
    setProducts([]);
    setHasMore(true);
    fetchCategoryProducts(true);
  };

  if (error && products.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => {
              setPage(1);
              setProducts([]);
              setHasMore(true);
              fetchCategoryProducts();
            }}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-3xl font-bold text-gray-900">{categoryName}</h1>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              refreshing
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700'
            }`}
            title="Refresh products"
          >
            <svg
              className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        {total > 0 && (
          <p className="text-gray-600">
            Showing {products.length} of {total.toLocaleString()} product{total !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {products.length === 0 && !loading ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">No products found in this category</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Browse All Products
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((product, index) => {
              if (products.length === index + 1) {
                return (
                  <div ref={lastProductRef} key={product.article_id}>
                    <ProductCard product={product} />
                  </div>
                );
              } else {
                return <ProductCard key={product.article_id} product={product} />;
              }
            })}
          </div>
          
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              <p className="mt-4 text-gray-600">Loading more products...</p>
            </div>
          )}
          
          {!hasMore && products.length > 0 && (
            <div className="text-center py-8">
              <p className="text-lg text-gray-600">🎉 No more products in this category.</p>
              <p className="text-sm text-gray-500 mt-2">All {total.toLocaleString()} products loaded</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Category;
