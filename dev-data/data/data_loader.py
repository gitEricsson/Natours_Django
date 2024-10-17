import sys
import os
import django
from django.conf import settings
import json
import pytz
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Add the project root to Python's module search path
sys.path.insert(0, project_root)

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Natours_Django.settings')
django.setup()

from tours.models import Tour, Point, Location
from users.models import User
from reviews.models import Review
from appointments.models import Appointment


# Load JSON data from files
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def import_data():
    try:
        tours_data = load_json('dev-data/data/mapped_tours.json')
        users = load_json('dev-data/data/mapped_users.json')
        reviews = load_json('dev-data/data/mapped_reviews.json')

        # Create or get Point instances for start_location and then bulk create tours
        tour_instances = []
        locations_data_map = {}  # Store locations to add after bulk creation
        guides_data_map = {}  # Store guides to add after bulk creation

        # Prepare tour instances and map locations/guides to set later
        for tour_data in tours_data:
            try:
                start_location_data = tour_data.pop('start_location')

                # Convert start dates to timezone-aware datetime objects
                tour_data['start_dates'] = [parse_datetime(date).replace(tzinfo=pytz.UTC) for date in tour_data['start_dates']]

                # Create or get the Point instance for start_location
                start_location, created = Point.objects.get_or_create(
                    description=start_location_data['description'],
                    defaults={
                        'coordinates': start_location_data['coordinates'],
                        'address': start_location_data['address']
                    }
                )
                
                tour_data['start_location'] = start_location

                # Remove guides and locations temporarily to process them after bulk creation
                guides_ids = tour_data.pop('guides', [])
                locations_data = tour_data.pop('locations', [])

                # Create the Tour instance (but don't save yet)
                tour_instance = Tour(**tour_data)
                tour_instances.append(tour_instance)

                # Map guides and locations to process later
                guides_data_map[tour_instance.name] = guides_ids
                locations_data_map[tour_instance.name] = locations_data

            except Exception as e:
                print(f"Error preparing tour {tour_data.get('name', 'Unknown')}: {str(e)}")

        # Bulk create tours
        Tour.objects.bulk_create(tour_instances, ignore_conflicts=True)
        print("Tours bulk created successfully")

        # Bulk create users
        User.objects.bulk_create([User(**user) for user in users], ignore_conflicts=True)
        print("Users bulk created successfully")
        
        # Handle ManyToMany relationships (guides and locations)
        for tour in Tour.objects.all():
            try:
                # Set guides after bulk creation
                guides_ids = guides_data_map.get(tour.name, [])
                if guides_ids:
                    guides = User.objects.filter(id__in=guides_ids)
                    tour.guides.set(guides)
                    print(f"Guides set for tour: {tour.id}")

                # Set locations after bulk creation
                location_instances = []
                locations_data = locations_data_map.get(tour.name, [])
                for location_data in locations_data:
                    location, _ = Location.objects.get_or_create(
                        description=location_data['description'],
                        defaults={
                            'coordinates': location_data['coordinates'],
                            'address': location_data.get('address', ''),
                            'day': location_data['day']
                        }
                    )
                    location_instances.append(location)
                tour.locations.set(location_instances)
                print(f"Locations set for tour: {tour.id}")

            except IntegrityError as ie:
                print(f"IntegrityError for tour {tour.name}: {str(ie)}")
            except Exception as e:
                print(f"Error processing tour {tour.name}: {str(e)}")

        # Create reviews and link them to the correct user and tour
        for review_data in reviews:
            try:
                # Fetch the user and tour instances
                user_instance = User.objects.get(id=review_data.pop('user'))
                tour_instance = Tour.objects.get(id=review_data.pop('tour'))

                # Create the Review instance with user and tour
                review = Review.objects.create(user=user_instance, tour=tour_instance, **review_data)
                print(f"Review created successfully for tour: {tour_instance.name}")

            except User.DoesNotExist:
                print(f"User with ID {review_data['user']} does not exist, skipping review.")
                continue
            except Tour.DoesNotExist:
                print(f"Tour with ID {review_data['tour']} does not exist, skipping review.")
                continue
            except IntegrityError as ie:
                print(f"IntegrityError for review: {str(ie)}")
            except Exception as e:
                print(f"Error creating review: {str(e)}")

        print("Reviews bulk created successfully")

        print("Data successfully loaded!")

    except Exception as e:
        print(f"Error: {e}")


def delete_data():
    try:
        Tour.objects.all().delete()
        User.objects.all().delete()
        Review.objects.all().delete()

        print("Data successfully deleted!")
    except Exception as e:
        print(f"Error: {e}")

def import_appointments():
    try:
        tours = Tour.objects.all()
        appointments = []

        for tour in tours:
            for start_date in tour.start_dates:
                appointments.append(Appointment(tour=tour, date=start_date, participants=0, sold_out=False))

        Appointment.objects.bulk_create(appointments)
        print("Appointments successfully loaded!")
    except Exception as e:
        print(f"Error: {e}")

# Main script logic
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == '--import':
            import_data()
        elif action == '--delete':
            delete_data()
        elif action == '--importDates':
            import_appointments()
        else:
            print("Invalid action. Use --import, --delete, or --importDates")


# # Commands to run 
# python dev-data/data/data_loader.py --import         # To import data
# python dev-data/data/data_loader.py --delete         # To delete data
# python dev-data/data/data_loader.py --importDates    # To import appointments