"""
Create Stripe products and prices for API subscription tiers and pay-per-use pricing.
Requires `STRIPE_SECRET_KEY` env var.
This script is idempotent: it will search for existing product by name and create if missing.
"""
import os
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

PRODUCTS = [
    {'id': 'api_starter', 'name': 'API Starter', 'monthly_cents': 4900},
    {'id': 'api_developer', 'name': 'API Developer', 'monthly_cents': 9900},
    {'id': 'api_pro', 'name': 'API Pro', 'monthly_cents': 19900},
    {'id': 'api_business', 'name': 'API Business', 'monthly_cents': 49900},
    {'id': 'api_enterprise', 'name': 'API Enterprise', 'monthly_cents': 99900},
]

PAY_PER_USE = [
    {'name': 'standard', 'display_name': 'Standard Verification', 'price_cents': 6},
    {'name': 'premium', 'display_name': 'Premium Verification', 'price_cents': 10},
    {'name': 'bulk', 'display_name': 'Bulk Verification', 'price_cents': 5},
    {'name': 'verify_plus', 'display_name': 'VerifyPlus Document', 'price_cents': 150},
]


def find_product_by_name(name):
    prods = stripe.Product.list(limit=100)
    for p in prods:
        if p['name'] == name:
            return p
    return None


def create_monthly_price(product_id, amount_cents):
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount_cents,
        currency='usd',
        recurring={'interval': 'month'}
    )
    return price


def create_metered_price(product_id, amount_cents):
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount_cents,
        currency='usd',
        recurring={'interval': 'month'},
        billing_scheme='per_unit'
    )
    return price


if __name__ == '__main__':
    if not stripe.api_key:
        print('STRIPE_SECRET_KEY not set')
        exit(1)

    print('Creating/updating subscription products...')
    for p in PRODUCTS:
        prod = find_product_by_name(p['name'])
        if not prod:
            prod = stripe.Product.create(name=p['name'])
            print('Created product', prod['id'])
        else:
            print('Found product', prod['id'])
        price = create_monthly_price(prod['id'], p['monthly_cents'])
        print('Created price', price['id'], 'for', p['name'])

    print('\nCreating pay-per-use metered products...')
    for p in PAY_PER_USE:
        prod = find_product_by_name(p['display_name'])
        if not prod:
            prod = stripe.Product.create(name=p['display_name'])
            print('Created product', prod['id'])
        else:
            print('Found product', prod['id'])
        price = create_metered_price(prod['id'], p['price_cents'])
        print('Created metered price', price['id'], 'for', p['display_name'])

    print('\nDone. Save the price IDs and wire them into your DB or config.')
