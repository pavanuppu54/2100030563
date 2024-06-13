import requests
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET
from uuid import uuid4

# Authentication details
AUTH_URL = "http://20.244.56.144/test/auth"
AUTH_BODY = {
    "companyName": "KL University",
    "clientID": "18fa805a-cbd2-4f64-bc72-6977f98548fa",
    "clientSecret": "nvkcOntPlUkJSGbU",
    "ownerName": "Uppu Jyothi Naga Pavan",
    "ownerEmail": "pavanuppu2002@gmail.com",
    "rollNo": "2100030563"
}

def get_access_token():
    try:
        response = requests.post(AUTH_URL, json=AUTH_BODY)
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Failed to get access token: {e}")
        return None

# List of companies to fetch data from
COMPANIES = ["AMZ", "FLP", "SNP", "MYN", "AZO"]

# Step 2: Create the main function to fetch and aggregate products from multiple companies

def fetch_products(cn, can, n, minp, maxp, access_token):
    url = f"http://20.244.56.144/test/companies/{cn}/categories/{can}/products"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"top": n, "minPrice": minp, "maxPrice": maxp}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch products for company {cn}: {e}")
        return []

@require_GET
def top_products(request, category_name):
    access_token = get_access_token()
    print(access_token)
    if not access_token:
        return JsonResponse({"error": "Failed to authenticate"}, status=500)

    n = int(request.GET.get("n", 10))
    pg = int(request.GET.get("pg", 1))
    minp = float(request.GET.get("minPrice", 0))
    maxp = float(request.GET.get("maxPrice", 1000000))
    sort_by = request.GET.get("sortBy", "price")
    order = request.GET.get("order", "asc")

    all_products = []
    for company in COMPANIES:
        products = fetch_products(company, category_name, n, minp, maxp, access_token)
        for product in products:
            product["company"] = company
            product["category"] = category_name
            product["id"] = str(uuid4())  # Generate a unique ID for each product
        all_products.extend(products)

    rorder = order == "desc"
    all_products = sorted(all_products, key=lambda x: x.get(sort_by, 0), reverse=rorder)

    total_products = len(all_products)
    start_index = (pg - 1) * n
    end_index = start_index + n
    paginated_products = all_products[start_index:end_index]

    response_data = {
        "total_products": total_products,
        "total_pages": (total_products + n - 1) // n,
        "current_page": pg,
        "products": paginated_products,
    }

    return JsonResponse(response_data)

@require_GET
def product_detail(request, category_name, product_id):
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({"error": "Failed to authenticate"}, status=500)

    # Search for the product in the previously fetched products
    # In a real-world application, you might want to store these in a cache or database
    all_products = []
    for company in COMPANIES:
        products = fetch_products(company, category_name, 1000, 0, 1000000, access_token)
        for product in products:
            product["company"] = company
            product["category"] = category_name
            product["id"] = str(uuid4())
        all_products.extend(products)

    for product in all_products:
        if product["id"] == product_id:
            return JsonResponse(product)

    return JsonResponse({"error": "Product not found"}, status=404)
