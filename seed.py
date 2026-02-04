import os
import django
import requests
import random
import urllib3
from django.core.files.base import ContentFile

# SSL warning hide karne ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from store.models import Category, Product

def seed_db():
    print("🧹 Cleaning database for Mega-Store update...")
    Product.objects.all().delete()

    # --- Categories ---
    electronics, _ = Category.objects.get_or_create(name="Electronics", slug="electronics")
    fashion, _ = Category.objects.get_or_create(name="Fashion", slug="fashion")
    home, _ = Category.objects.get_or_create(name="Home & Living", slug="home-living")
    sports, _ = Category.objects.get_or_create(name="Sports & Outdoors", slug="sports")
    beauty, _ = Category.objects.get_or_create(name="Beauty & Care", slug="beauty")
    books, _ = Category.objects.get_or_create(name="Books & Stationery", slug="books")

    # --- Mega List (25 Items) ---
    products_list = [
        # Electronics (Exact Device Matches)
        {"n": "iPhone 15 Pro", "p": 124900, "c": electronics, "u": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?q=80&w=1000"},
        {"n": "MacBook Pro M3", "p": 199999, "c": electronics, "u": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1000"},
        {"n": "Sony Wireless Headphones", "p": 29990, "c": electronics, "u": "https://images.unsplash.com/photo-1546435770-a3e426ff472b?q=80&w=1000"},
        {"n": "Samsung Odyssey G7", "p": 45000, "c": electronics, "u": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?q=80&w=1000"},
        {"n": "Apple Watch Ultra", "p": 89900, "c": electronics, "u": "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?q=80&w=1000"},
        
        # Fashion
        {"n": "Premium Cotton Hoodie", "p": 2499, "c": fashion, "u": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=1000"},
        {"n": "Nike Air Force 1", "p": 8200, "c": fashion, "u": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=1000"},
        {"n": "Luxury Wrist Watch", "p": 15000, "c": fashion, "u": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?q=80&w=1000"},
        {"n": "Denim Jacket", "p": 4500, "c": fashion, "u": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?q=80&w=1000"},
        
        # Home & Living
        {"n": "Ergonomic Office Chair", "p": 15500, "c": home, "u": "https://images.unsplash.com/photo-1505797149-43b0069ec26b?q=80&w=1000"},
        {"n": "Nespresso Coffee Machine", "p": 18000, "c": home, "u": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?q=80&w=1000"},
        {"n": "Smart Ambient Lamp", "p": 3200, "c": home, "u": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?q=80&w=1000"},
        
        # Sports
        {"n": "Mountain Bike", "p": 35000, "c": sports, "u": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?q=80&w=1000"},
        {"n": "Dumbbell Set 10kg", "p": 2500, "c": sports, "u": "https://images.unsplash.com/photo-1638536532686-d610adfc8e5c?q=80&w=1000"},
        {"n": "Yoga Mat", "p": 1200, "c": sports, "u": "https://images.unsplash.com/photo-1592432676554-2b6348924897?q=80&w=1000"},
        {"n": "Treadmill Pro", "p": 45000, "c": sports, "u": "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?q=80&w=1000"},
        
        # Beauty
        {"n": "Organic Face Serum", "p": 1500, "c": beauty, "u": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=1000"},
        {"n": "Electric Shaver", "p": 4500, "c": beauty, "u": "https://images.unsplash.com/photo-1621607512214-68297480165e?q=80&w=1000"},
        {"n": "Premium Fragrance", "p": 5500, "c": beauty, "u": "https://images.unsplash.com/photo-1541643600914-78b084683601?q=80&w=1000"},
        {"n": "Matte Lipstick Set", "p": 1800, "c": beauty, "u": "https://images.unsplash.com/photo-1586776977607-310e9c725c37?q=80&w=1000"},

        # Books
        {"n": "Hardbound Notebook", "p": 450, "c": books, "u": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?q=80&w=1000"},
        {"n": "Fountain Pen Set", "p": 2500, "c": books, "u": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?q=80&w=1000"},
        {"n": "Sci-Fi Novel", "p": 899, "c": books, "u": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=1000"},
        {"n": "Leather Journal", "p": 1200, "c": books, "u": "https://images.unsplash.com/photo-1512412023212-f099903b7ec8?q=80&w=1000"},
        {"n": "Calligraphy Set", "p": 3500, "c": books, "u": "https://images.unsplash.com/photo-1569424110759-322197be07c3?q=80&w=1000"}
    ]

    for p in products_list:
        product = Product.objects.create(
            name=p['n'], category=p['c'], price=p['p'],
            description=f"Authentic {p['n']} curated for NovaMarket.",
            stock=random.randint(5, 40)
        )

        try:
            # verify=False add kiya taaki SSL error na aaye
            res = requests.get(p['u'], timeout=20, verify=False)
            if res.status_code == 200:
                filename = f"{p['n'].lower().replace(' ', '_')}.jpg"
                product.image.save(filename, ContentFile(res.content), save=True)
                print(f"✅ Seeding: {p['n']}")
        except Exception as e:
            print(f"❌ Failed: {p['n']} | {e}")

    print(f"\n🚀 Success! NovaMarket now has {Product.objects.count()} Products across 6 Categories.")

if __name__ == '__main__':
    seed_db()
    