# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

logger = logging.getLogger(__name__)

class TopProductsAPIView(APIView):
    def get(self, request, category_name):
        company_names = ["AMZ", "FLP", "SNP", "MYN", "AZO"]
        top_n = int(request.GET.get('top', 10))
        min_price = float(request.GET.get('minPrice', 0))
        max_price = float(request.GET.get('maxPrice', float('inf')))
        sort_by = request.GET.get('sortBy', 'rating')  # Default sorting by rating

        if top_n > 10:
            page = int(request.GET.get('page', 1))
        else:
            page = 1

        products = []

        client_id = "18fa805a-cbd2-4f64-bc72-6977f98548fa"
        client_secret = "nvkcOntPlUkJSGbU"

        for company_name in company_names:
            url = f'http://20.244.56.144/test/companies/{company_name}/categories/{category_name}/products'
            params = {
                'top': top_n,
                'minPrice': min_price,
                'maxPrice': max_price,
                'sortBy': sort_by
            }
            
            headers = {
                'clientID': client_id,
                'clientSecret': client_secret
            }

            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()  # Raise an exception for bad responses (e.g., 404, 500)

                if response.status_code == 200:
                    products.extend(response.json())
                else:
                    return Response(f'Failed to fetch data from {company_name}: {response.text}', status=status.HTTP_400_BAD_REQUEST)

            except requests.exceptions.RequestException as e:
                logger.error(f'Error occurred while fetching data from {company_name}: {str(e)}')
                return Response(f'Error occurred while fetching data from {company_name}: {str(e)}', status=status.HTTP_400_BAD_REQUEST)

        # Sort products based on sortBy parameter
        products.sort(key=lambda x: x.get(sort_by, 0), reverse=True)  # Sorting in descending order

        # Pagination
        start_index = (page - 1) * top_n
        end_index = start_index + top_n
        paginated_products = products[start_index:end_index]

        return Response(paginated_products)



logger = logging.getLogger(__name__)

class ProductDetailsAPIView(APIView):
    def get(self, request, category_name, product_id):
        client_id = "18fa805a-cbd2-4f64-bc72-6977f98548fa"
        client_secret = "nvkcOntPlUkJSGbU"
        
        url = f'http://20.244.56.144/test/companies/AMZ/categories/{category_name}/products/{product_id}'
        
        headers = {
            'clientID': client_id,
            'clientSecret': client_secret
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad responses (e.g., 404, 500)

            if response.status_code == 200:
                product_details = response.json()
                return Response(product_details)
            else:
                return Response(f'Failed to fetch product details for product_id {product_id}: {response.text}', status=response.status_code)

        except requests.exceptions.RequestException as e:
            logger.error(f'Error occurred while fetching product details for product_id {product_id}: {str(e)}')
            return Response(f'Error occurred while fetching product details for product_id {product_id}: {str(e)}', status=status.HTTP_400_BAD_REQUEST)