"""
Feature Engineering Module

Builds features for (user_id, article_id) candidate pairs for the recommendation model.
Combines user features, item features, and user-item interaction features.

Usage:
    python src/features.py --data_dir datasets --sample_users 10
    python src/features.py --data_dir datasets --user_id 12345
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import QuantileTransformer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_processed_data(data_dir: str = "datasets/processed") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load processed datasets for feature engineering.
    
    Args:
        data_dir: Directory containing processed CSV files
        
    Returns:
        Tuple of (transactions_df, customers_df, articles_df)
    """
    logger.info(f"Loading processed data from {data_dir}")
    
    data_path = Path(data_dir)
    
    # Load transactions
    transactions = pd.read_csv(data_path / 'processed_transactions.csv')
    transactions['t_dat'] = pd.to_datetime(transactions['t_dat'])
    transactions['customer_id'] = transactions['customer_id'].astype(str)
    transactions['article_id'] = transactions['article_id'].astype(str)
    logger.info(f"Loaded transactions: {transactions.shape}")
    
    # Load customers
    customers = pd.read_csv(data_path / 'processed_customers.csv')
    customers['customer_id'] = customers['customer_id'].astype(str)
    logger.info(f"Loaded customers: {customers.shape}")
    
    # Load articles
    articles = pd.read_csv(data_path / 'processed_articles.csv')
    articles['article_id'] = articles['article_id'].astype(str)
    logger.info(f"Loaded articles: {articles.shape}")
    
    return transactions, customers, articles


def load_candidates_for_user(user_id: str, candidates_dir: str = "datasets/candidates") -> pd.DataFrame:
    """
    Load candidate recommendations for a specific user.
    
    Args:
        user_id: Customer ID
        candidates_dir: Directory containing candidate CSV files
        
    Returns:
        DataFrame with candidate recommendations
        
    Raises:
        FileNotFoundError: If candidate file doesn't exist
    """
    candidates_path = Path(candidates_dir) / f"{user_id}.csv"
    
    if not candidates_path.exists():
        raise FileNotFoundError(f"Candidate file not found: {candidates_path}")
    
    candidates = pd.read_csv(candidates_path)
    candidates['user_id'] = candidates['user_id'].astype(str)
    candidates['article_id'] = candidates['article_id'].astype(str)
    
    logger.debug(f"Loaded {len(candidates)} candidates for user {user_id}")
    
    return candidates


def compute_user_features(
    user_id: str,
    transactions_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    max_date: Optional[pd.Timestamp] = None
) -> dict:
    """
    Compute user-level features.
    
    Args:
        user_id: Customer ID
        transactions_df: Transactions DataFrame
        customers_df: Customers DataFrame
        max_date: Reference date for recency calculation
        
    Returns:
        Dictionary with user features
    """
    if max_date is None:
        max_date = transactions_df['t_dat'].max()
    
    # Get user transactions
    user_txns = transactions_df[transactions_df['customer_id'] == user_id]
    
    # User demographics
    user_info = customers_df[customers_df['customer_id'] == user_id]
    age_bin = user_info['age_bin'].iloc[0] if not user_info.empty and 'age_bin' in user_info.columns else 'unknown'
    
    # User purchase behavior
    user_total_purchases = len(user_txns)
    
    if user_total_purchases > 0:
        last_purchase_date = user_txns['t_dat'].max()
        user_recency_days = (max_date - last_purchase_date).days
    else:
        user_recency_days = 9999  # Large value for users with no history
    
    return {
        'user_total_purchases': user_total_purchases,
        'user_recency_days': user_recency_days,
        'user_age_bin': age_bin
    }


def compute_item_features(
    article_ids: List[str],
    transactions_df: pd.DataFrame,
    articles_df: pd.DataFrame,
    max_date: Optional[pd.Timestamp] = None,
    cache_dir: str = "datasets/cache"
) -> pd.DataFrame:
    """
    Compute item-level features for a list of articles.
    
    Uses caching for popularity and price aggregates to improve performance.
    
    Args:
        article_ids: List of article IDs
        transactions_df: Transactions DataFrame
        articles_df: Articles DataFrame
        max_date: Reference date for time windows
        cache_dir: Directory for caching intermediate results
        
    Returns:
        DataFrame with item features indexed by article_id
    """
    if max_date is None:
        max_date = transactions_df['t_dat'].max()
    
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    # Try to load cached item features
    cache_file_7d = cache_path / "item_features_7d.csv"
    cache_file_30d = cache_path / "item_features_30d.csv"
    
    # Compute 7-day popularity
    if cache_file_7d.exists():
        logger.debug("Loading cached 7-day item features")
        item_pop_7d = pd.read_csv(cache_file_7d)
        item_pop_7d['article_id'] = item_pop_7d['article_id'].astype(str)
    else:
        logger.debug("Computing 7-day item popularity")
        cutoff_7d = max_date - pd.Timedelta(days=7)
        txns_7d = transactions_df[transactions_df['t_dat'] >= cutoff_7d]
        item_pop_7d = txns_7d.groupby('article_id').size().reset_index(name='item_popularity_7d')
        item_pop_7d.to_csv(cache_file_7d, index=False)
    
    # Compute 30-day popularity and price
    if cache_file_30d.exists():
        logger.debug("Loading cached 30-day item features")
        item_features_30d = pd.read_csv(cache_file_30d)
        item_features_30d['article_id'] = item_features_30d['article_id'].astype(str)
    else:
        logger.debug("Computing 30-day item features")
        cutoff_30d = max_date - pd.Timedelta(days=30)
        txns_30d = transactions_df[transactions_df['t_dat'] >= cutoff_30d]
        
        item_pop_30d = txns_30d.groupby('article_id').size().reset_index(name='item_popularity_30d')
        
        if 'price' in txns_30d.columns:
            item_price_30d = txns_30d.groupby('article_id')['price'].mean().reset_index(name='item_price_mean_30d')
            item_features_30d = item_pop_30d.merge(item_price_30d, on='article_id', how='left')
        else:
            item_features_30d = item_pop_30d
            item_features_30d['item_price_mean_30d'] = 0.0
        
        item_features_30d.to_csv(cache_file_30d, index=False)
    
    # Merge popularity features
    item_features = item_pop_7d.merge(item_features_30d, on='article_id', how='outer')
    
    # Add article metadata
    article_meta = articles_df[['article_id', 'department_no', 'gender_tag']].copy()
    article_meta.columns = ['article_id', 'item_department_no', 'item_gender_tag']
    
    item_features = item_features.merge(article_meta, on='article_id', how='left')
    
    # Fill missing values
    item_features['item_popularity_7d'] = item_features['item_popularity_7d'].fillna(0).astype(int)
    item_features['item_popularity_30d'] = item_features['item_popularity_30d'].fillna(0).astype(int)
    item_features['item_price_mean_30d'] = item_features['item_price_mean_30d'].fillna(0.0).astype(float)
    item_features['item_department_no'] = item_features['item_department_no'].fillna(-1).astype(int)
    item_features['item_gender_tag'] = item_features['item_gender_tag'].fillna(0).astype(int)
    
    # Filter to requested articles
    item_features = item_features[item_features['article_id'].isin(article_ids)]
    
    return item_features


def compute_interaction_features(
    user_id: str,
    article_ids: List[str],
    transactions_df: pd.DataFrame,
    max_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Compute user-item interaction features.
    
    Args:
        user_id: Customer ID
        article_ids: List of article IDs
        transactions_df: Transactions DataFrame
        max_date: Reference date for time windows
        
    Returns:
        DataFrame with interaction features indexed by article_id
    """
    if max_date is None:
        max_date = transactions_df['t_dat'].max()
    
    # Get user's transaction history
    user_txns = transactions_df[transactions_df['customer_id'] == user_id]
    
    # Recent interaction flag (7 days)
    cutoff_7d = max_date - pd.Timedelta(days=7)
    recent_items = user_txns[user_txns['t_dat'] >= cutoff_7d]['article_id'].unique()
    
    # Get last 3 purchased items
    last_3_items = user_txns.nlargest(3, 't_dat')['article_id'].unique()
    
    # Co-purchase counts with last 3 items
    co_purchase_counts = {}
    for item_id in article_ids:
        # Count how many of the last 3 items were co-purchased with this item
        co_count = 0
        for last_item in last_3_items:
            # Find customers who bought the last_item
            customers_with_last = transactions_df[
                transactions_df['article_id'] == last_item
            ]['customer_id'].unique()
            
            # Check if they also bought the current item
            co_purchased = transactions_df[
                (transactions_df['customer_id'].isin(customers_with_last)) &
                (transactions_df['article_id'] == item_id)
            ]
            co_count += len(co_purchased)
        
        co_purchase_counts[item_id] = co_count
    
    # Build interaction features DataFrame
    interaction_features = pd.DataFrame({
        'article_id': article_ids,
        'recent_interaction_flag_7d': [1 if aid in recent_items else 0 for aid in article_ids],
        'co_purchase_count_with_last3': [co_purchase_counts.get(aid, 0) for aid in article_ids]
    })
    
    return interaction_features



def parse_retrieval_scores(rule_scores_json: str) -> dict:
    """
    Parse retrieval rule scores from JSON string.
    
    Args:
        rule_scores_json: JSON string with rule scores
        
    Returns:
        Dictionary with individual rule scores
    """
    try:
        scores = json.loads(rule_scores_json)
        return {
            'retrieval_recent_score': scores.get('recent_short', 0.0) + scores.get('recent_long', 0.0),
            'retrieval_bought_together_score': scores.get('bought_together', 0.0),
            'retrieval_popular_age_score': scores.get('popular_age', 0.0)
        }
    except (json.JSONDecodeError, TypeError):
        return {
            'retrieval_recent_score': 0.0,
            'retrieval_bought_together_score': 0.0,
            'retrieval_popular_age_score': 0.0
        }


def build_features_for_candidates(
    user_id: str,
    candidates_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    articles_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Build comprehensive features for candidate (user, article) pairs.
    
    Combines:
    - User features (purchase history, demographics)
    - Item features (popularity, price, metadata)
    - User-item interaction features
    - Retrieval rule scores
    
    Args:
        user_id: Customer ID
        candidates_df: DataFrame with candidate recommendations
        transactions_df: Transactions DataFrame
        customers_df: Customers DataFrame
        articles_df: Articles DataFrame
        
    Returns:
        DataFrame with all features, preserving original score and rule_scores_json
    """
    logger.info(f"Building features for user {user_id} with {len(candidates_df)} candidates")
    
    max_date = transactions_df['t_dat'].max()
    article_ids = candidates_df['article_id'].tolist()
    
    # Start with candidates
    features_df = candidates_df.copy()
    
    # 1. User features (same for all candidates)
    logger.debug("Computing user features")
    user_features = compute_user_features(user_id, transactions_df, customers_df, max_date)
    for key, value in user_features.items():
        features_df[key] = value
    
    # 2. Item features
    logger.debug("Computing item features")
    item_features = compute_item_features(article_ids, transactions_df, articles_df, max_date)
    features_df = features_df.merge(item_features, on='article_id', how='left')
    
    # Fill missing item features
    features_df['item_popularity_7d'] = features_df['item_popularity_7d'].fillna(0).astype(int)
    features_df['item_popularity_30d'] = features_df['item_popularity_30d'].fillna(0).astype(int)
    features_df['item_price_mean_30d'] = features_df['item_price_mean_30d'].fillna(0.0).astype(float)
    features_df['item_department_no'] = features_df['item_department_no'].fillna(-1).astype(int)
    features_df['item_gender_tag'] = features_df['item_gender_tag'].fillna(0).astype(int)
    
    # 3. Interaction features
    logger.debug("Computing interaction features")
    interaction_features = compute_interaction_features(user_id, article_ids, transactions_df, max_date)
    features_df = features_df.merge(interaction_features, on='article_id', how='left')
    
    # Fill missing interaction features
    features_df['recent_interaction_flag_7d'] = features_df['recent_interaction_flag_7d'].fillna(0).astype(int)
    features_df['co_purchase_count_with_last3'] = features_df['co_purchase_count_with_last3'].fillna(0).astype(int)
    
    # 4. Parse retrieval scores
    logger.debug("Parsing retrieval scores")
    if 'rule_scores_json' in features_df.columns:
        retrieval_scores = features_df['rule_scores_json'].apply(parse_retrieval_scores)
        retrieval_scores_df = pd.DataFrame(retrieval_scores.tolist())
        features_df = pd.concat([features_df, retrieval_scores_df], axis=1)
    else:
        features_df['retrieval_recent_score'] = 0.0
        features_df['retrieval_bought_together_score'] = 0.0
        features_df['retrieval_popular_age_score'] = 0.0
    
    # Convert age_bin to category
    if 'user_age_bin' in features_df.columns:
        features_df['user_age_bin'] = features_df['user_age_bin'].astype('category')
    
    logger.info(f"Built features: {features_df.shape}")
    
    return features_df


def quantile_normalize_features(
    df: pd.DataFrame,
    cols_to_normalize: List[str],
    n_quantiles: int = 100
) -> pd.DataFrame:
    """
    Apply quantile normalization to specified feature columns.
    
    Uses sklearn's QuantileTransformer to map features to uniform distribution.
    Handles small sample sizes by reducing n_quantiles if needed.
    
    Args:
        df: DataFrame with features
        cols_to_normalize: List of column names to normalize
        n_quantiles: Number of quantiles (default: 100)
        
    Returns:
        DataFrame with normalized features (original columns replaced)
    """
    logger.info(f"Applying quantile normalization to {len(cols_to_normalize)} columns")
    
    df_normalized = df.copy()
    
    # Filter to columns that exist
    cols_to_normalize = [col for col in cols_to_normalize if col in df.columns]
    
    if not cols_to_normalize:
        logger.warning("No columns to normalize")
        return df_normalized
    
    # Adjust n_quantiles for small sample sizes
    n_samples = len(df)
    n_quantiles = min(n_quantiles, n_samples)
    
    if n_quantiles < 10:
        logger.warning(f"Sample size too small ({n_samples}), skipping normalization")
        return df_normalized
    
    # Apply quantile transformation
    qt = QuantileTransformer(n_quantiles=n_quantiles, output_distribution='uniform', random_state=42)
    
    for col in cols_to_normalize:
        if df[col].nunique() > 1:  # Only normalize if there's variance
            try:
                df_normalized[col] = qt.fit_transform(df[[col]])
                logger.debug(f"Normalized {col}")
            except Exception as e:
                logger.warning(f"Failed to normalize {col}: {e}")
        else:
            logger.debug(f"Skipping {col} (no variance)")
    
    return df_normalized


def pipeline_build_features_for_users(
    user_list: Optional[List[str]] = None,
    candidates_dir: str = "datasets/candidates",
    data_dir: str = "datasets/processed",
    out_path: str = "datasets/features/features_all.csv",
    overwrite: bool = False
) -> pd.DataFrame:
    """
    Build features for multiple users and save to a single CSV file.
    
    Args:
        user_list: List of user IDs to process (if None, process all candidate files)
        candidates_dir: Directory containing candidate CSV files
        data_dir: Directory containing processed data
        out_path: Output path for combined features CSV
        overwrite: Whether to overwrite existing output file
        
    Returns:
        Combined DataFrame with all features
    """
    logger.info("=" * 60)
    logger.info("FEATURE ENGINEERING PIPELINE")
    logger.info("=" * 60)
    
    # Check if output exists
    out_file = Path(out_path)
    if out_file.exists() and not overwrite:
        logger.info(f"Output file already exists: {out_path}")
        logger.info("Loading existing features (use --overwrite to rebuild)")
        return pd.read_csv(out_path)
    
    # Create output directory
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load processed data
    transactions, customers, articles = load_processed_data(data_dir)
    
    # Get list of users to process
    if user_list is None:
        candidate_files = list(Path(candidates_dir).glob("*.csv"))
        user_list = [f.stem for f in candidate_files]
        logger.info(f"Found {len(user_list)} candidate files")
    else:
        logger.info(f"Processing {len(user_list)} specified users")
    
    if not user_list:
        logger.error("No users to process")
        return pd.DataFrame()
    
    # Build features for each user
    all_features = []
    success_count = 0
    
    for i, user_id in enumerate(user_list, 1):
        try:
            logger.info(f"[{i}/{len(user_list)}] Processing user {user_id}")
            
            # Load candidates
            candidates = load_candidates_for_user(user_id, candidates_dir)
            
            if candidates.empty:
                logger.warning(f"No candidates for user {user_id}")
                continue
            
            # Build features
            features = build_features_for_candidates(
                user_id,
                candidates,
                transactions,
                customers,
                articles
            )
            
            all_features.append(features)
            success_count += 1
            
        except FileNotFoundError:
            logger.warning(f"Candidate file not found for user {user_id}")
            continue
        except Exception as e:
            logger.error(f"Error processing user {user_id}: {e}")
            continue
    
    # Combine all features
    if not all_features:
        logger.error("No features generated")
        return pd.DataFrame()
    
    logger.info(f"\nCombining features from {len(all_features)} users")
    combined_features = pd.concat(all_features, ignore_index=True)
    
    # Save to CSV
    combined_features.to_csv(out_path, index=False)
    logger.info(f"Saved features to: {out_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("FEATURE ENGINEERING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✓ Processed {success_count}/{len(user_list)} users")
    logger.info(f"✓ Total feature rows: {len(combined_features):,}")
    logger.info(f"✓ Total feature columns: {len(combined_features.columns)}")
    logger.info(f"✓ Output: {out_path}")
    
    return combined_features


def build_and_show_sample(
    user_id: Optional[str] = None,
    data_dir: str = "datasets/processed",
    candidates_dir: str = "datasets/candidates"
) -> pd.DataFrame:
    """
    Helper function to build features for a user and display sample (for testing).
    
    Args:
        user_id: Customer ID (if None, picks random user from candidates)
        data_dir: Directory containing processed data
        candidates_dir: Directory containing candidate files
        
    Returns:
        DataFrame with features
    """
    logger.info("Building sample features for testing")
    
    # Load data
    transactions, customers, articles = load_processed_data(data_dir)
    
    # Pick random user if not specified
    if user_id is None:
        candidate_files = list(Path(candidates_dir).glob("*.csv"))
        if not candidate_files:
            logger.error("No candidate files found")
            return pd.DataFrame()
        
        random_file = np.random.choice(candidate_files)
        user_id = random_file.stem
        logger.info(f"Selected random user: {user_id}")
    
    # Load candidates
    candidates = load_candidates_for_user(user_id, candidates_dir)
    
    # Build features
    features = build_features_for_candidates(
        user_id,
        candidates,
        transactions,
        customers,
        articles
    )
    
    # Display sample
    logger.info(f"\nFeatures shape: {features.shape}")
    logger.info(f"Feature columns: {features.columns.tolist()}")
    logger.info(f"\nTop 10 rows:")
    print(features.head(10).to_string())
    
    return features



def main():
    """
    Main entry point for CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Build features for candidate recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build features for all users with candidates
  python src/features.py --data_dir datasets
  
  # Build features for specific user
  python src/features.py --data_dir datasets --user_id 12345
  
  # Build features for 10 random users
  python src/features.py --data_dir datasets --sample_users 10
  
  # Test with random user
  python src/features.py --data_dir datasets --test
  
  # Overwrite existing features
  python src/features.py --data_dir datasets --overwrite
        """
    )
    
    parser.add_argument(
        '--data_dir',
        type=str,
        default='datasets',
        help='Base data directory (default: datasets)'
    )
    
    parser.add_argument(
        '--candidates_dir',
        type=str,
        default=None,
        help='Directory containing candidate files (default: {data_dir}/candidates)'
    )
    
    parser.add_argument(
        '--user_id',
        type=str,
        default=None,
        help='Specific user ID to build features for'
    )
    
    parser.add_argument(
        '--sample_users',
        type=int,
        default=None,
        help='Build features for N random users'
    )
    
    parser.add_argument(
        '--out_path',
        type=str,
        default=None,
        help='Output path for features CSV (default: {data_dir}/features/features_all.csv)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output file'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test with random user and display features'
    )
    
    args = parser.parse_args()
    
    # Set default paths
    if args.candidates_dir is None:
        args.candidates_dir = f"{args.data_dir}/candidates"
    
    if args.out_path is None:
        args.out_path = f"{args.data_dir}/features/features_all.csv"
    
    processed_dir = f"{args.data_dir}/processed"
    
    logger.info("=" * 60)
    logger.info("FEATURE ENGINEERING MODULE")
    logger.info("=" * 60)
    logger.info(f"Data directory: {processed_dir}")
    logger.info(f"Candidates directory: {args.candidates_dir}")
    logger.info(f"Output path: {args.out_path}")
    
    try:
        # Test mode
        if args.test:
            logger.info("\n--- TEST MODE: Random User ---")
            build_and_show_sample(
                user_id=None,
                data_dir=processed_dir,
                candidates_dir=args.candidates_dir
            )
            return 0
        
        # Single user mode
        if args.user_id:
            logger.info(f"\n--- Building features for user {args.user_id} ---")
            
            transactions, customers, articles = load_processed_data(processed_dir)
            candidates = load_candidates_for_user(args.user_id, args.candidates_dir)
            
            features = build_features_for_candidates(
                args.user_id,
                candidates,
                transactions,
                customers,
                articles
            )
            
            # Save to user-specific file
            user_out_path = Path(args.data_dir) / "features" / f"{args.user_id}_features.csv"
            user_out_path.parent.mkdir(parents=True, exist_ok=True)
            features.to_csv(user_out_path, index=False)
            
            logger.info(f"\nSaved features to: {user_out_path}")
            logger.info(f"Features shape: {features.shape}")
            logger.info(f"\nTop 10 rows:")
            print(features.head(10).to_string())
            
            return 0
        
        # Sample users mode
        if args.sample_users:
            logger.info(f"\n--- Building features for {args.sample_users} random users ---")
            
            # Get random sample of candidate files
            candidate_files = list(Path(args.candidates_dir).glob("*.csv"))
            
            if len(candidate_files) < args.sample_users:
                logger.warning(f"Only {len(candidate_files)} candidate files available")
                sample_files = candidate_files
            else:
                sample_files = np.random.choice(candidate_files, size=args.sample_users, replace=False)
            
            user_list = [f.stem for f in sample_files]
            
            features = pipeline_build_features_for_users(
                user_list=user_list,
                candidates_dir=args.candidates_dir,
                data_dir=processed_dir,
                out_path=args.out_path,
                overwrite=args.overwrite
            )
            
            return 0
        
        # Default: process all users
        logger.info("\n--- Building features for all users ---")
        
        features = pipeline_build_features_for_users(
            user_list=None,
            candidates_dir=args.candidates_dir,
            data_dir=processed_dir,
            out_path=args.out_path,
            overwrite=args.overwrite
        )
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure processed data and candidates exist")
        return 1
    except Exception as e:
        logger.error(f"Error during feature engineering: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
