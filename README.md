# YouTube Video Trend Analyzer

Analyze trending YouTube videos by **category, language, and duration** using the YouTube Data API.  
This Streamlit app helps you discover what content is performing well — including **views, likes, subscribers, and sentiment analysis** of video titles.

---

## Features

- Fetch trending YouTube videos by keyword or category  
- Detect **Shorts** (≤5 minutes) vs **Full Videos** automatically  
- View **channel subscribers**, likes, comments, and duration  
- Analyze **positive vs negative sentiment** using TextBlob  
- Interactive charts using Plotly:  
   - Top 5 Videos by Views  
   - Likes vs Views Scatter Plot  
   - Sentiment Distribution Pie Chart  
- Download all results as a **CSV file**  
- Uses `.env` file to protect your YouTube API key 

---

## Tech Stack

- **Python**
- **Streamlit** (frontend dashboard)
- **YouTube Data API v3**
- **TextBlob** (sentiment analysis)
- **Plotly Express** (visualizations)
- **Pandas & isodate**
- **dotenv** (API key management)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YASHKALKANI/You-tube-Video-Trend-Analysis.git
cd You-tube-Video-Trend-Analysis
