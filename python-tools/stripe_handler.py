"""
Verity Systems - Stripe Payment Handler
Secure payment processing for subscription and premium features

Features:
- Subscription management
- One-time payments
- Webhook handling
- Usage-based billing
- Invoice management
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import stripe
from dotenv import load_dotenv

load_dotenv()

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Product IDs (create these in Stripe Dashboard)
STRIPE_PRODUCTS = {
    'starter': os.environ.get('STRIPE_STARTER_PRICE_ID'),
    'professional': os.environ.get('STRIPE_PROFESSIONAL_PRICE_ID'),
    'enterprise': os.environ.get('STRIPE_ENTERPRISE_PRICE_ID'),
}


class StripePaymentHandler:
    """Manages all Stripe payment operations"""
    
    @staticmethod
    def create_checkout_session(
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription
        
        Args:
            user_id: User identifier
            price_id: Stripe price ID
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancellation
            customer_email: Customer email address
            
        Returns:
            Checkout session data
        """
        try:
            session_params = {
                'payment_method_types': ['card'],
                'line_items': [
                    {
                        'price': price_id,
                        'quantity': 1
                    }
                ],
                'mode': 'subscription',
                'success_url': success_url,
                'cancel_url': cancel_url,
                'client_reference_id': user_id,
            }
            
            if customer_email:
                session_params['customer_email'] = customer_email
            
            session = stripe.checkout.Session.create(**session_params)
            return {
                'session_id': session.id,
                'url': session.url,
                'status': 'created'
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'items': [
                    {
                        'price_id': item.price.id,
                        'product_id': item.price.product
                    }
                    for item in subscription.items
                ]
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve subscription: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: If True, cancel at period end; if False, cancel immediately
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'canceled_at': subscription.canceled_at
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    @staticmethod
    def update_subscription(
        subscription_id: str,
        price_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a subscription (e.g., upgrade/downgrade plan)"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            if price_id:
                # Get the current item
                item_id = subscription.items.data[0].id
                
                # Update with new price
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    items=[{
                        'id': item_id,
                        'price': price_id
                    }],
                    proration_behavior='always_invoice'
                )
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'items': [
                    {
                        'price_id': item.price.id,
                        'product_id': item.price.product
                    }
                    for item in subscription.items
                ]
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to update subscription: {str(e)}")
    
    @staticmethod
    def create_customer(
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer"""
        try:
            customer_params = {'email': email}
            if name:
                customer_params['name'] = name
            if metadata:
                customer_params['metadata'] = metadata
            
            customer = stripe.Customer.create(**customer_params)
            return {
                'customer_id': customer.id,
                'email': customer.email
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    @staticmethod
    def create_usage_record(
        subscription_item_id: str,
        quantity: int,
        action: str = 'set'
    ) -> Dict[str, Any]:
        """
        Create a usage record for metered billing
        
        Args:
            subscription_item_id: Stripe subscription item ID
            quantity: Usage quantity
            action: 'set' or 'increment'
        """
        try:
            record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                action=action,
                timestamp=int(datetime.now().timestamp())
            )
            return {
                'id': record.id,
                'subscription_item': record.subscription_item,
                'quantity': record.quantity,
                'timestamp': record.timestamp
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create usage record: {str(e)}")
    
    @staticmethod
    def handle_webhook(body: str, signature: str) -> Dict[str, Any]:
        """
        Verify and process Stripe webhook
        
        Args:
            body: Raw webhook body
            signature: Stripe signature header
            
        Returns:
            Webhook event data
        """
        try:
            event = stripe.Webhook.construct_event(
                body,
                signature,
                STRIPE_WEBHOOK_SECRET
            )
            
            # Handle specific events
            if event['type'] == 'customer.subscription.created':
                return {
                    'event_type': 'subscription_created',
                    'subscription_id': event['data']['object']['id'],
                    'customer_id': event['data']['object']['customer'],
                    'status': event['data']['object']['status']
                }
            
            elif event['type'] == 'customer.subscription.updated':
                return {
                    'event_type': 'subscription_updated',
                    'subscription_id': event['data']['object']['id'],
                    'status': event['data']['object']['status']
                }
            
            elif event['type'] == 'customer.subscription.deleted':
                return {
                    'event_type': 'subscription_deleted',
                    'subscription_id': event['data']['object']['id']
                }
            
            elif event['type'] == 'invoice.payment_succeeded':
                return {
                    'event_type': 'payment_succeeded',
                    'invoice_id': event['data']['object']['id'],
                    'customer_id': event['data']['object']['customer'],
                    'amount': event['data']['object']['amount_paid'],
                    'currency': event['data']['object']['currency']
                }
            
            elif event['type'] == 'invoice.payment_failed':
                return {
                    'event_type': 'payment_failed',
                    'invoice_id': event['data']['object']['id'],
                    'customer_id': event['data']['object']['customer']
                }
            
            else:
                return {
                    'event_type': 'unhandled',
                    'stripe_event_type': event['type']
                }
        
        except ValueError:
            raise Exception("Invalid webhook signature")
        except stripe.error.SignatureVerificationError:
            raise Exception("Webhook signature verification failed")
    
    @staticmethod
    def get_invoices(customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customer invoices"""
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
            return [
                {
                    'id': invoice.id,
                    'amount': invoice.amount_paid,
                    'currency': invoice.currency,
                    'date': invoice.created,
                    'status': invoice.status,
                    'pdf_url': invoice.invoice_pdf
                }
                for invoice in invoices.data
            ]
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get invoices: {str(e)}")
    
    @staticmethod
    def get_payment_methods(customer_id: str) -> List[Dict[str, Any]]:
        """Get customer payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return [
                {
                    'id': pm.id,
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year
                }
                for pm in payment_methods.data
            ]
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to get payment methods: {str(e)}")


# Pricing tier configuration - matches pricing.html
PRICING_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'currency': 'usd',
        'billing_period': 'free',
        'features': {
            'verifications_per_month': 300,
            'llm_models': 2,
            'data_sources': 5,
            'api_access': True,
            'email_support': False,
            'priority_processing': False,
            'batch_processing': False,
            'advanced_analytics': False
        }
    },
    'starter': {
        'name': 'Starter',
        'price': 4900,  # $49/month in cents
        'currency': 'usd',
        'billing_period': 'monthly',
        'features': {
            'verifications_per_month': 2000,
            'llm_models': 4,
            'data_sources': 15,
            'api_access': True,
            'email_support': True,
            'priority_processing': False,
            'batch_processing': False,
            'advanced_analytics': False
        }
    },
    'pro': {
        'name': 'Pro',
        'price': 9900,  # $99/month in cents
        'currency': 'usd',
        'billing_period': 'monthly',
        'features': {
            'verifications_per_month': 5000,
            'llm_models': 8,
            'data_sources': 27,
            'api_access': True,
            'email_support': True,
            'priority_processing': True,
            'batch_processing': True,
            'advanced_analytics': True
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 19900,  # $199/month in cents
        'currency': 'usd',
        'billing_period': 'monthly',
        'features': {
            'verifications_per_month': 15000,
            'ai_providers': 15,
            'team_members': 5,
            'api_access': True,
            'email_support': True,
            'priority_processing': True,
            'batch_processing': True,
            'advanced_analytics': True
        }
    },
    'business': {
        'name': 'Business',
        'price': 59900,  # $599/month in cents
        'currency': 'usd',
        'billing_period': 'monthly',
        'features': {
            'verifications_per_month': 60000,
            'ai_providers': 15,
            'team_members': 15,
            'sso': True,
            'api_access': True,
            'email_support': True,
            'priority_processing': True,
            'batch_processing': True,
            'advanced_analytics': True
        }
    },
    'business_plus': {
        'name': 'Business+',
        'price': 79900,  # $799/month in cents
        'currency': 'usd',
        'billing_period': 'monthly',
        'features': {
            'verifications_per_month': 75000,
            'ai_providers': 15,
            'team_members': None,  # Unlimited
            'sla_guarantee': '99.9%',
            'api_access': True,
            'email_support': True,
            'priority_processing': True,
            'batch_processing': True,
            'advanced_analytics': True,
            'dedicated_support': True
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 0,  # Custom pricing
        'currency': 'usd',
        'billing_period': 'custom',
        'features': {
            'verifications_per_month': None,  # Unlimited
            'ai_providers': 15,
            'team_members': None,  # Unlimited
            'api_access': True,
            'email_support': True,
            'priority_processing': True,
            'batch_processing': True,
            'advanced_analytics': True,
            'dedicated_support': True,
            'custom_integration': True,
            'sla_guarantee': 'Custom'
        }
    }
}
