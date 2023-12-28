import reddit_collector
import title_card
import store_ids
from mongo import mongo_client, collection


#try:
#    mongo_client.admin.command('ping')
#    print("Pinged your deployment. You successfully connected to MongoDB!")
#except Exception as e:
#    print(e)
reddit_collector.scrape_posts()

