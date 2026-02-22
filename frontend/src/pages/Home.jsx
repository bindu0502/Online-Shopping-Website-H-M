import { useState, useEffect, useRef, useCallback } from 'react';
import API from '../api/axios';
import ProductCard from '../components/ProductCard';

function Home() {
  const [products, setProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshingRecommendations, setRefreshingRecommendations] = useState(false);
  const [refreshingProducts, setRefreshingProducts] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState('');

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

  useEffect(() => {
    fetchRecommendations();
    // Randomize products on initial load
    fetchProducts(true);
  }, []);

  useEffect(() => {
    if (page > 1) {
      fetchProducts();
    }
  }, [page]);

  const fetchProducts = async () => {
    if (loading) return;
    
    try {
      setLoading(true);
      setError('');
      
      const response = await API.get('/products/', {
        params: {
          page,
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
      console.error('Products error:', err);
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshingRecommendations(true);
      }
      
      const response = await API.get('/recommend/me?limit=12');
      
      if (response.data && Array.isArray(response.data.recommendations)) {
        setRecommendations(response.data.recommendations);
      }
    } catch (err) {
      console.log('ML recommendations not available');
      setRecommendations([]);
    } finally {
      if (isRefresh) {
        setRefreshingRecommendations(false);
      }
    }
  };

  const handleRefreshRecommendations = () => {
    fetchRecommendations(true);
  };

  if (error && products.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
        <button
          onClick={() => {
            setPage(1);
            setProducts([]);
            setHasMore(true);
            fetchProducts();
          }}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {recommendations.length > 0 && (
        <div className="mb-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Recommended For You
            </h2>
            <button
              onClick={handleRefreshRecommendations}
              disabled={refreshingRecommendations}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                refreshingRecommendations
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-700'
              }`}
              title="Refresh recommendations"
            >
              <svg
                className={`w-4 h-4 ${refreshingRecommendations ? 'animate-spin' : ''}`}
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
              {refreshingRecommendations ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {recommendations.map((product) => (
              <ProductCard key={product.article_id} product={product} />
            ))}
          </div>
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            All Products
          </h2>
          {total > 0 && (
            <span className="text-sm text-gray-600">
              Showing {products.length} of {total.toLocaleString()} products
            </span>
          )}
        </div>
        
        {products.length === 0 && !loading ? (
          <div className="text-center py-12">
            <p className="text-xl text-gray-600">No products found</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
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
                <p className="text-lg text-gray-600">🎉 You have reached the end.</p>
                <p className="text-sm text-gray-500 mt-2">All {total.toLocaleString()} products loaded</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Home;
