"""
LightGBM Model Training Module

Trains a LightGBM binary classifier to predict purchase probability for (user, article) pairs.
Includes evaluation metrics, feature importance analysis, and MAP@K computation.

Usage:
    python src/model_train.py --train_csv datasets/train/train_pairs.csv
    python src/model_train.py --task evaluate --model_out models/lgbm_v1.pkl
"""

import argparse
import json
import logging
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_training_data(
    train_csv: str,
    val_csv: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load training and validation datasets.
    
    Args:
        train_csv: Path to training CSV
        val_csv: Path to validation CSV
        
    Returns:
        Tuple of (train_df, val_df)
    """
    logger.info(f"Loading training data from {train_csv}")
    train_df = pd.read_csv(train_csv)
    logger.info(f"Loaded training data: {train_df.shape}")
    
    logger.info(f"Loading validation data from {val_csv}")
    val_df = pd.read_csv(val_csv)
    logger.info(f"Loaded validation data: {val_df.shape}")
    
    return train_df, val_df


def prepare_features(
    df: pd.DataFrame,
    exclude_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Prepare features for training by identifying feature columns and handling missing values.
    
    Args:
        df: Input DataFrame
        exclude_cols: Columns to exclude from features
        
    Returns:
        Tuple of (prepared_df, feature_columns, categorical_features)
    """
    if exclude_cols is None:
        exclude_cols = ['user_id', 'article_id', 'score', 'reason', 'rule_scores_json', 'label']
    
    # Identify feature columns
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    logger.info(f"Feature columns: {len(feature_cols)}")
    logger.debug(f"Features: {feature_cols}")
    
    # Identify categorical features
    categorical_features = []
    df_prepared = df.copy()
    
    for col in feature_cols:
        if df_prepared[col].dtype == 'object' or df_prepared[col].dtype.name == 'category':
            categorical_features.append(col)
            # Convert to category type for LightGBM
            df_prepared[col] = df_prepared[col].astype('category')
    
    if categorical_features:
        logger.info(f"Categorical features: {categorical_features}")
    
    # Fill missing values
    for col in feature_cols:
        if df_prepared[col].isna().any():
            if col in categorical_features:
                df_prepared[col] = df_prepared[col].fillna('unknown')
            else:
                df_prepared[col] = df_prepared[col].fillna(0)
    
    return df_prepared, feature_cols, categorical_features


def train_lightgbm(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_cols: List[str],
    categorical_features: List[str],
    params: Optional[Dict] = None,
    num_boost_round: int = 2000,
    early_stopping_rounds: int = 50,
    verbose_eval: int = 50
) -> Tuple[lgb.Booster, Dict]:
    """
    Train LightGBM binary classifier with early stopping.
    
    Args:
        train_df: Training DataFrame
        val_df: Validation DataFrame
        feature_cols: List of feature column names
        categorical_features: List of categorical feature names
        params: LightGBM parameters (optional)
        num_boost_round: Maximum number of boosting rounds
        early_stopping_rounds: Early stopping rounds
        verbose_eval: Logging frequency
        
    Returns:
        Tuple of (trained_model, training_info)
    """
    logger.info("=" * 60)
    logger.info("TRAINING LIGHTGBM MODEL")
    logger.info("=" * 60)
    
    # Default parameters
    if params is None:
        params = {
            'objective': 'binary',
            'boosting_type': 'gbdt',
            'metric': 'auc',
            'learning_rate': 0.03,
            'num_leaves': 128,
            'max_depth': 8,
            'min_child_samples': 20,
            'subsample': 0.8,
            'colsample_bytree': 0.7,
            'reg_alpha': 0.0,
            'reg_lambda': 0.0,
            'verbose': -1
        }
    
    logger.info("Training parameters:")
    for key, value in params.items():
        logger.info(f"  {key}: {value}")
    
    # Prepare datasets
    X_train = train_df[feature_cols]
    y_train = train_df['label']
    
    X_val = val_df[feature_cols]
    y_val = val_df['label']
    
    logger.info(f"\nTraining set: {X_train.shape}, Positives: {y_train.sum()}")
    logger.info(f"Validation set: {X_val.shape}, Positives: {y_val.sum()}")
    
    # Create LightGBM datasets
    train_data = lgb.Dataset(
        X_train,
        label=y_train,
        categorical_feature=categorical_features if categorical_features else 'auto',
        free_raw_data=False
    )
    
    val_data = lgb.Dataset(
        X_val,
        label=y_val,
        categorical_feature=categorical_features if categorical_features else 'auto',
        reference=train_data,
        free_raw_data=False
    )
    
    # Train model
    logger.info(f"\nStarting training with {num_boost_round} max rounds...")
    logger.info(f"Early stopping: {early_stopping_rounds} rounds")
    
    evals_result = {}
    model = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=[train_data, val_data],
        valid_names=['train', 'valid'],
        callbacks=[
            lgb.log_evaluation(verbose_eval),
            lgb.early_stopping(early_stopping_rounds),
            lgb.record_evaluation(evals_result)
        ]
    )
    
    # Training info
    best_iteration = model.best_iteration
    best_score = model.best_score['valid']['auc']
    
    logger.info(f"\n✓ Training completed")
    logger.info(f"Best iteration: {best_iteration}")
    logger.info(f"Best validation AUC: {best_score:.4f}")
    
    training_info = {
        'best_iteration': best_iteration,
        'best_score': best_score,
        'evals_result': evals_result,
        'params': params,
        'num_features': len(feature_cols),
        'feature_names': feature_cols
    }
    
    return model, training_info


def evaluate_model(
    model: lgb.Booster,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_cols: List[str],
    output_dir: str = "outputs"
) -> Dict:
    """
    Evaluate trained model and generate visualizations.
    
    Args:
        model: Trained LightGBM model
        train_df: Training DataFrame
        val_df: Validation DataFrame
        feature_cols: List of feature column names
        output_dir: Directory for output files
        
    Returns:
        Dictionary with evaluation metrics
    """
    logger.info("=" * 60)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 60)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare data
    X_train = train_df[feature_cols]
    y_train = train_df['label']
    
    X_val = val_df[feature_cols]
    y_val = val_df['label']
    
    # Predictions
    logger.info("\nGenerating predictions...")
    train_pred = model.predict(X_train, num_iteration=model.best_iteration)
    val_pred = model.predict(X_val, num_iteration=model.best_iteration)
    
    # AUC scores
    train_auc = roc_auc_score(y_train, train_pred)
    val_auc = roc_auc_score(y_val, val_pred)
    
    logger.info(f"\nAUC Scores:")
    logger.info(f"  Training AUC: {train_auc:.4f}")
    logger.info(f"  Validation AUC: {val_auc:.4f}")
    
    # ROC curve
    logger.info("\nGenerating ROC curve...")
    plot_roc_curve(y_train, train_pred, y_val, val_pred, output_path)
    
    # Feature importance
    logger.info("\nAnalyzing feature importance...")
    plot_feature_importance(model, feature_cols, output_path, top_n=15)
    
    # MAP@K evaluation
    logger.info("\nComputing MAP@K metrics...")
    mapk_results = compute_mapk(model, val_df, feature_cols, k_values=[10, 20, 30])
    save_mapk_table(mapk_results, output_path)
    
    evaluation_results = {
        'train_auc': train_auc,
        'val_auc': val_auc,
        'mapk_results': mapk_results
    }
    
    return evaluation_results


def plot_roc_curve(
    y_train: pd.Series,
    train_pred: np.ndarray,
    y_val: pd.Series,
    val_pred: np.ndarray,
    output_path: Path
) -> None:
    """
    Plot and save ROC curve for train and validation sets.
    
    Args:
        y_train: Training labels
        train_pred: Training predictions
        y_val: Validation labels
        val_pred: Validation predictions
        output_path: Output directory path
    """
    # Calculate ROC curves
    train_fpr, train_tpr, _ = roc_curve(y_train, train_pred)
    val_fpr, val_tpr, _ = roc_curve(y_val, val_pred)
    
    train_auc = roc_auc_score(y_train, train_pred)
    val_auc = roc_auc_score(y_val, val_pred)
    
    # Plot
    plt.figure(figsize=(10, 8))
    plt.plot(train_fpr, train_tpr, label=f'Train (AUC = {train_auc:.4f})', linewidth=2)
    plt.plot(val_fpr, val_tpr, label=f'Validation (AUC = {val_auc:.4f})', linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
    
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - LightGBM Recommendation Model', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    roc_file = output_path / 'roc_curve.png'
    plt.savefig(roc_file, dpi=150)
    plt.close()
    
    logger.info(f"Saved ROC curve to {roc_file}")


def plot_feature_importance(
    model: lgb.Booster,
    feature_names: List[str],
    output_path: Path,
    top_n: int = 15
) -> None:
    """
    Plot and save feature importance.
    
    Args:
        model: Trained LightGBM model
        feature_names: List of feature names
        output_path: Output directory path
        top_n: Number of top features to display
    """
    # Get feature importance
    importance = model.feature_importance(importance_type='gain')
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    # Print top features
    logger.info(f"\nTop {top_n} features by importance:")
    for idx, row in feature_importance.head(top_n).iterrows():
        logger.info(f"  {row['feature']}: {row['importance']:.2f}")
    
    # Plot
    top_features = feature_importance.head(top_n)
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'], color='steelblue')
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance (Gain)', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.title(f'Top {top_n} Feature Importance', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    importance_file = output_path / 'feature_importance.png'
    plt.savefig(importance_file, dpi=150)
    plt.close()
    
    logger.info(f"Saved feature importance to {importance_file}")



def compute_mapk(
    model: lgb.Booster,
    val_df: pd.DataFrame,
    feature_cols: List[str],
    k_values: List[int] = [10, 20, 30]
) -> Dict:
    """
    Compute Mean Average Precision at K (MAP@K) for validation set.
    
    For each user, ranks their candidate items by predicted score and computes
    average precision at different K values.
    
    Args:
        model: Trained LightGBM model
        val_df: Validation DataFrame with user_id, article_id, label
        feature_cols: List of feature column names
        k_values: List of K values to evaluate
        
    Returns:
        Dictionary with MAP@K and Recall@K for each K
    """
    logger.info("Computing MAP@K metrics...")
    
    # Add predictions to validation set
    val_df_eval = val_df.copy()
    X_val = val_df_eval[feature_cols]
    val_df_eval['pred_score'] = model.predict(X_val, num_iteration=model.best_iteration)
    
    # Group by user
    results = {k: {'map': [], 'recall': []} for k in k_values}
    
    for user_id, user_data in val_df_eval.groupby('user_id'):
        # Sort by predicted score
        user_data_sorted = user_data.sort_values('pred_score', ascending=False)
        
        # Get actual positives
        actual_positives = set(user_data_sorted[user_data_sorted['label'] == 1]['article_id'])
        n_positives = len(actual_positives)
        
        if n_positives == 0:
            continue
        
        # Compute metrics for each K
        for k in k_values:
            top_k = user_data_sorted.head(k)
            predicted_items = set(top_k['article_id'])
            
            # Compute Average Precision at K
            hits = 0
            sum_precisions = 0.0
            
            for i, (_, row) in enumerate(top_k.iterrows(), 1):
                if row['label'] == 1:
                    hits += 1
                    precision_at_i = hits / i
                    sum_precisions += precision_at_i
            
            ap_at_k = sum_precisions / min(k, n_positives) if n_positives > 0 else 0.0
            
            # Compute Recall at K
            recall_at_k = hits / n_positives if n_positives > 0 else 0.0
            
            results[k]['map'].append(ap_at_k)
            results[k]['recall'].append(recall_at_k)
    
    # Compute means
    mapk_results = {}
    for k in k_values:
        mapk_results[k] = {
            'map': np.mean(results[k]['map']) if results[k]['map'] else 0.0,
            'recall': np.mean(results[k]['recall']) if results[k]['recall'] else 0.0,
            'n_users': len(results[k]['map'])
        }
    
    return mapk_results


def save_mapk_table(mapk_results: Dict, output_path: Path) -> None:
    """
    Save MAP@K results to text file.
    
    Args:
        mapk_results: Dictionary with MAP@K results
        output_path: Output directory path
    """
    mapk_file = output_path / 'mapk_table.txt'
    
    with open(mapk_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("MAP@K and Recall@K Results\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'K':<10}{'MAP@K':<15}{'Recall@K':<15}{'N Users':<10}\n")
        f.write("-" * 60 + "\n")
        
        for k in sorted(mapk_results.keys()):
            result = mapk_results[k]
            f.write(f"{k:<10}{result['map']:<15.4f}{result['recall']:<15.4f}{result['n_users']:<10}\n")
        
        f.write("\n")
    
    logger.info(f"Saved MAP@K table to {mapk_file}")
    
    # Also print to console
    logger.info("\nMAP@K Results:")
    logger.info(f"{'K':<10}{'MAP@K':<15}{'Recall@K':<15}{'N Users':<10}")
    logger.info("-" * 60)
    for k in sorted(mapk_results.keys()):
        result = mapk_results[k]
        logger.info(f"{k:<10}{result['map']:<15.4f}{result['recall']:<15.4f}{result['n_users']:<10}")


def save_model_and_metadata(
    model: lgb.Booster,
    training_info: Dict,
    evaluation_results: Dict,
    model_out: str
) -> None:
    """
    Save trained model and training metadata.
    
    Args:
        model: Trained LightGBM model
        training_info: Training information dictionary
        evaluation_results: Evaluation results dictionary
        model_out: Output path for model file
    """
    # Save model
    model_path = Path(model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, model_path)
    logger.info(f"\n✓ Saved model to {model_path}")
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'model_path': str(model_path),
        'training': {
            'best_iteration': training_info['best_iteration'],
            'best_score': training_info['best_score'],
            'num_features': training_info['num_features'],
            'params': training_info['params']
        },
        'evaluation': {
            'train_auc': evaluation_results['train_auc'],
            'val_auc': evaluation_results['val_auc'],
            'mapk_results': evaluation_results['mapk_results']
        }
    }
    
    metadata_path = model_path.parent / 'training_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✓ Saved metadata to {metadata_path}")


def load_model(model_path: str) -> lgb.Booster:
    """
    Load trained LightGBM model.
    
    Args:
        model_path: Path to model file
        
    Returns:
        Loaded LightGBM model
    """
    logger.info(f"Loading model from {model_path}")
    model = joblib.load(model_path)
    logger.info("✓ Model loaded successfully")
    return model


def main():
    """
    Main entry point for CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Train LightGBM ranking model for recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train model with defaults
  python src/model_train.py
  
  # Train with custom parameters
  python src/model_train.py --num_boost_round 1000 --early_stopping_rounds 30
  
  # Evaluate existing model
  python src/model_train.py --task evaluate --model_out models/lgbm_v1.pkl
  
  # Custom data paths
  python src/model_train.py --train_csv custom/train.csv --val_csv custom/val.csv
        """
    )
    
    parser.add_argument(
        '--train_csv',
        type=str,
        default='datasets/train/train_pairs.csv',
        help='Path to training CSV (default: datasets/train/train_pairs.csv)'
    )
    
    parser.add_argument(
        '--val_csv',
        type=str,
        default='datasets/train/val_pairs.csv',
        help='Path to validation CSV (default: datasets/train/val_pairs.csv)'
    )
    
    parser.add_argument(
        '--model_out',
        type=str,
        default='models/lgbm_v1.pkl',
        help='Output path for model file (default: models/lgbm_v1.pkl)'
    )
    
    parser.add_argument(
        '--num_boost_round',
        type=int,
        default=2000,
        help='Maximum number of boosting rounds (default: 2000)'
    )
    
    parser.add_argument(
        '--early_stopping_rounds',
        type=int,
        default=50,
        help='Early stopping rounds (default: 50)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        choices=['train', 'evaluate'],
        default='train',
        help='Task to perform: train or evaluate (default: train)'
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        default='outputs',
        help='Directory for output files (default: outputs)'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("LIGHTGBM RECOMMENDATION MODEL")
    logger.info("=" * 60)
    logger.info(f"Task: {args.task}")
    logger.info(f"Training data: {args.train_csv}")
    logger.info(f"Validation data: {args.val_csv}")
    logger.info(f"Model output: {args.model_out}")
    logger.info(f"Random seed: {args.seed}")
    
    try:
        # Load data
        train_df, val_df = load_training_data(args.train_csv, args.val_csv)
        
        # Safety check for large datasets
        if len(train_df) > 500000 and args.num_boost_round > 1000:
            logger.warning("=" * 60)
            logger.warning("WARNING: Large dataset detected!")
            logger.warning(f"Training samples: {len(train_df):,}")
            logger.warning(f"Boosting rounds: {args.num_boost_round}")
            logger.warning("Consider reducing --num_boost_round for faster training")
            logger.warning("=" * 60)
        
        # Prepare features
        train_df_prep, feature_cols, categorical_features = prepare_features(train_df)
        val_df_prep, _, _ = prepare_features(val_df)
        
        if args.task == 'train':
            # Training mode
            logger.info("\n--- TRAINING MODE ---")
            
            # Set up parameters
            params = {
                'objective': 'binary',
                'boosting_type': 'gbdt',
                'metric': 'auc',
                'learning_rate': 0.03,
                'num_leaves': 128,
                'max_depth': 8,
                'min_child_samples': 20,
                'subsample': 0.8,
                'colsample_bytree': 0.7,
                'reg_alpha': 0.0,
                'reg_lambda': 0.0,
                'seed': args.seed,
                'verbose': -1
            }
            
            # Train model
            model, training_info = train_lightgbm(
                train_df_prep,
                val_df_prep,
                feature_cols,
                categorical_features,
                params=params,
                num_boost_round=args.num_boost_round,
                early_stopping_rounds=args.early_stopping_rounds,
                verbose_eval=50
            )
            
            # Evaluate model
            evaluation_results = evaluate_model(
                model,
                train_df_prep,
                val_df_prep,
                feature_cols,
                output_dir=args.output_dir
            )
            
            # Save model and metadata
            save_model_and_metadata(
                model,
                training_info,
                evaluation_results,
                args.model_out
            )
            
            logger.info("\n" + "=" * 60)
            logger.info("TRAINING SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✓ Model trained successfully")
            logger.info(f"✓ Best iteration: {training_info['best_iteration']}")
            logger.info(f"✓ Validation AUC: {evaluation_results['val_auc']:.4f}")
            logger.info(f"✓ Model saved to: {args.model_out}")
            logger.info(f"✓ Outputs saved to: {args.output_dir}/")
            
        else:
            # Evaluation mode
            logger.info("\n--- EVALUATION MODE ---")
            
            # Load model
            model = load_model(args.model_out)
            
            # Evaluate
            evaluation_results = evaluate_model(
                model,
                train_df_prep,
                val_df_prep,
                feature_cols,
                output_dir=args.output_dir
            )
            
            logger.info("\n" + "=" * 60)
            logger.info("EVALUATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"✓ Model evaluated successfully")
            logger.info(f"✓ Training AUC: {evaluation_results['train_auc']:.4f}")
            logger.info(f"✓ Validation AUC: {evaluation_results['val_auc']:.4f}")
            logger.info(f"✓ Outputs saved to: {args.output_dir}/")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.error("Make sure training data exists. Run create_training_data.py first.")
        return 1
    except Exception as e:
        logger.error(f"Error during model training: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
