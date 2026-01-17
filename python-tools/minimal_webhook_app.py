from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os, json, asyncio
import httpx

app = FastAPI()


@app.post('/stripe/webhook')
async def stripe_webhook(request: Request):
    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid JSON')

    event_id = event.get('id')
    event_type = event.get('type')

    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

    # Idempotency check (best-effort)
    if SUPABASE_URL and SUPABASE_SERVICE_KEY and event_id:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/stripe_events?event_id=eq.{event_id}&select=id", headers=headers)
                if r.status_code == 200 and r.json():
                    return JSONResponse({'received': True, 'duplicate': True})
                # persist event
                await client.post(f"{SUPABASE_URL}/rest/v1/stripe_events", json=[{
                    'event_id': event_id,
                    'event_type': event_type,
                    'payload': event
                }], headers={**headers, 'Prefer': 'resolution=merge-duplicates'})
        except Exception:
            pass

    # Handle checkout.session.completed
    if event_type == 'checkout.session.completed':
        session = event.get('data', {}).get('object', {})
        customer_email = session.get('customer_email')
        if SUPABASE_URL and SUPABASE_SERVICE_KEY and customer_email:
            headers = {
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Content-Type': 'application/json'
            }
            payload = {
                'email': customer_email,
                'stripe_customer_id': session.get('customer'),
                'stripe_subscription_id': session.get('subscription') or session.get('metadata', {}).get('subscription_id'),
                'last_paid_at': __import__('datetime').datetime.utcnow().isoformat()
            }
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(f"{SUPABASE_URL}/rest/v1/subscriptions", json=[payload], headers={**headers, 'Prefer': 'resolution=merge-duplicates'})
            except Exception:
                pass

    return JSONResponse({'received': True})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('minimal_webhook_app:app', host='127.0.0.1', port=int(os.getenv('PORT', '8001')))
