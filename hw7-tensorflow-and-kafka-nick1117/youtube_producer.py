import socket
from confluent_kafka import Producer, KafkaError
import os
import time 
from googleapiclient.discovery import build
import json

# Kafka settings
BROKER = 'localhost:9092'  # Change this to your Kafka broker address
TOPIC = 'youtube_topic_HW7'  # Replace with your Kafka topic
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cmu-class.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="system-tool-chains-229ab115b494.json"

youtube = build('youtube', 'v3')

def get_video_title(video_id):
    request = youtube.videos().list(
        part='snippet',
        id=video_id,
    )
    response = request.execute()

    if response['items']:
        title = response['items'][0]['snippet']['title']
        return title
    else:
        return None

def get_total_comment_likes(video_id):
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,
        textFormat='plainText'
    )
    response = request.execute()
    total_likes = 0
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        total_likes += comment.get('likeCount', 0)
    return total_likes

# Function to create a Kafka consumer
def create_kafka_producer(broker):
    conf = {
        'bootstrap.servers': broker,
        'client.id': socket.gethostname()

    }
    producer = Producer(conf)
    return producer

if __name__ == "__main__":
    producer = create_kafka_producer(BROKER)

    video_ids = []
    print("Enter five YouTube video IDs")
    for i in range(5):
        video_id = input(f"Enter vidoe ID {i+1}: ").strip()
        video_ids.append(video_id)

    for video_id in video_ids:
        title = get_video_title(video_id)
        if not title:
            print("Video ID {video_id} not found or invalid")
            continue
        total_likes = get_total_comment_likes(video_id)
        #json.dumps required to send two data types
        message = json.dumps({'title': title, 'total_likes': total_likes})
        producer.produce(TOPIC, key=video_id, value=message)
        producer.flush()
        print(f"Sent data for video '{title}' with total comment likes: {total_likes}")
    # signal the consumer to stop
    producer.produce(TOPIC, key='END', value='END')
    producer.flush()