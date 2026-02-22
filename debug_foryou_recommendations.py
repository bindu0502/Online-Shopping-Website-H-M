"""Debug For You recommendations for current user."""
from src.db import SessionLocal, User, CartItem, Product
from src.personalized_recommend import (
    get_user_activity_products,
    generate_personalized_recommendations,
    get_similar_products_optimized
)

db = SessionLocal()

# Get first user
user = db.query(User).first()
print(f"User: {user.email} (ID: {user.id})")

# Check cart items
cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
print(f"\nCart items: {len(cart_items)}")

for item in cart_items:
    product = db.query(Product).filter(Product.article_id == item.article_id).first()
    if product:
        print(f"\n  {product.name}")
        print(f"    Article ID: {product.article_id}")
        print(f"    Category: {product.product_group_name}")
        print(f"    Color: {product.primary_color}")
        print(f"    Has Image: {'✓' if product.image_path else '✗'}")
        
        # Try to find similar products
        print(f"    Finding similar products...")
        similar = get_similar_products_optimized(
            product, db, {product.article_id}, top_n=5
        )
        print(f"    Found {len(similar)} similar products")
        
        if similar:
            for i, (sim_prod, score) in enumerate(similar[:3], 1):
                print(f"      {i}. {sim_prod.name[:40]} (score: {score:.1f})")
        else:
            print(f"      ✗ No similar products found!")
            
            # Debug why
            same_category = db.query(Product).filter(
                Product.product_group_name == product.product_group_name,
                Product.image_path.isnot(None),
                Product.image_path != ''
            ).count()
            print(f"      Products in same category with images: {same_category}")

# Generate full recommendations
print(f"\n{'='*70}")
print("FULL RECOMMENDATIONS")
print('='*70)

recommendations = generate_personalized_recommendations(user.id, db, 5)
print(f"\nTotal recommendations: {len(recommendations)}")

if recommendations:
    print("\nTop 5:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['name'][:50]}")
        print(f"   Category: {rec['product_group_name']}")
        print(f"   Color: {rec['primary_color']}")
        print(f"   Score: {rec['score']:.1f}")
else:
    print("\n✗ No recommendations generated!")

db.close()
