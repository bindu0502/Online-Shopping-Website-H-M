"""
Training Data Creation Module

Creates labeled training and validation datasets from candidates and features.
Implements temporal labeling and negative sampling for recommendation model training.

Usage:
    python src/create_training_data.py --data_dir datasets
    python src/create_training_data.py --data_dir datasets --neg_pos_ratio 5 --val_fraction 0.15
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def calculate_default_windows(transactions_df: pd.DataFrame) -> dict:
    """
    Calculate default time windows for training and target periods.
    
    Default logic:
    - train_window_end: last_date - 7 days
    - train_window_start: train_window_end - 28 days (4 weeks)
    - target_start: last_date - 6 days
    - target_end: last_date
    
    Args:
        transactions_df: Transactions DataFrame with t_dat column
        
    Returns:
        Dictionary with window dates
    """
    last_date = transactions_df['t_dat'].max()
    
    windows = {
        'target_end': last_date,
        'target_start': last_date - pd.Timedelta(days=6),
        'train_window_end': last_date - pd.Timedelta(days=7),
        'train_window_start': last_date - pd.Timedelta(days=35)  # 4 weeks before train_window_end
    }
    
    logger.info("Calculated default time windows:")
    for key, value in windows.items():
        logger.info(f"  {key}: {value.date()}")
    
    return windows


def label_candidate_rows(
    candidates_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    target_start: pd.Timestamp,
    target_end: pd.Timestamp
) -> pd.DataFrame:
    """
    Label candidate (user, article) pairs based on future purchases.
    
    A pair is labeled 1 if the user purchased the article in [target_start, target_end],
    otherwise 0.
    
    Args:
        candidates_df: DataFrame with user_id and article_id columns
        transactions_df: Transactions DataFrame
        target_start: Start of target period
        target_end: End of target period
        
    Returns:
        DataFrame with added 'label' column (0 or 1)
    """
    logger.info(f"Labeling candidates for target period: {target_start.date()} to {target_end.date()}")
    
    # Filter transactions to target period
    target_txns = transactions_df[
        (transactions_df['t_dat'] >= target_start) &
        (transactions_df['t_dat'] <= target_end)
    ].copy()
    
    logger.info(f"Found {len(target_txns):,} transactions in target period")
    
    # Create set of positive (user, article) pairs
    target_txns['pair_key'] = target_txns['user_id'] + '_' + target_txns['article_id']
    positive_pairs = set(target_txns['pair_key'].unique())
    
    logger.info(f"Found {len(positive_pairs):,} unique positive pairs")
    
    # Label candidates
    labeled_df = candidates_df.copy()
    labeled_df['pair_key'] = labeled_df['user_id'] + '_' + labeled_df['article_id']
    labeled_df['label'] = labeled_df['pair_key'].isin(positive_pairs).astype(int)
    labeled_df = labeled_df.drop('pair_key', axis=1)
    
    # Log label distribution
    label_counts = labeled_df['label'].value_counts()
    logger.info(f"Label distribution:")
    logger.info(f"  Positives (1): {label_counts.get(1, 0):,}")
    logger.info(f"  Negatives (0): {label_counts.get(0, 0):,}")
    
    if label_counts.get(1, 0) > 0:
        ratio = label_counts.get(0, 0) / label_counts.get(1, 0)
        logger.info(f"  Negative/Positive ratio: {ratio:.2f}")
    
    return labeled_df


def sample_negatives(
    df: pd.DataFrame,
    neg_pos_ratio: float = 4.0,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Downsample negative examples to achieve target negative/positive ratio.
    
    Implements user-stratified sampling to maintain representation across users.
    
    Args:
        df: DataFrame with 'label' column
        neg_pos_ratio: Target ratio of negatives to positives
        random_state: Random seed for reproducibility
        
    Returns:
        DataFrame with downsampled negatives and all positives
    """
    logger.info(f"Sampling negatives with target ratio: {neg_pos_ratio}")
    
    # Separate positives and negatives
    positives = df[df['label'] == 1].copy()
    negatives = df[df['label'] == 0].copy()
    
    n_positives = len(positives)
    n_negatives = len(negatives)
    
    logger.info(f"Before sampling: {n_positives:,} positives, {n_negatives:,} negatives")
    
    if n_positives == 0:
        logger.warning("No positive examples found!")
        return df
    
    # Calculate target number of negatives
    target_negatives = int(n_positives * neg_pos_ratio)
    
    if target_negatives >= n_negatives:
        logger.info(f"Target negatives ({target_negatives:,}) >= available ({n_negatives:,}), keeping all")
        return df
    
    # User-stratified sampling
    logger.info("Performing user-stratified negative sampling")
    
    # Count negatives per user
    user_neg_counts = negatives.groupby('user_id').size()
    total_users = len(user_neg_counts)
    
    # Calculate negatives per user (proportional to their negative count)
    negatives_per_user = (user_neg_counts / user_neg_counts.sum() * target_negatives).round().astype(int)
    
    # Sample negatives for each user
    sampled_negatives = []
    np.random.seed(random_state)
    
    for user_id, n_sample in negatives_per_user.items():
        user_negatives = negatives[negatives['user_id'] == user_id]
        
        if n_sample >= len(user_negatives):
            # Keep all negatives for this user
            sampled_negatives.append(user_negatives)
        else:
            # Sample n_sample negatives
            sampled = user_negatives.sample(n=n_sample, random_state=random_state)
            sampled_negatives.append(sampled)
    
    # Combine sampled negatives with all positives
    sampled_negatives_df = pd.concat(sampled_negatives, ignore_index=True)
    result = pd.concat([positives, sampled_negatives_df], ignore_index=True)
    
    # Shuffle
    result = result.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    logger.info(f"After sampling: {len(positives):,} positives, {len(sampled_negatives_df):,} negatives")
    logger.info(f"Final ratio: {len(sampled_negatives_df) / len(positives):.2f}")
    
    return result


def create_train_val_splits(
    labeled_df: pd.DataFrame,
    val_fraction: float = 0.1,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split labeled data into training and validation sets.
    
    Uses stratified sampling to maintain class balance in both sets.
    
    Args:
        labeled_df: DataFrame with labels
        val_fraction: Fraction of data for validation (default: 0.1)
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (train_df, val_df)
    """
    logger.info(f"Creating train/val split with val_fraction={val_fraction}")
    
    # Stratified split by label
    positives = labeled_df[labeled_df['label'] == 1]
    negatives = labeled_df[labeled_df['label'] == 0]
    
    # Split positives
    n_val_pos = int(len(positives) * val_fraction)
    val_positives = positives.sample(n=n_val_pos, random_state=random_state)
    train_positives = positives.drop(val_positives.index)
    
    # Split negatives
    n_val_neg = int(len(negatives) * val_fraction)
    val_negatives = negatives.sample(n=n_val_neg, random_state=random_state)
    train_negatives = negatives.drop(val_negatives.index)
    
    # Combine and shuffle
    train_df = pd.concat([train_positives, train_negatives], ignore_index=True)
    train_df = train_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    val_df = pd.concat([val_positives, val_negatives], ignore_index=True)
    val_df = val_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    logger.info(f"Train set: {len(train_df):,} samples ({train_df['label'].sum():,} positives)")
    logger.info(f"Val set: {len(val_df):,} samples ({val_df['label'].sum():,} positives)")
    
    return train_df, val_df


def load_or_generate_features(
    features_file: str,
    candidates_dir: str,
    data_dir: str
) -> pd.DataFrame:
    """
    Load features from file or generate them if missing.
    
    Args:
        features_file: Path to features CSV file
        candidates_dir: Directory with candidate files
        data_dir: Directory with processed data
        
    Returns:
        DataFrame with features
    """
    features_path = Path(features_file)
    
    if features_path.exists():
        logger.info(f"Loading features from {features_file}")
        features = pd.read_csv(features_file)
        logger.info(f"Loaded {len(features):,} feature rows")
        return features
    
    logger.warning(f"Features file not found: {features_file}")
    logger.info("Generating features on the fly...")
    
    # Import features module
    try:
        from features import pipeline_build_features_for_users
        
        features = pipeline_build_features_for_users(
            user_list=None,
            candidates_dir=candidates_dir,
            data_dir=data_dir,
            out_path=features_file,
            overwrite=False
        )
        
        return features
    except Exception as e:
        logger.error(f"Failed to generate features: {e}")
        raise


def merge_features_with_candidates(
    candidates_df: pd.DataFrame,
    features_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge features with candidate pairs.
    
    Args:
        candidates_df: DataFrame with candidates and labels
        features_df: DataFrame with features
        
    Returns:
        Merged DataFrame with features
    """
    logger.info("Merging features with candidates")
    
    # Merge on user_id and article_id
    merged = candidates_df.merge(
        features_df,
        on=['user_id', 'article_id'],
        how='left',
        suffixes=('', '_feat')
    )
    
    # Check for missing features
    missing_features = merged[merged['score'].isna()]
    if len(missing_features) > 0:
        logger.warning(f"Found {len(missing_features):,} candidates without features")
        logger.warning("These will be dropped from training data")
        merged = merged.dropna(subset=['score'])
    
    logger.info(f"Merged dataset: {len(merged):,} rows")
    
    return merged



def save_training_stats(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    windows: dict,
    out_dir: str
) -> None:
    """
    Save training data statistics to JSON file.
    
    Args:
        train_df: Training DataFrame
        val_df: Validation DataFrame
        windows: Dictionary with time windows
        out_dir: Output directory
    """
    stats = {
        'creation_timestamp': datetime.now().isoformat(),
        'time_windows': {
            'train_window_start': str(windows['train_window_start'].date()),
            'train_window_end': str(windows['train_window_end'].date()),
            'target_start': str(windows['target_start'].date()),
            'target_end': str(windows['target_end'].date())
        },
        'train_set': {
            'total_samples': len(train_df),
            'positives': int(train_df['label'].sum()),
            'negatives': int((train_df['label'] == 0).sum()),
            'positive_rate': float(train_df['label'].mean()),
            'unique_users': int(train_df['user_id'].nunique()),
            'unique_articles': int(train_df['article_id'].nunique())
        },
        'val_set': {
            'total_samples': len(val_df),
            'positives': int(val_df['label'].sum()),
            'negatives': int((val_df['label'] == 0).sum()),
            'positive_rate': float(val_df['label'].mean()),
            'unique_users': int(val_df['user_id'].nunique()),
            'unique_articles': int(val_df['article_id'].nunique())
        }
    }
    
    stats_file = Path(out_dir) / 'training_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"Saved training statistics to {stats_file}")


def main():
    """
    Main entry point for CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Create labeled training and validation datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create training data with defaults
  python src/create_training_data.py --data_dir datasets
  
  # Custom negative sampling ratio
  python src/create_training_data.py --data_dir datasets --neg_pos_ratio 5
  
  # Custom validation fraction
  python src/create_training_data.py --data_dir datasets --val_fraction 0.15
  
  # Custom time windows (ISO format)
  python src/create_training_data.py --data_dir datasets --target_start 2018-09-18 --target_end 2018-09-24
        """
    )
    
    parser.add_argument(
        '--data_dir',
        type=str,
        default='datasets',
        help='Base data directory (default: datasets)'
    )
    
    parser.add_argument(
        '--features_file',
        type=str,
        default=None,
        help='Path to features CSV (default: {data_dir}/features/features_all.csv)'
    )
    
    parser.add_argument(
        '--candidates_dir',
        type=str,
        default=None,
        help='Directory with candidate files (default: {data_dir}/candidates)'
    )
    
    parser.add_argument(
        '--train_window_start',
        type=str,
        default=None,
        help='Training window start date (ISO format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--train_window_end',
        type=str,
        default=None,
        help='Training window end date (ISO format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--target_start',
        type=str,
        default=None,
        help='Target period start date (ISO format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--target_end',
        type=str,
        default=None,
        help='Target period end date (ISO format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--neg_pos_ratio',
        type=float,
        default=4.0,
        help='Negative to positive ratio for sampling (default: 4.0)'
    )
    
    parser.add_argument(
        '--val_fraction',
        type=float,
        default=0.1,
        help='Fraction of data for validation (default: 0.1)'
    )
    
    parser.add_argument(
        '--out_dir',
        type=str,
        default=None,
        help='Output directory for training data (default: {data_dir}/train)'
    )
    
    parser.add_argument(
        '--random_seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Set default paths
    if args.features_file is None:
        args.features_file = f"{args.data_dir}/features/features_all.csv"
    
    if args.candidates_dir is None:
        args.candidates_dir = f"{args.data_dir}/candidates"
    
    if args.out_dir is None:
        args.out_dir = f"{args.data_dir}/train"
    
    processed_dir = f"{args.data_dir}/processed"
    
    logger.info("=" * 60)
    logger.info("TRAINING DATA CREATION")
    logger.info("=" * 60)
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Features file: {args.features_file}")
    logger.info(f"Candidates directory: {args.candidates_dir}")
    logger.info(f"Output directory: {args.out_dir}")
    logger.info(f"Negative/Positive ratio: {args.neg_pos_ratio}")
    logger.info(f"Validation fraction: {args.val_fraction}")
    
    try:
        # Create output directory
        out_path = Path(args.out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        # Load transactions
        logger.info("\n--- Loading Data ---")
        transactions_file = Path(processed_dir) / 'processed_transactions.csv'
        transactions = pd.read_csv(transactions_file)
        transactions['t_dat'] = pd.to_datetime(transactions['t_dat'])
        
        # Rename customer_id to user_id for consistency
        if 'customer_id' in transactions.columns:
            transactions['user_id'] = transactions['customer_id'].astype(str)
        else:
            transactions['user_id'] = transactions['user_id'].astype(str)
        
        transactions['article_id'] = transactions['article_id'].astype(str)
        logger.info(f"Loaded transactions: {len(transactions):,} rows")
        
        # Calculate or parse time windows
        logger.info("\n--- Setting Time Windows ---")
        if args.train_window_start or args.train_window_end or args.target_start or args.target_end:
            # Use provided windows
            windows = calculate_default_windows(transactions)
            
            if args.train_window_start:
                windows['train_window_start'] = pd.to_datetime(args.train_window_start)
            if args.train_window_end:
                windows['train_window_end'] = pd.to_datetime(args.train_window_end)
            if args.target_start:
                windows['target_start'] = pd.to_datetime(args.target_start)
            if args.target_end:
                windows['target_end'] = pd.to_datetime(args.target_end)
            
            logger.info("Using custom time windows:")
            for key, value in windows.items():
                logger.info(f"  {key}: {value.date()}")
        else:
            # Calculate default windows
            windows = calculate_default_windows(transactions)
        
        # Load or generate features
        logger.info("\n--- Loading Features ---")
        features = load_or_generate_features(
            args.features_file,
            args.candidates_dir,
            processed_dir
        )
        
        # Ensure consistent types
        features['user_id'] = features['user_id'].astype(str)
        features['article_id'] = features['article_id'].astype(str)
        
        # Label candidates
        logger.info("\n--- Labeling Candidates ---")
        labeled_features = label_candidate_rows(
            features,
            transactions,
            windows['target_start'],
            windows['target_end']
        )
        
        # Sample negatives
        logger.info("\n--- Sampling Negatives ---")
        sampled_data = sample_negatives(
            labeled_features,
            neg_pos_ratio=args.neg_pos_ratio,
            random_state=args.random_seed
        )
        
        # Create train/val splits
        logger.info("\n--- Creating Train/Val Splits ---")
        train_df, val_df = create_train_val_splits(
            sampled_data,
            val_fraction=args.val_fraction,
            random_state=args.random_seed
        )
        
        # Save datasets
        logger.info("\n--- Saving Datasets ---")
        train_file = out_path / 'train_pairs.csv'
        val_file = out_path / 'val_pairs.csv'
        
        train_df.to_csv(train_file, index=False)
        logger.info(f"Saved training data to {train_file}")
        
        val_df.to_csv(val_file, index=False)
        logger.info(f"Saved validation data to {val_file}")
        
        # Save sample rows
        sample_file = out_path / 'sample_rows.csv'
        sample_df = pd.concat([
            train_df.head(5),
            val_df.head(5)
        ])
        sample_df.to_csv(sample_file, index=False)
        logger.info(f"Saved sample rows to {sample_file}")
        
        # Save statistics
        save_training_stats(train_df, val_df, windows, args.out_dir)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING DATA SUMMARY")
        logger.info("=" * 60)
        
        logger.info("\nTime Windows:")
        logger.info(f"  Training period: {windows['train_window_start'].date()} to {windows['train_window_end'].date()}")
        logger.info(f"  Target period: {windows['target_start'].date()} to {windows['target_end'].date()}")
        
        logger.info("\nTraining Set:")
        logger.info(f"  Total samples: {len(train_df):,}")
        logger.info(f"  Positives: {train_df['label'].sum():,}")
        logger.info(f"  Negatives: {(train_df['label'] == 0).sum():,}")
        logger.info(f"  Positive rate: {train_df['label'].mean():.4f}")
        logger.info(f"  Ratio (neg/pos): {(train_df['label'] == 0).sum() / train_df['label'].sum():.2f}")
        
        logger.info("\nValidation Set:")
        logger.info(f"  Total samples: {len(val_df):,}")
        logger.info(f"  Positives: {val_df['label'].sum():,}")
        logger.info(f"  Negatives: {(val_df['label'] == 0).sum():,}")
        logger.info(f"  Positive rate: {val_df['label'].mean():.4f}")
        logger.info(f"  Ratio (neg/pos): {(val_df['label'] == 0).sum() / val_df['label'].sum():.2f}")
        
        logger.info("\n✓ Training data creation completed successfully")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure processed data, candidates, and features exist")
        return 1
    except Exception as e:
        logger.error(f"Error creating training data: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
