import pymongo

def create_views_with_filters(db):
    # Drop existing views if they exist
    views = [
        'high_score_anime',
        'action_anime',
        'long_series',
        'recent_anime',
        'popular_anime',
        'average_score_anime'
    ]
    for view in views:
        try:
            db.command({'drop': view})
            print(f"Dropped existing view '{view}'")
        except pymongo.errors.OperationFailure:
            print(f"View '{view}' does not exist. Creating a new one.")

    # 1. Anime with score > 8
    db.command({
        'create': 'high_score_anime',
        'viewOn': 'anime',
        'pipeline': [{'$match': {'Score': {'$gt': 9}}},
                     {'$sort': {'Score': -1}}  # Rendit sipas Score në mënyrë zbritëse
        ]
    })
    print("Created 'high_score_anime' view.")
    print(f"Number of records in 'high_score_anime': {db['high_score_anime'].count_documents({})}")

    # 2. Anime of a specific genre
    db.command({
        'create': 'action_anime',
        'viewOn': 'anime',
        'pipeline': [
        {
            '$match': {
                'Genres': {
                    '$regex': r'\bAction\b',  # Match exactly "Action" as a whole word
                    '$options': 'i'  # Case-insensitive
                }
            }
        },
        {
            '$sort': {
                'Id_anime': 1  # Rendit sipas Id_anime në mënyrë rritëse (1 për rritëse, -1 për zbritëse)
            }
        }
    ]
})
    print("Created 'action_anime' view.")
    print(f"Number of records in 'action_anime': {db['action_anime'].count_documents({})}")

    # 3. Anime with more than 100 episodes
    db.command({
        'create': 'long_series',
        'viewOn': 'anime',
        'pipeline': [{'$match': {'Episodes': {'$gt': 500}}},
{
            '$sort': {
                'Episodes': -1  # Rendit sipas Episodes në mënyrë zbritëse (zbritës)
            }
        }
    ]
    })
    print("Created 'long_series' view.")
    print(f"Number of records in 'long_series': {db['long_series'].count_documents({})}")

    # 4. Anime from 2020 or later
    db.command({
        'create': 'recent_anime',
        'viewOn': 'anime',
        'pipeline': [
        {
            '$match': {
                # Use a regex to find years greater than or equal to 2020 in the 'Premiered' string
                'Premiered': {
                    '$regex': r'\b(202[3-9]|20[3-9][0-9])\b',  # Matches any year from 2023 onwards
                    '$options': 'i'  # Case-insensitive (optional, in case of case variations)
                }
            }
        },
        {
            '$sort': {
                'Premiered': 1  # Rendit sipas Title në mënyrë rritëse (alfabetike)
            }
        }
    ]
})
    print("Created 'recent_anime' view.")
    print(f"Number of records in 'recent_anime': {db['recent_anime'].count_documents({})}")

    # 5. Popular anime (based on members > 100,000)
    db.command({
        'create': 'popular_anime',
        'viewOn': 'anime',
        'pipeline': [{'$match': {'Popularity': {'$gt': 19000}}},
        {
            '$sort': {
                'Popularity': -1  # Rendit sipas popullaritetit në mënyrë zbritëse
            }
        }
        ]
    })
    print("Created 'popular_anime' view.")
    print(f"Number of records in 'popular_anime': {db['popular_anime'].count_documents({})}")

    # 6. Anime with average score
    # 1. Krijo një pipeline për të gjetur mesataren e Score
    average_score_pipeline = [
        {
            '$group': {
                '_id': None,  # Nuk na nevojitet grupimi
                'averageScore': {'$avg': '$Score'}  # Llogarit mesataren e Score
            }
        }
    ]

    # Merr mesataren e Score
    average_score_result = list(db['anime'].aggregate(average_score_pipeline))
    average_score = average_score_result[0]['averageScore'] if average_score_result else 0

    # 2. Krijo view për anime-t që kanë Score e barabartë me mesataren
    db.command({
    'create': 'average_score_anime',
    'viewOn': 'anime',
    'pipeline': [
        {
            '$match': {
                'Score': {  # Specifikoni fushën "Score"
                    '$gte': average_score - 0.001,  # Gjej anime-t me Score ≥ mesatare - 0.1
                    '$lte': average_score + 0.001   # Gjej anime-t me Score ≤ mesatare + 0.1
                }
            }
        }
        ]
    })
    print("Created 'average_score_anime' view.")
    print(f"Number of records in 'average_score_anime': {db['average_score_anime'].count_documents({})}")
   # Krijo një index për fushën 'name_id'
    db['anime'].create_index([('name_id', 1)])  # 1 për rend rritës, -1 për rend zbritës
    print("Index i krijuar për 'name_id'.")
    # Krijo gjashtë indexe
    db['anime'].create_index([('name_id', 1)])  # Index i thjeshtë për name_id
    db['anime'].create_index([('Score_id', -1)])  # Index për Score në rend zbritës
    db['anime'].create_index([('Popularity_id', -1)])  # Index për Popularity në rend zbritës
    db['anime'].create_index([('Premiered_id', 1)])  # Index për Premiered në rend rritës
    db['anime'].create_index([('Genres_id', 'text')])  # Index tekstual për Genres
    db['anime'].create_index([('Episodes_id', -1)])  # Index për Episodes në rend zbritës
("Gjashtë indexe janë krijuar për fushat 'name_id', 'Score', 'Popularity', 'Premiered', 'Genres' dhe 'Episodes'.")
   
   