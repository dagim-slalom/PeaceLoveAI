import boto3

# Create a DynamoDB client
dynamodb = boto3.client("dynamodb")

# Define the table names
player_table_name = "Player"
reaction_table_name = "ArtWorkReaction"


def calculate_average_round_reaction(session_id):
    # Define the query parameters for the Game table
    game_query_params = {
        "TableName": player_table_name,
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
    # As of now, sessionId is not a secondary index in the ArtWorkReaction table so this may need to be updated

    # Define the query parameters for the ArtWorkReaction table
    reaction_query_params = {
        "TableName": reaction_table_name,
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
    max_session_reaction = num_unique_player_card_ids * num_players * 5
    average_session_reaction = (num_reactions_per_session / max_session_reaction) * 5


    return {
        average_feeling_before,
        average_feeling_after,
        average_session_reaction
    }


# Test:
# session_id = ""
# result = calculate_average_round_reaction()
# print("Average Round Reactions:", result)
