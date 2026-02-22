"""
Candidate Generation Module - Simple Retrieval Strategy

Implements the simple retrieval candidate generation rules from the paper.
Reference: Paper page 7 and Fig.6 - Simple retrieval strategy combining:
- Recent purchases with time decay
- Popular items by age group
- Co-purchased items (bought together)

This module generates top-N candidates per user for the recommendation pipeline.

Usage:
    python src/retrieval.py --data_dir datasets/processed --sample_users 100
    python src/retrieval.py --data_dir datasets/processed --user_id 12345 --top_n 500
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def time_decay_score(x: float, a: float = 1.0, b: float = 1.0, c: float = 0.1, d: float = 0.0) -> float:
    """
    Calculate time decay score for recency-based recommendations.
    
    Formula from paper (page 7):
        r = a / sqrt(x) + b * exp(-c*x) - d
    
    Where x is the number of days since purchase.
    
    Args:
        x: Days since purchase (must be > 0)
        a: Coefficient for inverse square root term (default: 1.0)
        b: Coefficient for exponential decay term (default: 1.0)
        c: Decay rate for exponential term (default: 0.1)
        d: Offset term (default: 0.0)
        
    Returns:
        Time decay score (higher = more recent)
        
    Example:
        >>> time_decay_score(1)  # 1 day ago
        2.9048...
        >>> time_decay_score(7)  # 7 days ago
        0.8738...
    """
    if x <= 0:
        x = 0.01  # Avoid division by zero
    
    score = a / np.sqrt(x) + b * np.exp(-c * x) - d
    return max(0.0, score)  # Ensure non-negative


def recent_items(
    user_id: str,
    transactions_df: pd.DataFrame,
    days: int = 7,
    max_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Get recently purchased items for a user with time decay scoring.
    
    Args:
        user_id: Customer ID
        transactions_df: Transactions DataFrame with columns [customer_id, article_id, t_dat]
        days: Number of days to look back (default: 7)
        max_date: Reference date for recency calculation (default: max date in transactions)
        
    Returns:
        DataFrame with columns [article_id, score, reason]
        Score is based on time decay formula from paper
    """
    # Filter user transactions
    user_txns = transactions_df[transactions_df['customer_id'] == user_id].copy()
    
    if user_txns.empty:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Get reference date
    if max_date is None:
        max_date = transactions_df['t_dat'].max()
    
    # Calculate days since purchase
    user_txns['days_since'] = (max_date - user_txns['t_dat']).dt.days
    
    # Filter to recent window
    recent = user_txns[user_txns['days_since'] <= days].copy()
    
    if recent.empty:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Apply time decay scoring
    recent['score'] = recent['days_since'].apply(time_decay_score)
    
    # Aggregate by article (user may have purchased same item multiple times)
    result = recent.groupby('article_id')['score'].max().reset_index()
    result['reason'] = f'recent_{days}d'
    
    return result[['article_id', 'score', 'reason']]


def popular_by_age(
    age_bin: str,
    transactions_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    k: int = 100,
    window_days: int = 7,
    max_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Get top-k popular items purchased by users in the same age group.
    
    Reference: Paper page 7 - Age-based popularity for cold-start and diversity
    
    Args:
        age_bin: Age bin category (e.g., '18-25', '26-35')
        transactions_df: Transactions DataFrame
        customers_df: Customers DataFrame with age_bin column
        k: Number of top popular items to return (default: 100)
        window_days: Time window for popularity calculation (default: 7)
        max_date: Reference date (default: max date in transactions)
        
    Returns:
        DataFrame with columns [article_id, score, reason]
        Score is normalized popularity count
    """
    if max_date is None:
        max_date = transactions_df['t_dat'].max()
    
    # Get customers in same age bin
    age_customers = customers_df[customers_df['age_bin'] == age_bin]['customer_id'].unique()
    
    if len(age_customers) == 0:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Filter transactions to age group and time window
    cutoff_date = max_date - pd.Timedelta(days=window_days)
    age_txns = transactions_df[
        (transactions_df['customer_id'].isin(age_customers)) &
        (transactions_df['t_dat'] >= cutoff_date)
    ]
    
    if age_txns.empty:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Count purchases per article
    popularity = age_txns['article_id'].value_counts().head(k).reset_index()
    popularity.columns = ['article_id', 'count']
    
    # Normalize scores to [0, 1]
    max_count = popularity['count'].max()
    popularity['score'] = popularity['count'] / max_count if max_count > 0 else 0.0
    popularity['reason'] = f'popular_age_{age_bin}'
    
    return popularity[['article_id', 'score', 'reason']]


def bought_together(
    item_id: str,
    transactions_df: pd.DataFrame,
    top_k: int = 50
) -> pd.DataFrame:
    """
    Get items frequently bought together with the given item (market basket analysis).
    
    Reference: Paper page 7 - Co-purchase patterns for complementary recommendations
    
    Args:
        item_id: Article ID to find co-purchases for
        transactions_df: Transactions DataFrame with [customer_id, article_id, t_dat]
        top_k: Number of top co-purchased items to return (default: 50)
        
    Returns:
        DataFrame with columns [article_id, score, reason]
        Score is normalized co-occurrence count
    """
    # Find customers who bought this item
    item_customers = transactions_df[
        transactions_df['article_id'] == item_id
    ]['customer_id'].unique()
    
    if len(item_customers) == 0:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Get all purchases by these customers
    customer_purchases = transactions_df[
        transactions_df['customer_id'].isin(item_customers)
    ]
    
    # Count co-occurrences (exclude the original item)
    co_purchases = customer_purchases[
        customer_purchases['article_id'] != item_id
    ]['article_id'].value_counts().head(top_k).reset_index()
    co_purchases.columns = ['article_id', 'count']
    
    if co_purchases.empty:
        return pd.DataFrame(columns=['article_id', 'score', 'reason'])
    
    # Normalize scores
    max_count = co_purchases['count'].max()
    co_purchases['score'] = co_purchases['count'] / max_count if max_count > 0 else 0.0
    co_purchases['reason'] = f'bought_together_{item_id[:6]}'
    
    return co_purchases[['article_id', 'score', 'reason']]



def get_candidates_for_user(
    user_id: str,
    transactions_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    articles_df: pd.DataFrame,
    top_n: int = 500,
    params: Optional[Dict] = None,
    use_cache: bool = True,
    cache_dir: str = "datasets/cache"
) -> pd.DataFrame:
    """
    Generate top-N candidates for a user using multiple retrieval strategies.
    
    Combines multiple candidate sources as per paper (page 7, Fig.6):
    1. Recent purchases (3 days and 7 days windows)
    2. Popular items by age group
    3. Co-purchased items (bought together)
    
    Args:
        user_id: Customer ID
        transactions_df: Processed transactions DataFrame
        customers_df: Processed customers DataFrame
        articles_df: Processed articles DataFrame
        top_n: Number of top candidates to return (default: 500)
        params: Optional dict with parameters for retrieval rules
        use_cache: Whether to use cached popularity data (default: True)
        cache_dir: Directory for caching intermediate results
        
    Returns:
        DataFrame with columns [user_id, article_id, score, reason, rule_scores_json]
        Sorted by score descending
    """
    if params is None:
        params = {
            'recent_days_short': 3,
            'recent_days_long': 7,
            'popular_k': 200,
            'popular_window': 7,
            'bought_together_k': 50,
            'weight_recent': 0.4,
            'weight_bought_together': 0.3,
            'weight_popular': 0.3
        }
    
    logger.info(f"Generating candidates for user {user_id}")
    
    # Get user info
    user_info = customers_df[customers_df['customer_id'] == user_id]
    if user_info.empty:
        logger.warning(f"User {user_id} not found in customers dataset")
        return pd.DataFrame(columns=['user_id', 'article_id', 'score', 'reason', 'rule_scores_json'])
    
    age_bin = user_info['age_bin'].iloc[0] if 'age_bin' in user_info.columns else None
    max_date = transactions_df['t_dat'].max()
    
    all_candidates = []
    
    # 1. Recent purchases (short window)
    logger.debug(f"Fetching recent items ({params['recent_days_short']} days)")
    recent_short = recent_items(user_id, transactions_df, days=params['recent_days_short'], max_date=max_date)
    if not recent_short.empty:
        recent_short['rule'] = 'recent_short'
        all_candidates.append(recent_short)
    
    # 2. Recent purchases (long window)
    logger.debug(f"Fetching recent items ({params['recent_days_long']} days)")
    recent_long = recent_items(user_id, transactions_df, days=params['recent_days_long'], max_date=max_date)
    if not recent_long.empty:
        recent_long['rule'] = 'recent_long'
        all_candidates.append(recent_long)
    
    # 3. Popular by age group
    if age_bin and pd.notna(age_bin):
        cache_file = Path(cache_dir) / f"popular_age_{age_bin}_{params['popular_window']}d.csv"
        
        if use_cache and cache_file.exists():
            logger.debug(f"Loading cached popular items for age {age_bin}")
            popular = pd.read_csv(cache_file)
        else:
            logger.debug(f"Computing popular items for age {age_bin}")
            popular = popular_by_age(
                age_bin,
                transactions_df,
                customers_df,
                k=params['popular_k'],
                window_days=params['popular_window'],
                max_date=max_date
            )
            # Cache the result
            if use_cache and not popular.empty:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                popular.to_csv(cache_file, index=False)
                logger.debug(f"Cached popular items to {cache_file}")
        
        if not popular.empty:
            popular['rule'] = 'popular_age'
            all_candidates.append(popular)
    
    # 4. Bought together for recent purchases
    user_recent_items = transactions_df[
        (transactions_df['customer_id'] == user_id) &
        (transactions_df['t_dat'] >= max_date - pd.Timedelta(days=params['recent_days_long']))
    ]['article_id'].unique()
    
    logger.debug(f"Computing bought-together for {len(user_recent_items)} recent items")
    for item_id in user_recent_items[:10]:  # Limit to top 10 recent items to avoid explosion
        bt = bought_together(item_id, transactions_df, top_k=params['bought_together_k'])
        if not bt.empty:
            bt['rule'] = 'bought_together'
            all_candidates.append(bt)
    
    # Combine all candidates
    if not all_candidates:
        logger.warning(f"No candidates found for user {user_id}")
        return pd.DataFrame(columns=['user_id', 'article_id', 'score', 'reason', 'rule_scores_json'])
    
    candidates = pd.concat(all_candidates, ignore_index=True)
    
    # Pivot to get rule-specific scores
    candidates_pivot = candidates.pivot_table(
        index='article_id',
        columns='rule',
        values='score',
        aggfunc='max',
        fill_value=0.0
    ).reset_index()
    
    # Normalize each rule's scores using QuantileTransformer
    rule_columns = [col for col in candidates_pivot.columns if col != 'article_id']
    
    if len(rule_columns) > 0:
        qt = QuantileTransformer(n_quantiles=min(100, len(candidates_pivot)), output_distribution='uniform')
        
        for col in rule_columns:
            if candidates_pivot[col].sum() > 0:  # Only normalize if there are non-zero values
                candidates_pivot[f'{col}_norm'] = qt.fit_transform(candidates_pivot[[col]])
            else:
                candidates_pivot[f'{col}_norm'] = 0.0
        
        # Calculate weighted combined score
        score_components = []
        weights = []
        
        if 'recent_short_norm' in candidates_pivot.columns:
            score_components.append(candidates_pivot['recent_short_norm'])
            weights.append(params['weight_recent'])
        
        if 'recent_long_norm' in candidates_pivot.columns:
            score_components.append(candidates_pivot['recent_long_norm'])
            weights.append(params['weight_recent'] * 0.5)  # Lower weight for longer window
        
        if 'bought_together_norm' in candidates_pivot.columns:
            score_components.append(candidates_pivot['bought_together_norm'])
            weights.append(params['weight_bought_together'])
        
        if 'popular_age_norm' in candidates_pivot.columns:
            score_components.append(candidates_pivot['popular_age_norm'])
            weights.append(params['weight_popular'])
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Compute weighted sum
        candidates_pivot['score'] = sum(w * comp for w, comp in zip(weights, score_components))
    else:
        candidates_pivot['score'] = 0.0
    
    # Create rule_scores_json
    rule_scores = {}
    for col in rule_columns:
        rule_scores[col] = candidates_pivot[col].tolist()
    
    candidates_pivot['rule_scores_json'] = candidates_pivot.apply(
        lambda row: json.dumps({col: float(row[col]) for col in rule_columns}),
        axis=1
    )
    
    # Get primary reason (rule with highest score)
    candidates_pivot['reason'] = candidates_pivot[rule_columns].idxmax(axis=1)
    
    # Add user_id
    candidates_pivot['user_id'] = user_id
    
    # Sort by score and take top N
    result = candidates_pivot.nlargest(top_n, 'score')[
        ['user_id', 'article_id', 'score', 'reason', 'rule_scores_json']
    ].reset_index(drop=True)
    
    logger.info(f"Generated {len(result)} candidates for user {user_id}")
    
    return result


def save_candidates(
    user_id: str,
    candidates_df: pd.DataFrame,
    out_dir: str = "datasets/candidates"
) -> None:
    """
    Save candidate recommendations for a user to CSV.
    
    Args:
        user_id: Customer ID
        candidates_df: DataFrame with candidate recommendations
        out_dir: Output directory for candidate files (default: datasets/candidates)
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    file_path = out_path / f"{user_id}.csv"
    candidates_df.to_csv(file_path, index=False)
    
    logger.info(f"Saved {len(candidates_df)} candidates to {file_path}")


def load_processed_data(data_dir: str = "datasets/processed") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load processed datasets for candidate generation.
    
    Args:
        data_dir: Directory containing processed CSV files
        
    Returns:
        Tuple of (transactions_df, customers_df, articles_df)
    """
    logger.info(f"Loading processed data from {data_dir}")
    
    data_path = Path(data_dir)
    
    transactions = pd.read_csv(data_path / 'processed_transactions.csv')
    transactions['t_dat'] = pd.to_datetime(transactions['t_dat'])
    transactions['customer_id'] = transactions['customer_id'].astype(str)
    transactions['article_id'] = transactions['article_id'].astype(str)
    logger.info(f"Loaded transactions: {transactions.shape}")
    
    customers = pd.read_csv(data_path / 'processed_customers.csv')
    customers['customer_id'] = customers['customer_id'].astype(str)
    logger.info(f"Loaded customers: {customers.shape}")
    
    articles = pd.read_csv(data_path / 'processed_articles.csv')
    articles['article_id'] = articles['article_id'].astype(str)
    logger.info(f"Loaded articles: {articles.shape}")
    
    return transactions, customers, articles


def build_sample_candidates_for_random_user(
    data_dir: str = "datasets/processed",
    top_n: int = 500
) -> pd.DataFrame:
    """
    Helper function to build candidates for a random user (for testing/debugging).
    
    Args:
        data_dir: Directory containing processed data
        top_n: Number of candidates to generate
        
    Returns:
        DataFrame with candidate recommendations
    """
    logger.info("Building sample candidates for random user")
    
    # Load data
    transactions, customers, articles = load_processed_data(data_dir)
    
    # Pick a random user who has transactions
    active_users = transactions['customer_id'].unique()
    random_user = np.random.choice(active_users)
    
    logger.info(f"Selected random user: {random_user}")
    
    # Generate candidates
    candidates = get_candidates_for_user(
        random_user,
        transactions,
        customers,
        articles,
        top_n=top_n
    )
    
    # Print top 10
    logger.info(f"\nTop 10 candidates for user {random_user}:")
    print(candidates.head(10).to_string())
    
    return candidates



def main():
    """
    Main entry point for CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Generate candidate recommendations using simple retrieval strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate candidates for a specific user
  python src/retrieval.py --data_dir datasets/processed --user_id 12345 --top_n 500
  
  # Generate candidates for 100 random users
  python src/retrieval.py --data_dir datasets/processed --sample_users 100
  
  # Test with random user
  python src/retrieval.py --data_dir datasets/processed --test
        """
    )
    
    parser.add_argument(
        '--data_dir',
        type=str,
        default='datasets/processed',
        help='Path to directory containing processed CSV files'
    )
    
    parser.add_argument(
        '--user_id',
        type=str,
        default=None,
        help='Specific user ID to generate candidates for'
    )
    
    parser.add_argument(
        '--top_n',
        type=int,
        default=500,
        help='Number of top candidates to generate per user (default: 500)'
    )
    
    parser.add_argument(
        '--sample_users',
        type=int,
        default=None,
        help='Generate candidates for N random users'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test with random user and print top 10 candidates'
    )
    
    parser.add_argument(
        '--no_cache',
        action='store_true',
        help='Disable caching of intermediate results'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='datasets/candidates',
        help='Output directory for candidate files (default: datasets/candidates)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("CANDIDATE GENERATION - SIMPLE RETRIEVAL STRATEGY")
    logger.info("=" * 60)
    logger.info("Reference: Paper page 7 and Fig.6")
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Top N candidates: {args.top_n}")
    logger.info(f"Cache enabled: {not args.no_cache}")
    
    try:
        # Test mode
        if args.test:
            logger.info("\n--- TEST MODE: Random User ---")
            build_sample_candidates_for_random_user(args.data_dir, args.top_n)
            return 0
        
        # Load data
        transactions, customers, articles = load_processed_data(args.data_dir)
        
        # Single user mode
        if args.user_id:
            logger.info(f"\n--- Generating candidates for user {args.user_id} ---")
            
            candidates = get_candidates_for_user(
                args.user_id,
                transactions,
                customers,
                articles,
                top_n=args.top_n,
                use_cache=not args.no_cache
            )
            
            if candidates.empty:
                logger.warning(f"No candidates generated for user {args.user_id}")
                return 1
            
            # Save candidates
            save_candidates(args.user_id, candidates, args.output_dir)
            
            # Print top 10
            logger.info(f"\nTop 10 candidates for user {args.user_id}:")
            print(candidates.head(10).to_string())
            
            return 0
        
        # Sample users mode
        if args.sample_users:
            logger.info(f"\n--- Generating candidates for {args.sample_users} random users ---")
            
            # Get active users (users with transactions)
            active_users = transactions['customer_id'].unique()
            
            if len(active_users) < args.sample_users:
                logger.warning(f"Only {len(active_users)} active users available, using all")
                sample_users = active_users
            else:
                sample_users = np.random.choice(active_users, size=args.sample_users, replace=False)
            
            logger.info(f"Selected {len(sample_users)} users for candidate generation")
            
            # Generate candidates for each user
            success_count = 0
            for i, user_id in enumerate(sample_users, 1):
                try:
                    logger.info(f"[{i}/{len(sample_users)}] Processing user {user_id}")
                    
                    candidates = get_candidates_for_user(
                        user_id,
                        transactions,
                        customers,
                        articles,
                        top_n=args.top_n,
                        use_cache=not args.no_cache
                    )
                    
                    if not candidates.empty:
                        save_candidates(user_id, candidates, args.output_dir)
                        success_count += 1
                    else:
                        logger.warning(f"No candidates for user {user_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")
                    continue
            
            logger.info("\n" + "=" * 60)
            logger.info("CANDIDATE GENERATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✓ Successfully generated candidates for {success_count}/{len(sample_users)} users")
            logger.info(f"✓ Candidates saved to: {args.output_dir}")
            
            return 0
        
        # No mode specified
        logger.error("Please specify --user_id, --sample_users, or --test")
        parser.print_help()
        return 1
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure processed data exists. Run preprocess_short.py first.")
        return 1
    except Exception as e:
        logger.error(f"Error during candidate generation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
