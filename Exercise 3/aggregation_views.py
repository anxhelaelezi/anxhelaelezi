import pymongo
from bson import ObjectId
def create_aggregation_views(db):
    # Drop existing views if they exist
    aggregations = [
        'average_score_per_genre',
        'total_anime_per_studio',
        'top_10_highest_rated_anime',
        'total_episodes_per_studio',
        'top_10_most_popular_anime',
        'count_anime_by_type'
    ]
    
    for view in aggregations:
        try:
            db.command({'drop': view})
            print(f"Dropped existing view '{view}'")
        except pymongo.errors.OperationFailure:
            print(f"View '{view}' does not exist. Creating a new one.")

    # 1. Average score per genre with a filter for scores above 9
    db.command({
        'create': 'average_score_per_genre',
        'viewOn': 'anime',
        'pipeline': [
            {'$match': {'Score': {'$gt': 9}}},  # Filter for scores greater than 9
             {'$unwind': '$Genres'},
            {'$group': {
                '_id': {"$toString": "$Genres"} ,
                #'_id': '$Genres',  # Group by genre
                'averageScore': {'$avg': '$Score'},  # Calculate average score
                'totalAnime': {'$sum': 1},  # Count total anime
                'maxScore': {'$max': '$Score'},  # Maximum score in the group
                'genres': { '$push': { "$toString": "$Genres" } }
            }},
            {'$sort': {'averageScore': -1}}  # Sort by average score in descending order
        ]
    })
    print("Created 'average_score_per_genre' aggregation view.")
    print(f"Number of records: {db['average_score_per_genre'].count_documents({})}")
    print(list(db['average_score_per_genre'].find()))

    # 2. Total anime per studio with a filter for studios with greater than 60 anime
    db.command({
        'create': 'total_anime_per_studio',
        'viewOn': 'anime',
        'pipeline': [
            {'$match': {'Studios': {'$exists': True}}},  # Ensure Studios field exists
            {'$unwind': '$Studios'},
            {'$group': {
                '_id': '$Studios',  # Group by studio
                'totalAnime': {'$sum': 1},  # Count total anime per studio
                'Studios': { '$push': { "$toString": "$Studios" }}
            }},
            {'$match': {'totalAnime': {'$gt': 60}}},  # Filter for studios with more than 60 anime
            {'$sort': {'totalAnime': -1}}  # Sort by total anime in descending order
        ]
    })
    print("Created 'total_anime_per_studio' aggregation view.")
    print(f"Number of records: {db['total_anime_per_studio'].count_documents({})}")

    # 3. Top 10 highest-rated anime with a filter for scores above 9.0
    db.command({
        'create': 'top_10_highest_rated_anime',
        'viewOn': 'anime',
        'pipeline': [
            {'$match': {'Score': {'$gt': 9.0}}},  # Filter for Score > 9.0
            {'$sort': {'Score': -1}},  # Sort by score in descending order
            {'$limit': 10}  # Limit to top 10
        ]
    })
    print("Created 'top_10_highest_rated_anime' aggregation view.")
    print(f"Number of records: {db['top_10_highest_rated_anime'].count_documents({})}")

    # 4. Total episodes per studio with a filter for studios with less than 5 episodes
    db.command({
        'create': 'total_episodes_per_studio',
        'viewOn': 'anime',
        'pipeline': [
            {'$group': {
                '_id': '$Studios',  # Group by studio
                'totalEpisodes': {'$sum': '$Episodes'},  # Sum of episodes per studio
                'Studios': { '$push': { "$toString": "$Studios" }}

            }},
            {'$match': {'totalEpisodes': {'$lt': 5, '$gt': 0}}},  # Filter for studios with less than 5 episodes
            {'$sort': {'totalEpisodes': -1}}  # Sort by total episodes in descending order
        ]
    })
    print("Created 'total_episodes_per_studio' aggregation view.")
    print(f"Number of records: {db['total_episodes_per_studio'].count_documents({})}")

    # 5. Top 10 most popular anime with a filter for popularity above 200
    db.command({
        'create': 'top_10_most_popular_anime',
        'viewOn': 'anime',
        'pipeline': [
            {'$match': {'Popularity': {'$gt': 200}}},  # Filter for Popularity > 200
            {'$sort': {'Popularity': -1}},  # Sort by popularity in descending order
            {'$limit': 10}  # Limit to top 10
        ]
    })
    print("Created 'top_10_most_popular_anime' aggregation view.")
    print(f"Number of records: {db['top_10_most_popular_anime'].count_documents({})}")

   
    # 6. Average episodes per genre with a filter for genres with an average of less than 5 episodes
    db.command({
        'create': 'count_anime_by_type',
        'viewOn': 'anime',
        'pipeline': [
            {'$unwind': '$Type'},  # Unwind the Type field
            {
                '$group': {
                    '_id': '$Type',  # Group by Type
                    'animeCount': {'$sum': 1}  # Count the number of anime
                }
            },
            {
                '$project': {
                    'Type': '$_id',  # Include the type for output
                    'animeCount': 1,  # Include the count
                    '_id': 0  # Exclude the default _id
                }
            },
            {
                '$match': {
                    'animeCount': {'$gt': 0}  # Filter for types that have anime
                }
            },
            {
                '$sort': {
                    'animeCount': -1  # Sort by anime count in descending order
                }
            }
        ]
    })

    print("Created 'count_anime_by_type' aggregation view.")
    print(f"Number of records: {db['count_anime_by_type'].count_documents({})}")
    print(list(db['count_anime_by_type'].find()))