import boto3

# Create a DynamoDB client
dynamodb = boto3.client("dynamodb")

# Define the table names
game_table_name = "Game"
reaction_table_name = "ArtWorkReaction"


def calculate_average_round_reaction(session_id):
    # Define the query parameters for the Game table
    game_query_params = {
        "TableName": game_table_name,
        "KeyConditionExpression": "sessionId = :id",
        "ExpressionAttributeValues": {":id": {"S": session_id}},
        "ProjectionExpression": "gameId, feelingBefore, feelingAfter",
    }

    # Perform the query on the Game table
    game_response = dynamodb.query(**game_query_params)

    # Extract items from the Game table response
    game_items = game_response.get("Items", [])

    # Extract 'gameId', 'feelingBefore', 'feelingAfter', and 'playerCardId' values into separate lists
    game_ids = [item.get("gameId", {}).get("S", "") for item in game_items]
    feeling_before_list = [
        float(item.get("feelingBefore", {}).get("N", 0)) for item in game_items
    ]
    feeling_after_list = [
        float(item.get("feelingAfter", {}).get("N", 0)) for item in game_items
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

    # Query the ArtWorkReaction table for each gameId and count the number of reactions and unique playerCardIds
    average_round_reaction = []

    for game_id in game_ids:
        # Define the query parameters for the ArtWorkReaction table
        reaction_query_params = {
            "TableName": reaction_table_name,
            "KeyConditionExpression": "gameId = :id",
            "ExpressionAttributeValues": {":id": {"S": game_id}},
            "ProjectionExpression": "playerCardId, reactionValue",
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
        reactions_per_game = len(reaction_response.get("Items", []))
        max_round_reaction = num_unique_player_card_ids * num_players * 5
        current_round_reaction_average = (reactions_per_game / max_round_reaction) * 5

        # Store the results in a list
        average_round_reaction.append(current_round_reaction_average)

    return {
        average_feeling_before,
        average_feeling_after,
        average_round_reaction
    }


# Test:
# session_id = ""
# result = calculate_average_round_reaction()
# print("Average Round Reactions:", result)
