import streamlit as st
import json
import os
import feedparser

st.set_page_config(
    page_title="My RSS Reader", 
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("📰 B's RSS Reader")
FEEDS_FILE = "feeds.json"
SAVED_FILE = "saved.json"

#heloer
def load_feeds():
    if os.path.exists(FEEDS_FILE):
        with open(FEEDS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_feeds(feeds):
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds, f, indent=4)

def load_saved():
    if os.path.exists(SAVED_FILE):
        with open(SAVED_FILE, "r") as f:
            return json.load(f)
    return []

def save_article(entry):
    saved = load_saved()
    if not any(e['link'] == entry.link for e in saved):
        saved.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "Unknown"),
            "summary": entry.get("summary", "")
        })
        with open(SAVED_FILE, "w") as f:
            json.dump(saved, f, indent=4)
        st.toast("0.0 Article saved!")

#sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Configure your RSS feeds here.")

    feed_url = st.text_input("RSS Feed URL", placeholder="Enter RSS feed URL...", key="feed_url_input")
    feed_name = st.text_input("Feed Name", placeholder="Enter name for the feed...", key="feed_name_input")

    if st.button("Add Feed", key="add_feed_btn"):
        if feed_url and feed_name:
            feeds = load_feeds()
            feeds[feed_name] = feed_url
            save_feeds(feeds)
            st.success(f"✅ Added feed: {feed_name}")
            st.rerun()
        else:
            st.error("!!! Please enter both feed name and URL.")

    if st.button("Refresh Feeds", key="refresh_btn"):
        st.rerun()

#load feed
feeds = load_feeds()

if not feeds:
    st.warning("No RSS feeds found. Add one in the sidebar.")
    st.stop()

selected = st.sidebar.selectbox("/ Select a Feed", list(feeds.keys()), key="feed_select")
url = feeds[selected]
st.write(f"🔗 Selected Feed URL: {feeds[selected]}")

#display feeds
feed = feedparser.parse(feeds[selected])

st.subheader(f"🗞️ Latest Articles from {selected}")

if not feed.entries or len(feed.entries) == 0:
    st.warning("⚠️ No recent entries found. Trying to fetch last 5 available articles...")
    fallback_feed = feedparser.parse(url)
    entries = feedparser.parse(url).entries[:5]
else:
    for entry in feed.entries[:10]:
        with st.expander(entry.title):
            st.markdown(f"**Published:** {entry.get('published', 'Unknown')}")
            st.markdown(entry.get("summary", "No summary available"), unsafe_allow_html=True)
            st.markdown(f"[--> Read Full Article]({entry.link})", unsafe_allow_html=True)
            if st.button("/ Save", key=f"save_{entry.link}"):
                save_article(entry)


# Bookmarked Articles

st.divider()
st.subheader("[]Bookmarked Articles")

saved = load_saved()

if not saved:
    st.info("No articles saved yet.")
else:
    for item in saved[::-1]:  # Show newest first
        with st.expander(item['title']):
            st.markdown(f"**Published:** {item.get('published', 'Unknown')}")
            st.markdown(item.get("summary", "No summary available"), unsafe_allow_html=True)
            st.markdown(f"[🔗 Read Full Article]({item['link']})", unsafe_allow_html=True)
