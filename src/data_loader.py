"""
Data Loader for H&M Fashion Dataset

This module provides utilities to load and sample customer, article, and transaction data.
Supports chunked loading and reservoir sampling for large transaction files to minimize memory usage.

Usage:
    python data_loader.py --data_dir ../datasets --sample_transactions 100000 --save_samples
"""

import argparse
import logging
import os
import sys
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


def load_customers(path: str) -> pd.DataFrame:
    """
    Load customers dataset from CSV file.
    
    Args:
        path: Path to customers.csv file
        
    Returns:
        DataFrame containing customer data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
    """
    logger.info(f"Loading customers from: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Customers file not found: {path}")
    
    df = pd.read_csv(path)
    logger.info(f"Loaded customers: {df.shape[0]} rows, {df.shape[1]} columns")
    logger.debug(f"Customers columns: {df.columns.tolist()}")
    logger.debug(f"First few rows:\n{df.head(3)}")
    
    return df


def load_articles(path: str) -> pd.DataFrame:
    """
    Load articles dataset from CSV file.
    
    Args:
        path: Path to articles.csv file
        
    Returns:
        DataFrame containing article data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
    """
    logger.info(f"Loading articles from: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Articles file not found: {path}")
    
    df = pd.read_csv(path)
    logger.info(f"Loaded articles: {df.shape[0]} rows, {df.shape[1]} columns")
    logger.debug(f"Articles columns: {df.columns.tolist()}")
    logger.debug(f"First few rows:\n{df.head(3)}")
    
    return df


def load_transactions(
    path: str,
    nrows: Optional[int] = None,
    sample_fraction: Optional[float] = None
) -> pd.DataFrame:
    """
    Load transactions dataset with optional sampling.
    
    Args:
        path: Path to transactions CSV file
        nrows: If provided, load only first N rows
        sample_fraction: If provided (0.0-1.0), sample rows proportionally using chunked reading
        
    Returns:
        DataFrame containing transaction data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If both nrows and sample_fraction are provided
    """
    logger.info(f"Loading transactions from: {path}")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Transactions file not found: {path}")
    
    if nrows is not None and sample_fraction is not None:
        raise ValueError("Cannot specify both nrows and sample_fraction")
    
    # Simple case: load with nrows limit
    if nrows is not None:
        logger.info(f"Loading first {nrows} rows")
        df = pd.read_csv(path, nrows=nrows)
        logger.info(f"Loaded transactions: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    # Chunked sampling case
    if sample_fraction is not None:
        logger.info(f"Loading with sample fraction: {sample_fraction}")
        chunk_size = 100000
        sampled_chunks = []
        
        for chunk in pd.read_csv(path, chunksize=chunk_size):
            # Sample from each chunk proportionally
            n_sample = int(len(chunk) * sample_fraction)
            if n_sample > 0:
                sampled = chunk.sample(n=n_sample, random_state=42)
                sampled_chunks.append(sampled)
        
        df = pd.concat(sampled_chunks, ignore_index=True)
        logger.info(f"Loaded sampled transactions: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    # Default: load entire file
    logger.info("Loading entire transactions file")
    df = pd.read_csv(path)
    logger.info(f"Loaded transactions: {df.shape[0]} rows, {df.shape[1]} columns")
    logger.debug(f"Transactions columns: {df.columns.tolist()}")
    logger.debug(f"First few rows:\n{df.head(3)}")
    
    return df



def sample_transactions_chunked(
    path: str,
    sample_n: int,
    out_path: str,
    random_state: int = 42
) -> None:
    """
    Sample N rows from a large transactions file using reservoir sampling.
    Reads file in chunks to avoid loading entire dataset into memory.
    
    Reservoir sampling algorithm ensures uniform random sampling across entire file
    without knowing total row count in advance.
    
    Args:
        path: Path to input transactions CSV file
        sample_n: Number of rows to sample
        out_path: Path to save sampled CSV
        random_state: Random seed for reproducibility
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If sample_n <= 0
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Transactions file not found: {path}")
    
    if sample_n <= 0:
        raise ValueError(f"sample_n must be positive, got {sample_n}")
    
    logger.info(f"Sampling {sample_n} transactions from {path}")
    logger.info("Using reservoir sampling algorithm for memory-efficient sampling")
    
    np.random.seed(random_state)
    chunk_size = 100000
    
    # Reservoir sampling: maintain a reservoir of sample_n items
    reservoir = None
    total_rows_seen = 0
    
    for chunk_idx, chunk in enumerate(pd.read_csv(path, chunksize=chunk_size)):
        chunk_start = total_rows_seen
        chunk_end = total_rows_seen + len(chunk)
        
        if reservoir is None:
            # Initialize reservoir with first chunk (or part of it)
            if len(chunk) >= sample_n:
                reservoir = chunk.iloc[:sample_n].copy()
                total_rows_seen = sample_n
                # Process remaining rows in first chunk
                for i in range(sample_n, len(chunk)):
                    total_rows_seen += 1
                    # Random index to potentially replace
                    j = np.random.randint(0, total_rows_seen)
                    if j < sample_n:
                        reservoir.iloc[j] = chunk.iloc[i]
            else:
                reservoir = chunk.copy()
                total_rows_seen = len(chunk)
        else:
            # Apply reservoir sampling to each row in chunk
            for i in range(len(chunk)):
                total_rows_seen += 1
                # Random index to potentially replace
                j = np.random.randint(0, total_rows_seen)
                if j < sample_n:
                    reservoir.iloc[j] = chunk.iloc[i]
        
        if (chunk_idx + 1) % 10 == 0:
            logger.info(f"Processed {total_rows_seen:,} rows...")
    
    logger.info(f"Total rows processed: {total_rows_seen:,}")
    logger.info(f"Sampled {len(reservoir)} rows")
    
    # Save to output path
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    reservoir.to_csv(out_path, index=False)
    logger.info(f"Saved sampled transactions to: {out_path}")


def validate_dataframes(
    customers: pd.DataFrame,
    articles: pd.DataFrame,
    transactions: pd.DataFrame
) -> bool:
    """
    Validate loaded dataframes for basic sanity checks.
    
    Checks:
    - DataFrames are not empty
    - Expected columns exist
    - Data types are reasonable
    - Displays preview of each dataset
    
    Args:
        customers: Customers DataFrame
        articles: Articles DataFrame
        transactions: Transactions DataFrame
        
    Returns:
        True if all validations pass, False otherwise
    """
    logger.info("=" * 60)
    logger.info("VALIDATING DATAFRAMES")
    logger.info("=" * 60)
    
    all_valid = True
    
    # Validate customers
    logger.info("\n--- CUSTOMERS ---")
    if customers.empty:
        logger.error("Customers DataFrame is empty!")
        all_valid = False
    else:
        logger.info(f"Shape: {customers.shape}")
        logger.info(f"Columns: {customers.columns.tolist()}")
        logger.info(f"Memory usage: {customers.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        logger.info(f"Sample data:\n{customers.head(3)}")
        
        # Check for customer_id column (common in such datasets)
        if 'customer_id' not in customers.columns:
            logger.warning("Expected 'customer_id' column not found in customers")
    
    # Validate articles
    logger.info("\n--- ARTICLES ---")
    if articles.empty:
        logger.error("Articles DataFrame is empty!")
        all_valid = False
    else:
        logger.info(f"Shape: {articles.shape}")
        logger.info(f"Columns: {articles.columns.tolist()}")
        logger.info(f"Memory usage: {articles.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        logger.info(f"Sample data:\n{articles.head(3)}")
        
        # Check for article_id column
        if 'article_id' not in articles.columns:
            logger.warning("Expected 'article_id' column not found in articles")
    
    # Validate transactions
    logger.info("\n--- TRANSACTIONS ---")
    if transactions.empty:
        logger.error("Transactions DataFrame is empty!")
        all_valid = False
    else:
        logger.info(f"Shape: {transactions.shape}")
        logger.info(f"Columns: {transactions.columns.tolist()}")
        logger.info(f"Memory usage: {transactions.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        logger.info(f"Sample data:\n{transactions.head(3)}")
        
        # Check for expected columns
        expected_cols = ['customer_id', 'article_id']
        for col in expected_cols:
            if col not in transactions.columns:
                logger.warning(f"Expected '{col}' column not found in transactions")
    
    logger.info("=" * 60)
    
    if all_valid:
        logger.info("✓ All validations passed")
    else:
        logger.error("✗ Some validations failed")
    
    return all_valid


def main():
    """
    Main entry point for CLI usage.
    Parses arguments, loads data, validates, and optionally creates samples.
    """
    parser = argparse.ArgumentParser(
        description="Load and sample H&M fashion dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load full datasets
  python data_loader.py --data_dir ../datasets
  
  # Sample 100k transactions and save
  python data_loader.py --data_dir ../datasets --sample_transactions 100000 --save_samples
  
  # Use custom random seed
  python data_loader.py --data_dir ../datasets --sample_transactions 50000 --random_seed 123
        """
    )
    
    parser.add_argument(
        '--data_dir',
        type=str,
        default='../datasets',
        help='Path to directory containing CSV files (default: ../datasets)'
    )
    
    parser.add_argument(
        '--sample_transactions',
        type=int,
        default=None,
        help='Number of transaction rows to sample (e.g., 100000)'
    )
    
    parser.add_argument(
        '--save_samples',
        action='store_true',
        help='Save sampled CSVs to data_dir/sampled/ folder'
    )
    
    parser.add_argument(
        '--random_seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.random_seed)
    
    logger.info("=" * 60)
    logger.info("H&M FASHION DATASET LOADER")
    logger.info("=" * 60)
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Random seed: {args.random_seed}")
    
    # Construct file paths
    data_dir = Path(args.data_dir)
    
    # Handle nested directory structure (e.g., datasets/customers.csv/customers.csv)
    customers_path = data_dir / 'customers.csv'
    if customers_path.is_dir():
        customers_path = customers_path / 'customers.csv'
    
    articles_path = data_dir / 'articles.csv'
    if articles_path.is_dir():
        articles_path = articles_path / 'articles.csv'
    
    transactions_path = data_dir / 'transactions_train.csv'
    if transactions_path.is_dir():
        transactions_path = transactions_path / 'transactions_train.csv'
    
    try:
        # Load customers and articles (typically smaller files)
        customers = load_customers(str(customers_path))
        articles = load_articles(str(articles_path))
        
        # Load transactions with optional sampling
        if args.sample_transactions:
            logger.info(f"Sampling {args.sample_transactions} transactions")
            # Use chunked loading for sampling
            sample_fraction = min(args.sample_transactions / 10_000_000, 1.0)  # Assume ~10M rows
            transactions = load_transactions(
                str(transactions_path),
                nrows=args.sample_transactions * 2  # Load 2x and then sample
            )
            # Further sample if needed
            if len(transactions) > args.sample_transactions:
                transactions = transactions.sample(
                    n=args.sample_transactions,
                    random_state=args.random_seed
                )
                logger.info(f"Sampled down to {len(transactions)} rows")
        else:
            transactions = load_transactions(str(transactions_path))
        
        # Validate all dataframes
        validate_dataframes(customers, articles, transactions)
        
        # Save samples if requested
        if args.save_samples:
            logger.info("\n" + "=" * 60)
            logger.info("SAVING SAMPLED DATASETS")
            logger.info("=" * 60)
            
            sampled_dir = data_dir / 'sampled'
            sampled_dir.mkdir(exist_ok=True)
            
            # Save customers
            customers_out = sampled_dir / 'sampled_customers.csv'
            customers.to_csv(customers_out, index=False)
            logger.info(f"Saved: {customers_out}")
            
            # Save articles
            articles_out = sampled_dir / 'sampled_articles.csv'
            articles.to_csv(articles_out, index=False)
            logger.info(f"Saved: {articles_out}")
            
            # Save transactions
            transactions_out = sampled_dir / 'sampled_transactions.csv'
            transactions.to_csv(transactions_out, index=False)
            logger.info(f"Saved: {transactions_out}")
            
            logger.info(f"\nAll sampled files saved to: {sampled_dir}")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        print(f"customers: {len(customers)} rows, articles: {len(articles)} rows, transactions: {len(transactions)} rows")
        
        logger.info("✓ Data loading completed successfully")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
