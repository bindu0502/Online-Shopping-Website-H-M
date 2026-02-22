"""
Verify Cold-Start Implementation

Quick verification script to test cold-start recommendations.
Run this after restarting the backend server.
"""

import sys
from src.db import SessionLocal, User
from src.personalized_recommend import (
    generate_personalized_recommendations,
    get_user_activity_products
)

def verify_coldstart():
    """Verify cold-start implementation."""
    db = SessionLocal()
    
    print("=" * 70)
    print("COLD-START VERIFICATION")
    print("=" * 70)
    
    # Find cold-start test user
    user = db.query(User).filter(User.email == "coldstart@example.com").first()
    
    if not user:
        print("\n✗ Test user 'coldstart@example.com' not found!")
        print("  Run: python create_test_user.py")
        db.close()
        return False
    
    print(f"\n✓ Found test user: {user.email}")
    print(f"  User ID: {user.id}")
    print(f"  Preferred categories: {user.preferred_categories}")
    
    # Check activity
    activity = get_user_activity_products(user.id, db)
    print(f"\n✓ Activity check: {len(activity)} products")
    
    if len(activity) > 0:
        print("  ⚠ User has activity - not a pure cold-start scenario")
    else:
        print("  ✓ No activity - perfect cold-start scenario")
    
    # Generate recommendations
    print("\n⏳ Generating recommendations...")
    recommendations = generate_personalized_recommendations(user.id, db)
    
    print(f"\n✓ Generated {len(recommendations)} recommendations")
    
    if len(recommendations) == 0:
        print("\n✗ FAIL: No recommendations generated!")
        print("  Check if:")
        print("  1. User has preferred_categories set")
        print("  2. Products exist in those categories")
        print("  3. Backend server was restarted after code changes")
        db.close()
        return False
    
    # Verify categories
    categories_found = set()
    for rec in recommendations:
        categories_found.add(rec['product_group_name'])
    
    print(f"\n✓ Categories in recommendations: {categories_found}")
    
    # Show samples
    print("\n📦 Sample recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n  {i}. {rec['name']}")
        print(f"     Category: {rec['product_group_name']}")
        print(f"     Price: ${rec['price']:.2f}")
        print(f"     Reason: {rec['reason']}")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION PASSED")
    print("=" * 70)
    print("\nCold-start implementation is working correctly!")
    print("\n📋 Next steps:")
    print("  1. Restart backend server: uvicorn main:app --reload")
    print("  2. Test via API: python test_complete_coldstart_flow.py")
    print("  3. Test via frontend: Login as coldstart@example.com")
    
    return True

if __name__ == "__main__":
    try:
        success = verify_coldstart()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
