"""Check how many products have images."""
from src.db import SessionLocal, Product

db = SessionLocal()

total = db.query(Product).count()
with_images = db.query(Product).filter(
    Product.image_path.isnot(None), 
    Product.image_path != ''
).count()

print(f"Total products: {total}")
print(f"With images: {with_images}")
print(f"Without images: {total - with_images}")

if with_images > 0:
    sample = db.query(Product).filter(Product.image_path.isnot(None)).first()
    print(f"\nSample product with image:")
    print(f"  Article ID: {sample.article_id}")
    print(f"  Name: {sample.name}")
    print(f"  Image: {sample.image_path}")

db.close()
