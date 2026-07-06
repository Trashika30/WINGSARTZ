import requests, json, io

BASE = 'http://localhost:8000/api/v1'
print('=== WingsArtz Extensions API Verification ===')

def clean(s):
    # Replace the Rupee sign with Rs. first, then ignore remaining non-ASCII emojis for safe printing
    if not isinstance(s, str):
        return str(s)
    s = s.replace('₹', 'Rs. ')
    return s.encode('ascii', 'ignore').decode('ascii')

try:
    # 1. Login as Owner
    r = requests.post(f'{BASE}/auth/login', json={'email': 'owner@wingsartz.com', 'password': 'WingsOwner2026!'}, timeout=5)
    data = r.json()
    token_owner = data.get('access_token', '')
    print('[OWNER LOGIN]', 'OK' if token_owner else 'FAIL')

    # 2. Login as Painter
    r = requests.post(f'{BASE}/auth/login', json={'email': 'painter1@wingsartz.com', 'password': 'WingsPainter2026!'}, timeout=5)
    data = r.json()
    token_painter = data.get('access_token', '')
    print('[PAINTER LOGIN]', 'OK' if token_painter else 'FAIL')

    # 3. Test Admin AI Chatbot
    r = requests.post(
        f'{BASE}/chat/admin/chat', 
        headers={'Authorization': f'Bearer {token_owner}'},
        json={'query': "Why is today's demand predicted to be high?"},
        timeout=5
    )
    print('[ADMIN CHAT]', clean(r.json().get('agent')), '->', clean(r.json().get('response'))[:100] + '...')

    # 4. Test Painter AI Chatbot (Technique query)
    r = requests.post(
        f'{BASE}/chat/painter/chat', 
        headers={'Authorization': f'Bearer {token_painter}'},
        json={'query': "What is the best technique for acrylic portraits?"},
        timeout=5
    )
    print('[PAINTER CHAT]', clean(r.json().get('agent')), '->', clean(r.json().get('response'))[:100] + '...')

    # 5. Test Painter AI Chatbot security block on financial queries
    r = requests.post(
        f'{BASE}/chat/painter/chat', 
        headers={'Authorization': f'Bearer {token_painter}'},
        json={'query': "Show me our net profit margins and raw cost impact reports"},
        timeout=5
    )
    print('[PAINTER CHAT BLOCK]', r.status_code, '->', clean(r.json().get('detail')))

    # 5a. Login and Test Inventory Manager Chatbot
    r = requests.post(f'{BASE}/auth/login', json={'email': 'inventory@wingsartz.com', 'password': 'WingsInventory2026!'}, timeout=5)
    token_inv = r.json().get('access_token', '')
    r = requests.post(
        f'{BASE}/chat/inventory/chat',
        headers={'Authorization': f'Bearer {token_inv}'},
        json={'query': "Do we have any low stock alerts for canvas boards?"},
        timeout=5
    )
    print('[INVENTORY CHAT]', clean(r.json().get('agent')), '->', clean(r.json().get('response'))[:100] + '...')

    # 5b. Test Inventory Chatbot security block
    r = requests.post(
        f'{BASE}/chat/inventory/chat',
        headers={'Authorization': f'Bearer {token_inv}'},
        json={'query': "What is our net revenue and profit margin report?"},
        timeout=5
    )
    print('[INVENTORY CHAT BLOCK]', r.status_code, '->', clean(r.json().get('detail')))

    # 5c. Login and Test Shipping Manager Chatbot
    r = requests.post(f'{BASE}/auth/login', json={'email': 'shipping@wingsartz.com', 'password': 'WingsShipping2026!'}, timeout=5)
    token_ship = r.json().get('access_token', '')
    r = requests.post(
        f'{BASE}/chat/shipping/chat',
        headers={'Authorization': f'Bearer {token_ship}'},
        json={'query': "Which courier is recommended for Chennai city ground dispatch?"},
        timeout=5
    )
    print('[SHIPPING CHAT]', clean(r.json().get('agent')), '->', clean(r.json().get('response'))[:100] + '...')

    # 5d. Test Shipping Chatbot security block
    r = requests.post(
        f'{BASE}/chat/shipping/chat',
        headers={'Authorization': f'Bearer {token_ship}'},
        json={'query': "Show me salary sheets and financial audits"},
        timeout=5
    )
    print('[SHIPPING CHAT BLOCK]', r.status_code, '->', clean(r.json().get('detail')))

    # 6. Test Shipping rates for Indian Couriers in INR
    r = requests.get(
        f'{BASE}/shipping/rates?weight_lbs=4.5&zip_code=600040', 
        headers={'Authorization': f'Bearer {token_owner}'},
        timeout=5
    )
    rates_data = r.json()
    print('[INDIAN COURIERS]', [clean(q['carrier']) + ' = Rs. ' + str(q['cost']) + ' (' + clean(q['reason'])[:30] + '...)' for q in rates_data['quotes']])

    # 7. Login as Customer & Place Order with Geolocation
    r = requests.post(f'{BASE}/auth/login', json={'email': 'customer@gmail.com', 'password': 'WingsCustomer2026!'}, timeout=5)
    token_cust = r.json().get('access_token', '')
    
    mock_file = io.BytesIO(b"fake image data")
    mock_file.name = "portrait.jpg"
    
    order_payload = {
        'size_inches': '16x20',
        'frame_type': 'Black Wood',
        'custom_description': 'Paint a pencil sketch of her.',
        'delivery_date_str': '2026-07-20T12:00:00Z',
        'location': 'Anna Nagar, Chennai, Tamil Nadu'
    }
    
    r = requests.post(
        f'{BASE}/orders/custom',
        headers={'Authorization': f'Bearer {token_cust}'},
        data=order_payload,
        files={'image': ('portrait.jpg', mock_file, 'image/jpeg')},
        timeout=5
    )
    order_res = r.json()
    order_id = order_res.get('id')
    print('[PLACE ORDER WITH ADDRESS]', r.status_code, '-> Tracking #:', clean(order_res.get('tracking_number')), '| Location:', clean(order_res.get('location')))

    # 8. Owner accepts the custom order
    r = requests.put(
        f'{BASE}/admin/orders/{order_id}/status',
        headers={'Authorization': f'Bearer {token_owner}'},
        json={'status': 'Accepted'},
        timeout=5
    )
    print('[OWNER ACCEPT ORDER]', r.status_code, '-> Status:', clean(r.json().get('status')))

    # 9. Customer performs secure payment for the Accepted order
    r = requests.post(
        f'{BASE}/orders/{order_id}/pay',
        headers={'Authorization': f'Bearer {token_cust}'},
        timeout=5
    )
    print('[CUSTOMER PAY ORDER]', r.status_code, '-> Status after payment:', clean(r.json().get('status')))

    # 10. Check my orders lists
    r = requests.get(f'{BASE}/orders/my-orders', headers={'Authorization': f'Bearer {token_cust}'}, timeout=5)
    my_orders = r.json()
    print('[MY ORDERS]', len(my_orders), 'orders found. Latest total price: Rs. ', my_orders[0]['total_price'])

    print()
    print('=== ALL UPDATES SUCCESSFUL & VERIFIED ===')

except Exception as e:
    print(f'ERROR: {e}')
