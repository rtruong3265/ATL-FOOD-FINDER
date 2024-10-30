from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import Restaurant, Review
from .retrieval import RestaurantFinder
from .retrieval import GooglePlacesAPI
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile

# Password reset view that works for both authenticated and unauthenticated users
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Profile

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not hasattr(user, 'profile'):
            # Handle case where user does not have a profile
            Profile.objects.create(user=user)

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')

        return render(request, 'users/reset_confirm.html')
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('reset_confirm')






def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            # Fetch the user using the email
            user = User.objects.get(email=email)

            # Generate token and UID for the password reset link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct password reset link
            reset_link = request.build_absolute_uri(f"/reset-confirm/{uid}/{token}/")

            # Send email with reset link
            send_mail(
                subject="Password Reset Request",
                message=f"Click the following link to reset your password: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')

    return render(request, 'users/password_reset.html')


restaurantDetails = []
profiles = Profile.objects.all()
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Validation logic...
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Try again!')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use. Try again!')
            return redirect('register')

        # Create the User object
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        profile = user.profile  # Access the Profile through the reverse relation
        profile.save()

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request, 'users/register.html')





def login(request):
   if request.method == 'POST':
       username = request.POST['username']
       password = request.POST['password']


       user = authenticate(request, username=username, password=password)
       if user is not None:
           auth_login(request, user)
           profiles = Profile.objects.get(user=user)
           return redirect('search')  # Redirect to a home or dashboard page
       else:
           messages.error(request, 'Invalid username or password')


   return render(request, 'users/login.html')


def home(request):
   if request.user.is_authenticated:
       auth_logout(request)
   return render(request, 'users/home.html')


def search(request):
   """Handle the search functionality."""
   # Get parameters from the request (GET parameters from the form)
   location = request.GET.get('location', 'Atlanta').strip()
   cuisine = request.GET.get('cuisine', '').strip()  # This will be ignored since you're not using it
   radius = int(request.GET.get('radius', '16093'))  # Default radius (10 miles)
   min_rating = request.GET.get('min_rating', '0')  # Default rating


   # Check which filter is selected
   filter_option = request.GET.get('filter_option')
   sort_distance = filter_option == 'distance'
   sort_rating = filter_option == 'rating'

   min_rating = float(min_rating) if min_rating else 0.0

   sort_option = request.GET.get('sort', 'distance')  # Get the sort parameter from the request
   sort_distance = sort_option == 'distance'  # True if "Sort by Distance" is selected
   sort_rating = sort_option == 'rating'

   if request.method == 'GET' and location:
       if request.user.is_authenticated:
           profile = Profile.objects.get(user=request.user)
           favorites = profile.favorites.all()
           # Create a set of favorite restaurant names for quick lookup
           favorite_names = {restaurant.name for restaurant in favorites}

           # Get all restaurants and update their favorite status
           restaurants = Restaurant.objects.all()
           for restaurant in restaurants:
               restaurant.favorite = restaurant.name in favorite_names
               restaurant.save()
       else:
           restaurants = Restaurant.objects.all()
           for restaurant in restaurants:
               restaurant.favorite = False
       restaurantDetails = []
       results, reviews_list = RestaurantFinder().search(
           location=location,
           name=cuisine,
           radius=radius,
           min_rating=min_rating,
           sort_distance=sort_distance,
           sort_rating=sort_rating
       )
       review_list = reviews_list
       restaurantList = results.split('\n')
       for restaurant in restaurantList:
           details = restaurant.split('\t')
           restaurantDetails.append(details)

       restaurants = []
       for i, details in enumerate(restaurantDetails):
           distance = float(details[3].split()[0])
           restaurant, created = Restaurant.objects.get_or_create(
               name=details[0],
               defaults={
                   'name': details[0],
                   'rating': details[1],
                   'location': details[2],
                   'distance': distance,
                   'types': details[4],
                   'phone': details[5],
                   'website': details[6],
                   'favorite': False
               })
           lat, lang = GooglePlacesAPI().get_lat_and_long(details[2])
           restaurants.append({
               'name': details[0],
               'lat': lat,  # Example: replace with actual latitude data
               'lng': lang,  # Example: replace with actual longitude data
               'rating': details[1]    # Adding rating to display in marker info window
           })
           restaurants_json = json.dumps(restaurants)
           details.append(restaurant.favorite)
           details.append(review_list[i] if i < len(restaurantDetails) else "No reviews available.")
           restaurant.reviews = details[8]
           restaurant.save()

       request.session['restaurantDetails'] = restaurantDetails
   else:
       restaurantDetails = request.session.get('restaurantDetails', [])

   # Debugging output
   for details in restaurantDetails:
       print(details[0], details[7])
   #print("Results to be rendered:", results)


   # Render the results in the template
   return render(request, 'restaurant_search.html',
                 {'results': restaurantDetails, 'location': location, 'restaurants_json': restaurants_json})


def profile(request):
    if request.user.is_authenticated:
        # Get the profile of the logged-in user
        profile = Profile.objects.get(user=request.user)
        return render(request, 'users/profile.html', {'profile': profile})
    else:
        # Handle the case where the user is not logged in
        return redirect('login')  # Redirect to login page


def toggle_favorite(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            restaurantDetails = request.session.get('restaurantDetails', [])
            print(request.POST)
            print(len(restaurantDetails))
            restaurant_id = int(request.POST.get('id'))
            if 0 <= restaurant_id < len(restaurantDetails):
                restaurant_name = restaurantDetails[restaurant_id][0]
                print("NAMEEE: " + restaurant_name)
                try:
                    restaurant = Restaurant.objects.get(name=restaurant_name)
                    restaurant.favorite = not restaurant.favorite  # Toggle the favorite status
                    restaurant.save()

                    # Update the session data to reflect the new favorite status
                    restaurantDetails[restaurant_id][7] = restaurant.favorite

                    if restaurant.favorite:
                        profile.favorites.add(restaurant)
                    else:
                        profile.favorites.remove(restaurant)

                    profile.save()

                    # Update session with new restaurantDetails
                    request.session['restaurantDetails'] = restaurantDetails
                except Restaurant.DoesNotExist:
                    print(f"Restaurant '{restaurant_name}' not found.")
        else:
            return redirect('login')

    return redirect('search')

def write_review(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            review_id = int(request.POST.get('id'))
        else:
            return redirect('login')
    return render(request, 'users/review.html', {'review_id': review_id})

def toggle_fav_profile(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            id = request.POST.get('id')
            favRestaurants = profile.favorites.all()
            for restaurant in favRestaurants:
                if restaurant.name == id:
                    restaurant.favorite = not restaurant.favorite
                    restaurant.save()
                    profile.favorites.remove(restaurant)
                    profile.save()
    return redirect('profile')

def custom_logout(request):
    auth_logout(request)
    return redirect('home')

def review(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            restaurantDetails = request.session.get('restaurantDetails', [])
            review_id = int(request.POST.get('review_id'))
            review = request.POST.get('review')
            rating = request.POST.get('rating')
            print(f"Review: {review}, Rating: {rating}")
            reviewOne = Review.objects.create(
                # Assuming 'restaurant' is a ForeignKey to Restaurant
                review=review,  # Text of the review
                rating=rating  # Rating provided
            )
            print(f"Rating: {reviewOne.rating}, Review: {reviewOne.review}, ID: {review_id}")
            if 0 <= review_id < len(restaurantDetails):
                restaurant_name = restaurantDetails[review_id][0]
                try:
                    restaurant = Restaurant.objects.get(name=restaurant_name)
                    reviewOne.restaurant = restaurant
                    reviewOne.save()
                    profile.reviews.add(reviewOne)
                    profile.save()

                except Restaurant.DoesNotExist:
                    print(f"Restaurant '{restaurant_name}' not found.")
                return render(request, 'users/profile.html', {'profile': profile})
        else:
            return redirect('login')
    return render(request, 'users/profile.html')

def delete_review(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            id = int(request.POST.get('id'))
            reviews = profile.reviews.all()
            review = reviews[id]
            profile.reviews.remove(review)
            profile.save()
            review.delete()
            return redirect('profile')
        else:
            return redirect('login')
