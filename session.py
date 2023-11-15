import json
import boto3

def lambda_handler(event, context):

    # Create a DynamoDB client
    dynamodb = boto3.client("dynamodb")
    
    # Define the table names
    index_name = "bySessionId"
    session_id = event["sessionId"]
    environment = event["environment"]
    player_table_name = f"Player-{environment}"
    reaction_table_name = f"ArtworkReaction-{environment}"

    # Define the query parameters for the Game table
    game_query_params = {
        "TableName": player_table_name,
        "IndexName": index_name,
        "KeyConditionExpression": "sessionId = :id",
        "ExpressionAttributeValues": {":id": {"S": session_id}},
        "ProjectionExpression": "feelingBefore, feelingAfter",
    }

    # Perform the query on the Game table
    game_response = dynamodb.query(**game_query_params)

    # Extract items from the Game table response
    player_items = game_response.get("Items", [])
    

    # Extract 'feelingBefore' and 'feelingAfter' values into separate lists
    feeling_before_list = [
        float(item.get("feelingBefore", {}).get("N", 0)) for item in player_items
    ]
    feeling_after_list = [
        float(item.get("feelingAfter", {}).get("N", 0)) for item in player_items
    ]
    

    # Calculate the average feelingBefore and feelingAfter
    average_feeling_before = (
        sum(feeling_before_list) / len(feeling_before_list)
        if feeling_before_list
        else 0
    )
    average_feeling_after = (
        sum(feeling_after_list) / len(feeling_after_list) if feeling_after_list else 0
    )
    num_players = len(feeling_before_list)
    
    # Query the ArtWorkReaction table for this sessionId and count the number of reactions and unique playerCardIds

    # Define the query parameters for the ArtWorkReaction table
    reaction_query_params = {
        "TableName": reaction_table_name,
        "IndexName": index_name,
        "KeyConditionExpression": "sessionId = :id",
        "ExpressionAttributeValues": {":id": {"S": session_id}},
        "ProjectionExpression": "playerCardId, reaction",
    }

    # Perform the query on the ArtWorkReaction table
    reaction_response = dynamodb.query(**reaction_query_params)

    # Extract 'playerCardId' values into a list
    player_card_ids_in_game = [
        item.get("playerCardId", {}).get("S", "")
        for item in reaction_response.get("Items", [])
    ]

    # Count the number of unique playerCardIds and store in the dictionary
    num_unique_player_card_ids = len(set(player_card_ids_in_game))
    num_reactions_per_session = len(reaction_response.get("Items", []))
    
    ## This currently leads to a very low average_session_reaction so may need to scale this differently
    max_session_reaction = num_unique_player_card_ids * num_players * 5
    average_session_reaction = (num_reactions_per_session / max_session_reaction) * 5
    
    return {
        "pre_game_average": average_feeling_before, 
        "post_game_average": average_feeling_after,
        "session_average": average_session_reaction,
        "sessionId": session_id
    }



# Test Event:
# {
#   "sessionId": "2789",
#   "environment": "dev"
# }
