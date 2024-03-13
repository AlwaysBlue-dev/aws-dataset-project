from django.shortcuts import render
from .models import Product
from django.db.models import Q
from .get_s3_urls import get_s3_object_urls, save_urls_to_database

def home(request):
    # Fetch all products from the database
    products_complimentary = Product.objects.filter(price=0)[:6]
    products_premium = Product.objects.filter(price__gt=0)[:6]

    query = request.GET.get('query')

    if query:
        # Perform the search using a case-insensitive search on the product name and description
        results = Product.objects.filter(Q(name__icontains=query.lower()) | Q(description__icontains=query.lower()))
    else:
        results = None

    # Call the get_s3_urls function to get the S3 URLs
    urls = get_s3_object_urls('pairit-product-files')
    
    # Check if all URLs already exist in the database
    for url in urls:
        if not Product.objects.filter(file_path__in=url).exists():
            # Save URLs to the database
            save_urls_to_database(urls)

    # Pass the categorized products and search results to the template
    return render(request, 'home.html', {'products_complimentary': products_complimentary,
                                         'products_premium': products_premium,
                                         'results': results,
                                         'query': query})

def find_data(request):
    # Fetch all products from the database
    products = Product.objects.all()

    query = request.GET.get('query')

    if query:
        # Perform the search using a case-insensitive search on the product name and description
        results = Product.objects.filter(Q(name__icontains=query.lower()) | Q(description__icontains=query.lower()))
    else:
        results = None

    # Pass the categorized products and search results to the template
    return render(request,'find_data.html',{ 'products': products,
                                            'results': results,
                                            'query': query})