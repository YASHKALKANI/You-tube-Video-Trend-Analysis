import streamlit as st
import pandas as pd
from googleapiclient import discovery
build = discovery.build
from textblob import TextBlob
import isodate
import plotly.express as px
from dotenv import load_dotenv
import os

# --- Load API Key from .env ---
load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🎥 YouTube Video Trend Analyzer", layout="wide")
st.title("📊 YouTube Video Trend Analyzer")
st.write(
    "Analyze trending YouTube videos by category, language, and duration. "
    "Videos ≤5 minutes are considered Shorts, others as Full Videos."
)

# --- Sidebar ---
st.sidebar.header("📈 Chart Options")
chart_option = st.sidebar.radio(
    "Select Chart to Display:",
    [
        "🏆 Top 5 Videos by Views",
        "👍 Likes vs Views Scatter",
        "💬 Sentiment Distribution"
    ]
)

# --- API Validation ---
if not api_key:
    st.error("⚠️ API key not found! Please add it in your .env file as 'YOUTUBE_API_KEY=YOUR_API_KEY'.")
else:
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        # --- Language Selection ---
        language = st.selectbox("🌐 Select Language:", ["English", "Hindi", "Gujarati"])

        # --- Video Type Selection ---
        video_type = st.radio("🎞 Select Video Type to Display:", ["Short Videos", "Full Videos"])

        # --- Category and Subcategory Selection ---
        categories = {
            "Entertainment": ["Comedy", "Funny Skits", "Pranks", "Challenges", "Vlogs", "Reaction", "Parodies"],
            "Educational": ["Motivational", "How-To", "Study Tips", "Science", "Language Learning", "Book Summaries"],
            "Tech": ["Product Reviews", "Unboxing", "Tech News", "AI Tools", "App Tutorials", "Comparison"],
            "Analysis": ["Movie Analysis", "Sports Analysis", "News Commentary", "Finance Case Studies"],
            "Emotional": ["Inspirational Stories", "Social Awareness", "Life Journey", "Mental Health"],
            "Gaming": ["Gameplay", "Funny Gaming", "Live Streaming", "Game Reviews"],
            "Business": ["Finance Education", "Online Earning", "Startup Stories", "Automation Tools"],
            "Music": ["Covers", "Dance", "Singing", "Art", "Calligraphy"],
            "Travel & Food": ["Travel Vlogs", "Street Food", "Hotel Reviews", "Budget Travel"],
        }

        main_category = st.selectbox("🎯 Select Main Category:", list(categories.keys()))
        sub_category = st.selectbox("📌 Select Sub Category:", categories[main_category])

        if st.button("🔍 Analyze Trending Videos"):
            st.info("Fetching trending videos... please wait ⏳")

            search_query = f"{language} {sub_category}"

            request = youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                maxResults=30,
                videoDuration="any"
            )
            response = request.execute()

            video_data = []

            for item in response["items"]:
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                title = snippet["title"]
                channel = snippet["channelTitle"]
                publish_date = snippet.get("publishedAt", "Unknown")
                channel_id = snippet["channelId"]

                # --- Get Video Details ---
                stats_request = youtube.videos().list(
                    part="contentDetails,statistics",
                    id=video_id
                )
                stats_response = stats_request.execute()
                video_info = stats_response["items"][0]

                duration = video_info["contentDetails"].get("duration", "N/A")
                try:
                    duration_seconds = isodate.parse_duration(duration).total_seconds()
                    if duration_seconds < 60:
                        duration_readable = f"{int(duration_seconds)}s"
                    elif duration_seconds < 3600:
                        mins = int(duration_seconds // 60)
                        secs = int(duration_seconds % 60)
                        duration_readable = f"{mins}m {secs}s"
                    else:
                        hrs = int(duration_seconds // 3600)
                        mins = int((duration_seconds % 3600) // 60)
                        duration_readable = f"{hrs}h {mins}m"

                    video_type_class = "Short Video" if duration_seconds <= 300 else "Full Video"
                except:
                    duration_readable = "Unknown"
                    video_type_class = "Unknown"

                stats = video_info["statistics"]
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                comments = int(stats.get("commentCount", 0))

                # --- Channel Subscribers ---
                channel_request = youtube.channels().list(
                    part="statistics",
                    id=channel_id
                )
                channel_response = channel_request.execute()
                subscribers = int(channel_response["items"][0]["statistics"].get("subscriberCount", 0))

                sentiment = TextBlob(title).sentiment.polarity
                sentiment_label = (
                    "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                )

                if (video_type_class == "Short Video" and video_type == "Short Videos") or \
                   (video_type_class == "Full Video" and video_type == "Full Videos"):

                    video_data.append({
                        "Title": title,
                        "Channel": channel,
                        "Subscribers": subscribers,
                        "Views": views,
                        "Likes": likes,
                        "Comments": comments,
                        "Duration": duration_readable,
                        "Published Date": publish_date[:10],
                        "Video Type": video_type_class,
                        "Sentiment": sentiment_label,
                        "Video Link": f"https://www.youtube.com/watch?v={video_id}"
                    })

            df = pd.DataFrame(video_data)
            st.success(f"✅ Found {len(df)} trending {language} {video_type.lower()} in {sub_category} category!")

            if not df.empty:
                # --- Data Table ---
                st.dataframe(df)

                # --- Summary Stats ---
                col1, col2, col3 = st.columns(3)
                col1.metric("📺 Total Views", f"{df['Views'].sum():,}")
                col2.metric("👍 Total Likes", f"{df['Likes'].sum():,}")
                col3.metric("💬 Total Comments", f"{df['Comments'].sum():,}")

                # --- Chart Selection from Sidebar ---
                if chart_option == "🏆 Top 5 Videos by Views":
                    top_views = df.nlargest(5, 'Views')
                    fig = px.bar(
                        top_views,
                        x='Title',
                        y='Views',
                        color='Video Type',
                        title="🏆 Top 5 Videos by Views",
                        text='Views'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_option == "👍 Likes vs Views Scatter":
                    fig = px.scatter(
                        df,
                        x='Views',
                        y='Likes',
                        color='Video Type',
                        hover_data=['Title', 'Channel'],
                        title="👍 Likes vs 📺 Views"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_option == "💬 Sentiment Distribution":
                    sentiment_count = df['Sentiment'].value_counts().reset_index()
                    sentiment_count.columns = ['Sentiment', 'Count']
                    fig = px.pie(
                        sentiment_count,
                        names='Sentiment',
                        values='Count',
                        title="💬 Sentiment Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # --- Download CSV ---
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Results as CSV",
                    data=csv,
                    file_name=f"youtube_{language.lower()}_{video_type.lower().replace(' ','_')}_{sub_category.lower().replace(' ','_')}_analysis.csv",
                    mime='text/csv'
                )
            else:
                st.info("No videos found for the selected filters.")

    except Exception as e:
        st.error(f"An error occurred with the API key or request: {e}")
