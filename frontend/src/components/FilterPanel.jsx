import { useState, useEffect } from 'react';

function FilterPanel({ filters, onFilterChange }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [priceRange, setPriceRange] = useState([
    filters.min_price ? parseInt(filters.min_price) : 0,
    filters.max_price ? parseInt(filters.max_price) : 200
  ]);
  const [localFilters, setLocalFilters] = useState({
    min_price: filters.min_price || '',
    max_price: filters.max_price || '',
    sort: filters.sort || ''
  });

  // Update local filters when props change
  useEffect(() => {
    setLocalFilters({
      min_price: filters.min_price || '',
      max_price: filters.max_price || '',
      sort: filters.sort || ''
    });
    setPriceRange([
      filters.min_price ? parseInt(filters.min_price) : 0,
      filters.max_price ? parseInt(filters.max_price) : 200
    ]);
  }, [filters]);

  const handlePriceRangeChange = (index, value) => {
    const newRange = [...priceRange];
    newRange[index] = parseInt(value);
    
    // Ensure min doesn't exceed max
    if (index === 0 && newRange[0] > newRange[1]) {
      newRange[0] = newRange[1];
    }
    if (index === 1 && newRange[1] < newRange[0]) {
      newRange[1] = newRange[0];
    }
    
    setPriceRange(newRange);
    
    const newFilters = {
      ...localFilters,
      min_price: newRange[0] > 0 ? newRange[0].toString() : '',
      max_price: newRange[1] < 200 ? newRange[1].toString() : ''
    };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleSortChange = (value) => {
    const newFilters = { ...localFilters, sort: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    const resetFilters = {
      min_price: '',
      max_price: '',
      sort: ''
    };
    setPriceRange([0, 200]);
    setLocalFilters(resetFilters);
    onFilterChange(resetFilters);
  };

  const hasActiveFilters = 
    localFilters.min_price || 
    localFilters.max_price || 
    localFilters.sort;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
      {/* Header - Always Visible */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{isExpanded ? '🔽' : '▶️'}</span>
          <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
            <span>Filters</span>
            {hasActiveFilters && (
              <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">
                Active
              </span>
            )}
          </h2>
        </div>
        <div className="flex items-center gap-3">
          {hasActiveFilters && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleReset();
              }}
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Reset
            </button>
          )}
          <span className="text-xs text-gray-500">
            {isExpanded ? 'Click to collapse' : 'Click to expand'}
          </span>
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
            {/* Price Range Slider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Price Range: ${priceRange[0]} - ${priceRange[1] === 200 ? '200+' : priceRange[1]}
              </label>
              
              {/* Min Price Slider */}
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-gray-600 w-16">Min: ${priceRange[0]}</span>
                  <input
                    type="range"
                    min="0"
                    max="200"
                    step="5"
                    value={priceRange[0]}
                    onChange={(e) => handlePriceRangeChange(0, e.target.value)}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>
              </div>

              {/* Max Price Slider */}
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-gray-600 w-16">Max: ${priceRange[1] === 200 ? '200+' : priceRange[1]}</span>
                  <input
                    type="range"
                    min="0"
                    max="200"
                    step="5"
                    value={priceRange[1]}
                    onChange={(e) => handlePriceRangeChange(1, e.target.value)}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>
              </div>

              {/* Quick Price Buttons */}
              <div className="flex flex-wrap gap-2 mt-3">
                <button
                  onClick={() => {
                    setPriceRange([0, 25]);
                    handlePriceRangeChange(0, 0);
                    handlePriceRangeChange(1, 25);
                  }}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-full hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                >
                  Under $25
                </button>
                <button
                  onClick={() => {
                    setPriceRange([25, 50]);
                    handlePriceRangeChange(0, 25);
                    handlePriceRangeChange(1, 50);
                  }}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-full hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                >
                  $25-$50
                </button>
                <button
                  onClick={() => {
                    setPriceRange([50, 100]);
                    handlePriceRangeChange(0, 50);
                    handlePriceRangeChange(1, 100);
                  }}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-full hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                >
                  $50-$100
                </button>
                <button
                  onClick={() => {
                    setPriceRange([100, 200]);
                    handlePriceRangeChange(0, 100);
                    handlePriceRangeChange(1, 200);
                  }}
                  className="px-2 py-1 text-xs border border-gray-300 rounded-full hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
                >
                  $100+
                </button>
              </div>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Sort By
              </label>
              <select
                value={localFilters.sort}
                onChange={(e) => handleSortChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-sm"
              >
                <option value="">Default Order</option>
                <option value="price_asc">💰 Price: Low to High</option>
                <option value="price_desc">💎 Price: High to Low</option>
                <option value="popular">⭐ Popular Items</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FilterPanel;
