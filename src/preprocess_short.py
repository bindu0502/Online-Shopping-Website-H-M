"""
Short Preprocessing Script

Executes the same preprocessing steps as the notebook but as a standalone script.
Reads sampled CSVs and writes processed CSVs to datasets/processed/.

Usage:
    python src/preprocess_short.py
    python src/preprocess_short.py --input_dir datasets/sampled --output_dir datasets/processed
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_transactions(df: pd.DataFrame, date_col: str = 't_dat') -> pd.DataFrame:
    """
    Process transactions dataset:
    - Convert date to datetime
    - Extract year, month, day
    - Ensure IDs are strings
    
    Args:
        df: Transactions DataFrame
        date_col: Name of the date column
        
    Returns:
        Processed transactions DataFrame
    """
    logger.info("Processing transactions...")
    
    # Convert date to datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Extract temporal features
    df['t_year'] = df[date_col].dt.year
    df['t_month'] = df[date_col].dt.month
    df['t_day'] = df[date_col].dt.day
    
    # Ensure IDs are strings
    df['customer_id'] = df['customer_id'].astype(str)
    df['article_id'] = df['article_id'].astype(str)
    
    logger.info(f"Transactions processed: {df.shape}")
    logger.info(f"Date range: {df[date_col].min()} to {df[date_col].max()}")
    
    return df


def process_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process customers dataset:
    - Ensure customer_id is string
    - Create age bins
    
    Args:
        df: Customers DataFrame
        
    Returns:
        Processed customers DataFrame
    """
    logger.info("Processing customers...")
    
    # Ensure customer_id is string
    df['customer_id'] = df['customer_id'].astype(str)
    
    # Create age bins if age column exists
    if 'age' in df.columns:
        age_bins = [0, 18, 25, 35, 50, 120]
        age_labels = ['<18', '18-25', '26-35', '36-50', '50+']
        df['age_bin'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)
        logger.info("Age bins created")
        logger.info(f"Age distribution:\n{df['age_bin'].value_counts().sort_index()}")
    else:
        logger.warning("Age column not found in customers dataset")
    
    logger.info(f"Customers processed: {df.shape}")
    
    return df


def infer_gender(row: pd.Series) -> int:
    """
    Infer gender from product metadata:
    0 = unisex/unknown
    1 = women/female
    2 = men/male
    
    Args:
        row: DataFrame row with product information
        
    Returns:
        Gender code (0, 1, or 2)
    """
    text = ''
    if 'product_type_name' in row and pd.notna(row['product_type_name']):
        text += str(row['product_type_name']).lower() + ' '
    if 'detail_desc' in row and pd.notna(row['detail_desc']):
        text += str(row['detail_desc']).lower()
    
    if 'men' in text or 'male' in text or 'boy' in text:
        return 2
    elif 'women' in text or 'female' in text or 'girl' in text or 'ladies' in text:
        return 1
    else:
        return 0


def process_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process articles dataset:
    - Ensure article_id is string
    - Encode product_type_name as categorical
    - Create gender tag heuristic
    
    Args:
        df: Articles DataFrame
        
    Returns:
        Processed articles DataFrame
    """
    logger.info("Processing articles...")
    
    # Ensure article_id is string
    df['article_id'] = df['article_id'].astype(str)
    
    # Encode product_type_name as categorical
    if 'product_type_name' in df.columns:
        df['product_type_code'] = pd.Categorical(df['product_type_name']).codes
        logger.info(f"Product types encoded: {df['product_type_code'].nunique()} unique types")
    else:
        logger.warning("product_type_name column not found")
    
    # Create gender tag heuristic
    df['gender_tag'] = df.apply(infer_gender, axis=1)
    
    gender_dist = df['gender_tag'].value_counts().sort_index()
    logger.info(f"Gender tag distribution:\n{gender_dist}")
    logger.info("(0=unisex/unknown, 1=women, 2=men)")
    
    logger.info(f"Articles processed: {df.shape}")
    
    return df


def main():
    """
    Main entry point for preprocessing script.
    """
    parser = argparse.ArgumentParser(
        description="Preprocess H&M fashion dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input_dir',
        type=str,
        default='datasets/sampled',
        help='Path to directory containing sampled CSV files'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='datasets/processed',
        help='Path to directory for saving processed CSV files'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("H&M FASHION DATASET PREPROCESSING")
    logger.info("=" * 60)
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Define paths
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    try:
        # Load datasets
        logger.info("\n--- LOADING DATASETS ---")
        customers = pd.read_csv(input_dir / 'sampled_customers.csv')
        logger.info(f"Loaded customers: {customers.shape}")
        
        articles = pd.read_csv(input_dir / 'sampled_articles.csv')
        logger.info(f"Loaded articles: {articles.shape}")
        
        transactions = pd.read_csv(input_dir / 'sampled_transactions.csv')
        logger.info(f"Loaded transactions: {transactions.shape}")
        
        # Process datasets
        logger.info("\n--- PROCESSING DATASETS ---")
        
        # Detect date column name
        date_col = 't_dat' if 't_dat' in transactions.columns else transactions.columns[0]
        transactions = process_transactions(transactions, date_col)
        
        customers = process_customers(customers)
        articles = process_articles(articles)
        
        # Create output directory
        output_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"\nCreated output directory: {output_dir}")
        
        # Save processed datasets
        logger.info("\n--- SAVING PROCESSED DATASETS ---")
        
        customers_out = output_dir / 'processed_customers.csv'
        customers.to_csv(customers_out, index=False)
        logger.info(f"Saved: {customers_out} ({customers.shape[0]:,} rows)")
        
        articles_out = output_dir / 'processed_articles.csv'
        articles.to_csv(articles_out, index=False)
        logger.info(f"Saved: {articles_out} ({articles.shape[0]:,} rows)")
        
        transactions_out = output_dir / 'processed_transactions.csv'
        transactions.to_csv(transactions_out, index=False)
        logger.info(f"Saved: {transactions_out} ({transactions.shape[0]:,} rows)")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("PREPROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Customers: {customers.shape[0]:,} rows, {customers.shape[1]} columns")
        logger.info(f"✓ Articles: {articles.shape[0]:,} rows, {articles.shape[1]} columns")
        logger.info(f"✓ Transactions: {transactions.shape[0]:,} rows, {transactions.shape[1]} columns")
        logger.info("\nProcessed datasets ready for modeling pipeline!")
        logger.info("Next steps: candidate generation → feature engineering → model training")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure to run data_loader.py with --save_samples first")
        return 1
    except Exception as e:
        logger.error(f"Error during preprocessing: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
