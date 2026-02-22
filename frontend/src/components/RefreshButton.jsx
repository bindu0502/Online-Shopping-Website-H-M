import { useState } from 'react';

function RefreshButton({ 
  onRefresh, 
  loading = false, 
  disabled = false, 
  size = 'md',
  variant = 'primary',
  className = '' 
}) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleClick = async () => {
    if (disabled || loading || isRefreshing) return;
    
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  const isLoading = loading || isRefreshing;

  // Size classes
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  // Icon size classes
  const iconSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  // Variant classes
  const variantClasses = {
    primary: isLoading || disabled
      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
      : 'bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700',
    secondary: isLoading || disabled
      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
      : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:text-indigo-700',
    minimal: isLoading || disabled
      ? 'text-gray-400 cursor-not-allowed'
      : 'text-gray-600 hover:text-gray-800'
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`
        flex items-center gap-2 rounded-lg font-medium transition-colors
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      title="Refresh"
    >
      <svg
        className={`${iconSizeClasses[size]} ${isLoading ? 'animate-spin' : ''}`}
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
      {isLoading ? 'Refreshing...' : 'Refresh'}
    </button>
  );
}

export default RefreshButton;