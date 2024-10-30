import requests
from math import radians, sin, cos, sqrt, atan2

class GooglePlacesAPI:
    GOOGLE_PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    PLACE_DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

    def __init__(self):
        self.API_KEY = "YOUR API HERE"

    def get_lat_and_long(self, address):
        """Fetch latitude and longitude of the given address using the Geocoding API."""
        params = {
            'address': address,
            'key': self.API_KEY
        }
        response = requests.get(self.GEOCODING_URL, params=params)
        results = response.json()

        if results['status'] == 'OK':
            location = results['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return latitude, longitude
        else:
            print(f"Error: {results['status']}")
            return None, None

    def get_place_details(self, place_id):
        """Fetch place details like phone number and website using the Place Details API."""
        params = {
            'place_id': place_id,
            'key': self.API_KEY
        }
        response = requests.get(self.PLACE_DETAILS_URL, params=params)
        details = response.json()
        if details['status'] == 'OK':
            result = details['result']
            contact_info = {
                'phone_number': result.get('formatted_phone_number', 'N/A'),
                'website': result.get('website', 'N/A'),
                'reviews': result.get('reviews', [])
            }
            return contact_info
        return {'phone_number': 'N/A', 'website': 'N/A', 'reviews': '[]'}

    def get_restaurants(self, location="33.7488, -84.3877", name="Any", radius=10000, min_rating=0, sort_distance=False,
                        sort_rating=False):
        """Fetch nearby restaurants and filter/sort based on rating and distance."""
        if isinstance(location, str):
            location_lat, location_lng = map(float, location.split(", "))
        else:
            location_lat, location_lng = location

        params = {
            'key': self.API_KEY,
            'location': f"{location_lat},{location_lng}",  # User's latitude and longitude
            'radius': radius,
            'type': "restaurant",
        }
        if name:
            params['name'] = name
        else:
            name = "Any"

        response = requests.get(self.GOOGLE_PLACES_URL, params=params)
        results = response.json()

        if 'results' not in results:
            return "No results found."

        places = results["results"]
        filtered_places = []
        reviews_list = []

        for place in places:
            rating = place.get('rating', None)
            place_lat = place['geometry']['location']['lat']
            place_lng = place['geometry']['location']['lng']
            place_id = place['place_id']


            if rating is not None and rating >= min_rating:
                distance = self.calculate_distance(location_lat, location_lng, place_lat,
                                                   place_lng)  # Calculate distance
                contact_info = self.get_place_details(place_id)
                reviews = self.format_reviews(contact_info['reviews'])
                filtered_places.append({
                    'name': place.get('name', 'N/A'),
                    'rating': float(rating),
                    'location': place.get('vicinity', 'N/A'),
                    'distance': distance,
                    'phone_number': contact_info['phone_number'],
                    'website': contact_info['website'],
                    'reviews': reviews
                })

                reviews_list.append(reviews)

        if not filtered_places:
            return "No places found with the given criteria."

        if sort_rating:
            filtered_places.sort(key=lambda x: x['rating'], reverse=True)

        if sort_distance:
            filtered_places.sort(key=lambda x: x['distance'])

        result = "\n".join([
            f"{place['name']}\t{place['rating']}\t{place['location']}\t"
            f"{place['distance']:.2f} miles\t{name}\t"
            f"{place['phone_number']}\t{place['website']}"
            for place in filtered_places])

        reviews = "\n".join([
            f"{place['name']} - Top Reviews:\n{place['reviews']}"
            for place in filtered_places
        ])

        return result, reviews_list

    def format_reviews(self, reviews):
        """Format the top reviews into a readable string, ensuring 'Anonymous' when author name is missing."""
        if not reviews:
            return "No reviews available."
        formatted_reviews = "\n".join([
            f"- {review.get('author_name', 'Anonymous')}: {review.get('text', 'No review text available')}"
            for review in reviews[:3]  # Show up to 3 reviews
        ])
        return formatted_reviews

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the distance between two points using the Haversine formula, return distance in miles."""
        R = 6371.0  # Radius of the Earth in km

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance_km = R * c
        distance_miles = distance_km * 0.621371  # Convert kilometers to miles
        return distance_miles


class RestaurantFinder:
    def __init__(self):
        self.google_places_api = GooglePlacesAPI()

    def search(self, location=None, name="Any", radius=10000, min_rating=0, sort_distance=False, sort_rating=False):
        """Search for restaurants using the GooglePlacesAPI."""
        if location:
            location_coords = self.google_places_api.get_lat_and_long(location)
        else:
            location_coords = (33.7488, -84.3877)  # Default to Atlanta if no location is provided

        return self.google_places_api.get_restaurants(location=location_coords, name=name, radius=radius,
                                                      min_rating=min_rating, sort_distance=sort_distance,
                                                      sort_rating=sort_rating)


 #Example usage
#restaurant_finder = RestaurantFinder()
#results, reviews_list = restaurant_finder.search(location="Georgia Tech", name="The Varsity", radius=1000, min_rating=0, sort_distance=True, sort_rating=False)
#print("Restaurants:\n", results)
#print("\nReviews:")
#for i, review in enumerate(reviews_list):
  #  print(f"Reviews:\n{review}\n")
