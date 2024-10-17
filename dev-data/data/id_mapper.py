import json
from uuid import uuid4

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def generate_bigint():
    return abs(hash(str(uuid4())))

def map_ids(users, tours, reviews):
    # Create a mapping of old user IDs to new BigInt IDs
    user_id_map = {user['id']: generate_bigint() for user in users}
    
    # Create a mapping of old tour IDs to new BigInt IDs
    tour_id_map = {tour['id']: generate_bigint() for tour in tours}
    
    # Update user IDs
    for user in users:
        user['id'] = user_id_map[user['id']]
    
    # Update tour IDs and guide IDs
    for tour in tours:
        tour['id'] = tour_id_map[tour['id']]
        tour['guides'] = [user_id_map.get(guide_id, guide_id) for guide_id in tour['guides']]
    
    # Update review IDs, user IDs, and tour IDs
    for review in reviews:
        review['id'] = generate_bigint()
        review['user'] = user_id_map.get(review['user'], review['user'])
        review['tour'] = tour_id_map.get(review['tour'], review['tour'])
    
    return users, tours, reviews

def main():
    # Load data
    users = load_json('dev-data/data/users.json')
    tours = load_json('dev-data/data/tours.json')
    reviews = load_json('dev-data/data/reviews.json')
    
    # Map IDs
    updated_users, updated_tours, updated_reviews = map_ids(users, tours, reviews)
    
    # Save updated data
    save_json(updated_users, 'dev-data/data/mapped_users.json')
    save_json(updated_tours, 'dev-data/data/mapped_tours.json')
    save_json(updated_reviews, 'dev-data/data/mapped_reviews.json')
    
    print("ID mapping completed. Mapped files saved as 'mapped_users.json', 'mapped_tours.json', and 'mapped_reviews.json'.")

if __name__ == "__main__":
    main()