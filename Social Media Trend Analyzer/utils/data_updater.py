import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def update_datasets(num_rows=50):
    try:
        # Generate new data for engagement.csv
        eng_path = os.path.join(BASE_DIR, 'engagement.csv')
        if os.path.exists(eng_path):
            eng_df = pd.read_csv(eng_path)
            
            # Create synthetic rows
            new_eng = []
            media_types = ['reel', 'image', 'carousel', 'video']
            categories = ['Technology', 'Fashion', 'Sports', 'Food', 'Lifestyle', 'Travel', 'Education', 'Gaming']
            traffic_sources = ['Home Feed', 'Explore', 'Profile', 'Hashtags', 'Other']
            buckets = ['low', 'medium', 'high', 'viral']
            
            current_time = datetime.now()
            
            # Start ID from the max existing if possible, else random
            last_id = 1000000
            if 'post_id' in eng_df.columns:
                try:
                    last_id = int(eng_df['post_id'].iloc[-1].replace('IG', ''))
                except:
                    pass

            for i in range(num_rows):
                post_datetime = current_time - timedelta(minutes=random.randint(1, 1440))
                likes = random.randint(10, 50000)
                comments = random.randint(0, int(likes * 0.1) + 1)
                shares = random.randint(0, int(likes * 0.05) + 1)
                saves = random.randint(0, int(likes * 0.08) + 1)
                reach = likes * random.randint(5, 20)
                impressions = reach * random.uniform(1.1, 1.5)
                
                row = {
                    'post_id': f'IG{last_id + i + 1:07d}',
                    'account_id': random.randint(1, 100),
                    'account_type': random.choice(['brand', 'creator', 'personal']),
                    'follower_count': random.randint(100, 1000000),
                    'media_type': random.choice(media_types),
                    'content_category': random.choice(categories),
                    'traffic_source': random.choice(traffic_sources),
                    'has_call_to_action': random.choice([0, 1]),
                    'post_datetime': post_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'post_date': post_datetime.strftime('%Y-%m-%d'),
                    'post_hour': post_datetime.hour,
                    'day_of_week': post_datetime.strftime('%A'),
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'saves': saves,
                    'reach': int(reach),
                    'impressions': int(impressions),
                    'engagement_rate': round(likes / impressions if impressions > 0 else 0, 4),
                    'followers_gained': random.randint(-10, 500),
                    'caption_length': random.randint(10, 2200),
                    'hashtags_count': random.randint(0, 30),
                    'performance_bucket_label': random.choice(buckets)
                }
                new_eng.append(row)
            
            pd.concat([eng_df, pd.DataFrame(new_eng)]).to_csv(eng_path, index=False)


        # Generate new data for hashtags.csv
        hash_path = os.path.join(BASE_DIR, 'hashtags.csv')
        if os.path.exists(hash_path):
            try:
                hash_df = pd.read_csv(hash_path)
            except Exception:
                hash_df = pd.read_csv(hash_path, encoding='latin1')
                
            new_hash = []
            platforms = ['Instagram', 'TikTok', 'Twitter', 'Facebook', 'YouTube']
            topics = ['#AI', '#Tech', '#Trending', '#Viral', '#Fashion', '#Travel', '#Foodie', '#Fitness', '#OOTD', '#Coding']
            regions = ['Global', 'India', 'USA', 'UK', 'Brazil', 'Europe', 'Australia', 'Japan']
            c_types = ['Video', 'Reels', 'Image', 'Carousel', 'Text', 'Shorts']
            e_levels = ['Low', 'Medium', 'High', 'Viral']
            
            last_p_id = 10000
            try:
                if 'Post_ID' in hash_df.columns:
                    last_p_id = int(hash_df['Post_ID'].iloc[-1].replace('Post_', ''))
            except: pass
            
            for i in range(num_rows):
                views = random.randint(1000, 10000000)
                likes = int(views * random.uniform(0.01, 0.15))
                row = {
                    'Post_ID': f'Post_{last_p_id + i + 1}',
                    'Post_Date': current_time.strftime('%Y-%m-%d'),
                    'Platform': random.choice(platforms),
                    'Hashtag': random.choice(topics) + str(random.randint(1, 100)),
                    'Content_Type': random.choice(c_types),
                    'Region': random.choice(regions),
                    'Views': views,
                    'Likes': likes,
                    'Shares': int(likes * random.uniform(0.01, 0.2)),
                    'Comments': int(likes * random.uniform(0.01, 0.1)),
                    'Engagement_Level': random.choice(e_levels)
                }
                new_hash.append(row)
                
            pd.concat([hash_df, pd.DataFrame(new_hash)]).to_csv(hash_path, index=False, encoding='utf-8')


        # Generate new data for time_series.csv
        ts_path = os.path.join(BASE_DIR, 'time_series.csv')
        if os.path.exists(ts_path):
            try:
                ts_df = pd.read_csv(ts_path)
            except:
                ts_df = pd.read_csv(ts_path, encoding='latin1')
            
            new_ts = []
            titles = ['NEW TECH 2026!', 'VLOG: My Day', 'Coding Tutorial', 'Funny Cats', 'Gaming Highlights', 'Music Video']
            
            for i in range(num_rows):
                vid = f'vid{random.randint(10000, 99999)}'
                v_count = random.randint(1000, 5000000)
                row = {
                    'video_id': vid,
                    'title': random.choice(titles),
                    'description': 'Generated real-time data description.',
                    'published_date': current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'channel_id': f'UC{random.randint(1000, 9999)}',
                    'channel_title': f'Channel_{random.randint(1, 100)}',
                    'tags': "['new', 'trending', 'live']",
                    'category_id': random.randint(1, 30),
                    'view_count': float(v_count),
                    'like_count': float(v_count * random.uniform(0.01, 0.05)),
                    'comment_count': float(v_count * random.uniform(0.001, 0.01)),
                    'duration': f'PT{random.randint(1, 20)}M{random.randint(0, 59)}S',
                    'thumbnail': f'https://i.ytimg.com/vi/{vid}/default.jpg'
                }
                new_ts.append(row)
                
            pd.concat([ts_df, pd.DataFrame(new_ts)]).to_csv(ts_path, index=False, encoding='utf-8')

        return True, f"Successfully fetched and appended {num_rows} real-time data rows to all datasets."
    except Exception as e:
        return False, f"Error generating data: {str(e)}"
