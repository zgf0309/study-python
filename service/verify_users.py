import json
from app.routes.users import read_users

def test_read_users():
    # Test page=1
    response1 = read_users(page=1)
    body1 = json.loads(response1.body)
    print(f"Page 1 response: {body1}")
    has_total1 = 'total' in body1
    
    # Test page=2
    response2 = read_users(page=2)
    body2 = json.loads(response2.body)
    print(f"Page 2 response: {body2}")
    has_total2 = 'total' in body2
    
    print(f"Page 1 has total: {has_total1}")
    print(f"Page 2 has total: {has_total2}")
    
    if not has_total1 and has_total2:
        print("Verification SUCCESS: Page 1 does NOT have total, Page 2 HAS total.")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    try:
        test_read_users()
    except Exception as e:
        import traceback
        traceback.print_exc()
