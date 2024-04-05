from django.shortcuts import render, redirect
from .models import Product, Listing, UserProfile, UserPurchasedItem
from django.db.models import Q
from .get_s3_urls import get_s3_object_urls, save_urls_to_database
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
import stripe
from django.conf import settings
import json

def home(request):
    # Fetch all products from the database
    products_complimentary = Product.objects.filter(price=0)[:6]
    products_premium = Product.objects.filter(price__gt=0)[:6]

    query = request.GET.get('query')

    if query:
        # Perform the search using a case-insensitive search on the product name and description
        product_results = Product.objects.filter(Q(name__icontains=query.lower()) | Q(description__icontains=query.lower()))
        listing_results = Listing.objects.filter(Q(dataset_name__icontains=query.lower()) | Q(dataset_description__icontains=query.lower()))
    else:
        product_results = None
        listing_results = None

  
    # Call the get_s3_urls function to get the S3 URLs
    folder_name = 'web-data'
    urls = get_s3_object_urls('pairit-product-files', folder_name)
    
    # Check if all URLs already exist in the database
    for url in urls:
        if not Product.objects.filter(file_path__in=url).exists():
            # Save URLs to the database
            save_urls_to_database(urls)

    # Pass the categorized products and search results to the template
    return render(request, 'home.html', {'products_complimentary': products_complimentary,
                                         'products_premium': products_premium,
                                         'product_results': product_results,
                                         'listing_results': listing_results,
                                         'query': query})

def find_data(request):
    # Fetch all products and listings from the database
    products = Product.objects.all()
    listings = Listing.objects.all()

    query = request.GET.get('query')

    if query:
        # Perform the search using a case-insensitive search on the product name and description
        product_results = Product.objects.filter(Q(name__icontains=query.lower()) | Q(description__icontains=query.lower()))
        listing_results = Listing.objects.filter(Q(dataset_name__icontains=query.lower()) | Q(dataset_description__icontains=query.lower()))
    else:
        product_results = None
        listing_results = None

    # Pass the categorized products, listings, and search results to the template
    return render(request,'find_data.html', { 'products': products,
                                              'listings': listings,
                                              'product_results': product_results,
                                              'listing_results': listing_results,
                                              'query': query})
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        # Validate input
        if len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password should be at least 6 characters long',
                                                    'username': username,
                                                    'email': email})

        if password != cpassword:
            return render(request, 'signup.html', {'error': 'Passwords do not match',
                                                    'username': username,
                                                    'email': email})

        # Check uniqueness of username and email
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists',
                                                    'username': username,
                                                    'email': email})

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already exists',
                                                    'username': username,
                                                    'email': email})

        # Create a new user using Django's built-in User model
        user = User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')

        # # Optionally, log in the user after signup
        # user = authenticate(request, username=username, password=password)
        # if user is not None:
        #     login(request, user)
        #     # Redirect to a success page
        #     return redirect('home')  # Replace 'home' with the name of your home page URL

    return render(request, 'signup.html')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate input
        if not username or not password:
            return render(request, 'login.html', {'error': 'Please provide both username and password'})

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user) 
            # Redirect to a success page
            return redirect('home') 
        else:
            # Return an invalid login error message
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login/') 
def share_data(request):
    user = request.user
    user_listings = Listing.objects.filter(username=user)
    aws_listings = Product.objects.filter(username=user)
    return render(request, 'share_data.html', {'user_listings': user_listings, 'aws_listings': aws_listings})

@login_required(login_url='/login/') 
def get_listing_details(request):
    if request.method == 'GET':
        listing_id = request.GET.get('listing_id')
        try:
            listing = Listing.objects.get(id=listing_id)
            data = {
                'dataset_name': listing.dataset_name,
                'dataset_description': listing.dataset_description,
                'dataset_image': listing.dataset_image.url,
                'dataset_file_path': listing.dataset_file_path.url,
                'dataset_price': listing.dataset_price
            }
            return JsonResponse(data)
        except Listing.DoesNotExist:
            return JsonResponse({'error': 'Listing not found'}, status=404)

@login_required(login_url='/login/') 
def add_data(request):  
    if request.method == 'POST':
    
        # Extract data from the request
        dataset_name = request.POST.get('name')
        dataset_description = request.POST.get('description')
        dataset_price = request.POST.get('price')
        dataset_image = request.FILES.get('image')
        dataset_file_path = request.FILES.get('file')
        datasheet_file_path = request.FILES.get('datas-sheet')

         # Validate if price is positive
        if dataset_price is not None:
            try:
                dataset_price = float(dataset_price)
                if dataset_price < 0:
                    messages.error(request, 'Price should be a positive value')
                    return render(request, 'share_data.html', {'name': dataset_name, 'description': dataset_description})
            except ValueError:
                messages.error(request, 'Invalid price format')
                return render(request, 'share_data.html', {'name': dataset_name, 'description': dataset_description})

        error_messages = []

       # Validate file types
        error_messages = []
        if dataset_file_path:
            if not dataset_file_path.name.endswith(('.csv', '.xlsx')):
                error_messages.append('Invalid file type for dataset')
        if dataset_image:
            if not dataset_image.name.endswith(('.jpg', '.jpeg', '.png')):
                error_messages.append('Invalid file type for image')
        if datasheet_file_path:
            if not datasheet_file_path.name.endswith(('.pdf', '.docx')):
                error_messages.append('Invalid file type for datasheet')

        if error_messages:
            for error_message in error_messages:
                messages.error(request, error_message)
            return render(request, 'share_data.html', {'name': dataset_name, 'description': dataset_description})  # Pass back previous data
        # Ensure that dataset_price is always 0
        dataset_price = 0
        
        # Create a new Listing object
        new_listing = Listing(
            username=request.user,
            dataset_name=dataset_name,
            dataset_description=dataset_description,
            dataset_price=dataset_price,
            dataset_image=dataset_image,
            dataset_file_path=dataset_file_path,
            datasheet_file_path=datasheet_file_path
        )
        # Save the object
        new_listing.save()
        messages.success(request, 'Congratulations your dataset successfully published 🎉🥳')
        return HttpResponseRedirect(request.path)
    return redirect('share_data')

@login_required(login_url='/login/') 
def update_data(request):
    if request.method == 'POST':
        dataset_name = request.POST.get('name')
        dataset_description = request.POST.get('description')
        dataset_image = request.FILES.get('image')
        dataset_file_path = request.FILES.get('file')
        listing_id = request.POST.get('selectField')
        datasheet_file_path = request.FILES.get('listing-datasheet')

         # Validate file types
        error_messages = []
        if dataset_file_path:
            if not dataset_file_path.name.endswith(('.csv', '.xlsx')):
                error_messages.append('Invalid file type for dataset')
                
        if dataset_image:
            if not dataset_image.name.endswith(('.jpg', '.jpeg', '.png')):
                error_messages.append('Invalid file type for image')

        if datasheet_file_path:
            if not datasheet_file_path.name.endswith(('.pdf', '.docx')):
                error_messages.append('Invalid file type for datasheet')

        if error_messages:
            for error_message in error_messages:
                messages.error(request, error_message)
            return redirect('share_data')
                
        # Retrieve the user's listing
        try:
            selected_listing = Listing.objects.get(pk=listing_id, username=request.user)
        except Listing.DoesNotExist:
            # Handle the case where the listing does not exist or does not belong to the user
            return HttpResponse("Listing not found or does not belong to the user", status=404)

        # Update the listing attributes
        selected_listing.dataset_name = dataset_name
        selected_listing.dataset_description = dataset_description
        if dataset_image:
            selected_listing.dataset_image = dataset_image
        if dataset_file_path:
            selected_listing.dataset_file_path = dataset_file_path
        if datasheet_file_path:
            selected_listing.datasheet_file_path = datasheet_file_path


        # Save the updated listing
        selected_listing.save()

        messages.success(request, 'Your listing successfully updated')
        return redirect('share_data')
    else:
        # Handle the case where the request method is not POST
        return render(request, 'share_data.html')

@login_required(login_url='/login/') 
def rating(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        listing_id = request.POST.get('listing_id')
        rating_value = request.POST.get('rating')
        username = request.POST.get('username')

        if username == 'admin':
            listing = Product.objects.get(id=product_id)
        else:
            listing = Listing.objects.get(id=listing_id)
        
        previous_rating = listing.rating
        previous_total_rating = listing.total_ratings
        new_rating = previous_rating + int(rating_value)
        new_total_rating = previous_total_rating + 1
        avg_rating = new_rating / new_total_rating
        listing.rating = new_rating
        listing.total_ratings = new_total_rating
        listing.avg_ratings = avg_rating
        listing.save()
        
        messages.success(request, 'Rating submitted successfully.')
    else:
        messages.error(request, 'Rating submission failed.')
    
    # Redirect back to the same page
    return redirect(request.META.get('HTTP_REFERER'))

def prod_info(request, product_id, username):
    # Check if the user is an admin
    if username == "admin":
        product = Product.objects.get(id=product_id)
        context = {'product': product}
    else:
        listing = Listing.objects.get(id=product_id)
        context = {'listing': listing}
    
    return render(request, 'product_info.html', context)

@login_required(login_url='/login/') 
def account(request):
    user = request.user
    username = user.username
    try:
        profile = UserProfile.objects.get(username=user)
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        city = request.POST.get('city')
        facebook = request.POST.get('facebook')
        instagram = request.POST.get('city')
        twitter = request.POST.get('twitter')

        # Check if avatar file is provided and has valid image extension
        if avatar:
            if not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                messages.error(request, 'Please upload a valid image file (jpg, jpeg, or png).')
                return redirect('account')

        if profile:
            # If profile exists, update it
           
            profile.avatar = avatar if avatar else profile.avatar
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email = email
            profile.phone = phone
            profile.country = country
            profile.city = city
            profile.facebook_link = facebook
            profile.instagram_link = instagram
            profile.twitter_link  = twitter
            profile.save()
        else:
            # If profile doesn't exist, create a new one
            profile = UserProfile.objects.create(
                username=user,
                avatar=avatar,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                country=country,
                city=city,
                facebook_link = facebook,
                instagram_link = instagram,
                twitter_link = twitter
            )

        messages.success(request, 'Profile updated successfully.')

    context = {
        'profile': profile,
        'username': username
    }

    return render(request, 'account.html', context)

@login_required(login_url='/login/') 
def cart(request):
    return render(request, 'cart.html')

@login_required(login_url='/login/') 
def generate_payment_link(request):
    if request.method == 'POST':
        cart = request.POST.get('cart')
        if not cart:
            return JsonResponse({'error': 'Cart is empty.'}, status=400)

        # Parse cart data and calculate total price
        cart = json.loads(cart)
        line_items = []
        total_price = 0
        for item in cart:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(float(item['price']) * 100),  # Convert price to cents
                },
                'quantity': 1,
            })
            total_price += float(item['price'])

        # Generate a payment link using Stripe
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY 
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://127.0.0.1:8000/payment_success/',  # Redirect URL after successful payment
            cancel_url='http://127.0.0.1:8000/cancel/',    # Redirect URL if the user cancels the payment
        )
        request.session['pending_purchase'] = cart
        return JsonResponse({'payment_url': session.url})

    else:
        return redirect('login')

@login_required(login_url='/login/') 
def payment_success(request):
    # Retrieve stored purchase details from session
    cart = request.session.get('pending_purchase')
    if cart:
        for item in cart:
            # Create entry in the database for each item in the cart
            UserPurchasedItem.objects.create(
                user=request.user,
                item_id=item.get('id'),
                item_name=item.get('name'),
                item_price=item.get('price'),
                item_posted_by=item.get('owner'),
            )

        # Clear the stored cart from session after successful purchase
        del request.session['pending_purchase']

        return render(request, 'successful_payment.html')
        # return JsonResponse({'message': 'Payment successful and purchase details saved.'})
    else:
        return JsonResponse({'error': 'No items found in the cart.'})
    
@login_required(login_url='/login/') 
def purchased_items(request):
    # Retrieve all entries of the logged-in user from UserPurchasedItem model
    purchased_items = UserPurchasedItem.objects.filter(user=request.user)

    # Create an empty list to store the details of purchased items
    items_details = []

    # Loop through purchased items
    for item in purchased_items:
        if item.item_posted_by == 'admin':
            # If the item is posted by admin, fetch details from Product model
            product = Product.objects.get(id=item.item_id)
            items_details.append({
                'id': product.id,
                'name': product.name,
                'price': item.item_price,
                'posted_by': 'admin',
                'product_img': product.image,
                'product_dataset_url': product.file_path,
                'datasheet_url': product.datasheet_file_path
            })
        else:
            # If the item is posted by a user, fetch details from Listing model
            listing = Listing.objects.get(id=item.item_id)
            items_details.append({
                'id': listing.id,
                'name': listing.dataset_name,
                'price': item.item_price,
                'posted_by': listing.username, 
                'listing_img': listing.dataset_image,
                'listing_dataset_url': listing.dataset_file_path,
                'datasheet_url': listing.datasheet_file_path
            })

    # Pass the purchased items details to the template
    return render(request, 'purchased_items.html', {'items_details': items_details})

@login_required(login_url='/login/') 
def successful_payment(request):
    return render(request, 'successful_payment.html')

def community(request):
    return render(request, 'community.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')