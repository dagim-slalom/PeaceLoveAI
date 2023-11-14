from openai import OpenAI
client = OpenAI()

def lambda_handler(session_sentiments):
    
    initial_sentiment = session_sentiments["average_feeling_before"]
    final_sentiment = session_sentiments["average_feeling_after"]
    game_sentiment = session_sentiments["average_session_reaction"]

    session_prompt = f"""Based on the sentiment scores of 0-5, generate a heatmap that transitions from one color (representing the initial sentiment)
      to another color (representing the final sentiment).
      The inital sentiment is {initial_sentiment}. Then the sentiment is {game_sentiment}. The final sentiment is {final_sentiment}. 
      You can use multiple colors but start with gray for sad and end up with yellow for happy."""
    response = client.images.generate(
    model="dall-e-3",
    prompt=session_prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    print(image_url)
    return image_url

lambda_handler({"average_feeling_before" : 2.1, "average_feeling_after" : 4.1, "average_session_reaction" : 3.7})