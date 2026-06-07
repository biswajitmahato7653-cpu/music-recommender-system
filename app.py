import streamlit as st
import pandas as pd
import pickle
import requests

# ========================== 
# LOAD DATA
# ==========================
try:
    songs_dict = pickle.load(open('songs_dict.pkl', 'rb'))
    df = pd.DataFrame(songs_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except:
    df = pd.read_csv("chatbot_song_dataset_500plus.csv")

# ==========================
# RECOMMENDATION FUNCTION
# ==========================
def get_album_cover(song_name, artist_name=""):
    try:
        query = f"{song_name} {artist_name}"

        url = "https://itunes.apple.com/search"

        params = {
            "term": query,
            "entity": "song",
            "limit": 1
        }

        response = requests.get(url, params=params)

        data = response.json()

        if data["resultCount"] > 0:
            return data["results"][0]["artworkUrl100"].replace(
                "100x100",
                "600x600"
            )

    except:
        pass

    return None
def recommend(query, topn=10):
    q = (query or "").strip()
    if not q:
        return []
    recs = []

    try:
        if 'similarity' in globals() and similarity is not None:
            name_col = "Song_Title"
            lower_names = df[name_col].astype(str).str.lower().tolist()
            idx = None
            qlower = q.lower()
            for i, s in enumerate(lower_names):
                if s == qlower:
                    idx = i
                    break
            if idx is None:
                for i, s in enumerate(lower_names):
                    if qlower in s:
                        idx = i
                        break
            if idx is None and len(lower_names) > 0:
                idx = 0
                print("Selected index:", idx)
                print("Selected song:", df.iloc[idx]["Song_Title"])
            if idx is not None:
                sim_scores = list(enumerate(similarity[idx]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
                for i, score in sim_scores[:10]:
                    print(
                        df.iloc[i]["Song_Title"],
                        "|",
                        df.iloc[i]["Artist_Category"],
                        "|",
                        round(score, 3)
    )
                for i, score in sim_scores[:topn]:
                 row = df.iloc[i]

                recs.append({
                    "song": row["Song_Title"],
                    "artist": row["Artist_Category"],
                    "thumbnail": get_album_cover(
                        row["Song_Title"],
                        row["Artist_Category"]
        )
    })
            return recs
    except Exception:
        pass

    try:
        name_col = "Song_Title"
        artist_col = "Artist_Category"
        exact = df[df[name_col].astype(str).str.lower() == q.lower()]
        if len(exact) > 0:
            filtered = exact.head(topn)
        else:
            mask_name = df[name_col].astype(str).str.contains(q, case=False, na=False)
            if artist_col is not None:
                mask_artist = df[artist_col].astype(str).str.contains(q, case=False, na=False)
                filtered = df[mask_name | mask_artist].head(topn)
            else:
                filtered = df[mask_name].head(topn)
        for _, row in filtered.iterrows():
            recs.append({
                "song": row["Song_Title"],
                "artist": row["Artist_Category"],
                "thumbnail": get_album_cover(
                    row["Song_Title"],
                    row["Artist_Category"]
        )
    })
        if len(recs) < topn:
            existing = {r['song'] for r in recs}
            for _, row in df.head(topn).iterrows():
                if len(recs) >= topn:
                    break
                candidate = {
                    "song": row["Song_Title"],
                    "artist": row["Artist_Category"],
                    "thumbnail": get_album_cover(
                        row["Song_Title"],
                        row["Artist_Category"]
            )
}
                if candidate['song'] not in existing:
                    recs.append(candidate)
                    existing.add(candidate['song'])
        if not recs:
            for _, row in filtered.iterrows():
                recs.append({
                    "song": row["Song_Title"],
                    "artist": row["Artist_Category"],
                    "thumbnail": get_album_cover(
                        row["Song_Title"],
                        row["Artist_Category"]
        )
    })
    except:
        return []
    return recs

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(page_title="Song Recommender", layout="wide")

# ==========================
# CSS & STYLE
# ==========================
st.markdown("""
<style>
.stApp{
    background-image:url("https://direct-coffee-kpibh2wx.edgeone.app/wp6195787.jpg");
    background-size:cover;
    background-position:center;
    background-attachment:fixed;
}

.hero-title{
    font-size:75px;
    font-weight:900;
    text-align:center;
    background: linear-gradient(90deg,#00ff88,#00eaff,#7d7dff,#ff4df8);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    text-shadow:0 0 15px cyan,0 0 30px cyan,0 0 60px cyan;
}

.terminal-box{
    background: rgba(0,0,0,.75);
    padding: 20px;
    border-radius: 20px;
    border:2px solid #00ff88;
    box-shadow:0 0 25px #00ff88;
}

.monitor-box{
    background: rgba(0,0,0,.75);
    padding: 20px;
    border-radius: 20px;
    border:2px solid cyan;
    box-shadow:0 0 25px cyan;
}

/* Search input */
.stTextInput input{
    background: rgba(0,0,0,.85);
    border:2px solid cyan;
    color:white;
    border-radius:18px;

    height:55px !important;
    min-height:55px !important;

    font-size:20px;
    padding-left:20px !important;

    width:100%;
    box-shadow:0 0 10px cyan,
               0 0 25px rgba(0,255,255,.4);
}

/* Search button */
.stButton button{
    background:linear-gradient(90deg,#00eaff,#7d7fff);
    color:white;
    border:none;
    border-radius:14px;
    padding:14px 30px;
    font-size:18px;
    font-weight:bold;

    height:55px !important;
    margin-top:0px !important;

    box-shadow:0 0 10px cyan,
               0 0 30px rgba(0,255,255,.5);
}

.result-card{
    background:rgba(0,10,30,.85);
    border:1px solid #9c4dff;
    border-radius:18px;
    padding:20px;
    margin-top:20px;
    box-shadow:0 0 20px rgba(156,77,255,.4);
}
.result-card{
border:2px solid #00eaff;
box-shadow:0 0 20px cyan;
}

.song-card{
background:rgba(0,0,0,.6);
border:1px solid cyan;
border-radius:18px;
padding:10px;
box-shadow:0 0 15px rgba(0,255,255,.4);
}
.song-card:hover{
transform:scale(1.05);
transition:.3s;
}

.section-title{
    color:#00d9ff;
    font-size:32px;
    font-weight:800;
    margin-top:25px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;'>
<h1 class='hero-title'>🎵 SONG RECOMMENDER SYSTEM</h1>
<p style='font-size:28px;color:white;margin-top:5px;'>Discover. Play. Feel The Music.</p>
</div>
""", unsafe_allow_html=True)

# ==========================
# TERMINAL BOXES
# ==========================
left,right = st.columns([1,1])
with left:
    st.markdown(f"""
    <div style='
        background-image:url("https://direct-coffee-kpibh2wx.edgeone.app/wp6195787.jpg");
        background-size: cover;
        background-position: center;
        height:200px;
        border-radius:20px;
        box-shadow:0 0 25px #00ff88;
    '>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown(f"""
    <div style='
        background-image:url("https://direct-coffee-kpibh2wx.edgeone.app/wp6195787.jpg");
        background-size: cover;
        background-position: center;
        height:200px;
        border-radius:20px;
        box-shadow:0 0 25px cyan;
    '>
    </div>
    """, unsafe_allow_html=True)
# ==========================
# SEARCH
# ==========================
main_left, main_right = st.columns([2,1])
rec_songs = []

with main_left:

    user_input = st.text_input(
        "",
        placeholder="🔍 Search for a song..."
    )

    search_btn = st.button(
        "🔍 SEARCH",
        use_container_width=True
    )

    if search_btn and user_input:

        with st.spinner("🎵 Finding best songs..."):
            rec_songs = recommend(user_input)


# ============================
# RECOMMENDED SONGS
# ============================

if rec_songs:

    st.markdown(
        "<div class='section-title'>🎵 RECOMMENDED SONGS</div>",
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    for i, song in enumerate(rec_songs[:4]):

       with cols[i]:

            if song.get("thumbnail"):
                st.image(
                    song["thumbnail"],
                    use_container_width=True
        )

            st.markdown(
               f"""
               <h4 style="
                   text-align:center;
                   min-height:70px;
                   color:white;
                   margin-bottom:10px;
            ">
                   {song['song']}
               </h4>
              """,
              unsafe_allow_html=True
        )

            st.markdown(
                f"<p style='text-align:center;color:#00d9ff'>{song.get('artist','')}</p>",
                unsafe_allow_html=True
            )

            spotify_query = f"{song['song']} {song.get('artist','')}".replace(" ", "+")

            st.markdown(
                f"""
                <div style="text-align:center;margin-bottom:10px;">
                   <a href="https://open.spotify.com/search/{spotify_query}"
                      target="_blank"
                      style="
                      display:inline-block;
                      width:170px;
                      padding:12px;
                      background:#1DB954;
                      border-radius:10px;
                      color:white;
                      text-decoration:none;
                      font-weight:bold;
                      text-align:center;
                      ">
                      🎵 PLAY ON SPOTIFY
                   </a>
                </div>
       """,
       unsafe_allow_html=True
)

            youtube_query = f"{song['song']} {song.get('artist','')}".replace(" ", "+")

            st.markdown(
               f"""
              <div style="
              text-align:center;
              min-height:90px;
              display:flex;
              align-items:center;
              justify-content:center;
            ">
        <a href="https://www.youtube.com/results?search_query={youtube_query}"
           target="_blank"
           style="
           display:inline-block;
           width:170px;
           padding:12px;
           background:#dc2626;
           border-radius:10px;
           color:white;
           text-decoration:none;
           font-weight:bold;
           text-align:center;
           ">
           ▶ PLAY ON YOUTUBE
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
        



# ============================
# ALL SONGS LIBRARY (5-card layout)
# ============================
for _, row in df.head(10).iterrows():

    song_name = row.get("Song_Title", "")
    artist = row.get("Artist_Category", "")

    left, middle, right = st.columns([1,6,2])

    with left:

        search_name = song_name.replace(" ", "+")

        cover = get_album_cover(song_name, artist)

        if cover:
            st.image(cover, width=120)
    with middle:
        st.markdown(
            f"""
            <h3 style='color:white'>{song_name}</h3>
            <p style='color:#00eaff'>{artist}</p>
            """,
            unsafe_allow_html=True
        )

    with right:
        spotify_query = f"{song_name} {artist}".replace(" ","+")

        st.link_button(
            "▶ PLAY",
            f"https://open.spotify.com/search/{spotify_query}",
            use_container_width=True
        )

    st.divider()

st.markdown(
    "<div class='section-title'>⭐ RECOMMENDED FOR YOU</div>",
    unsafe_allow_html=True
)

cols = st.columns(5)

for i, song in enumerate(recommend("love",5)):

    with cols[i]:

        if song.get("thumbnail"):
            st.image(song["thumbnail"], use_container_width=True)

        st.markdown(
            f"<h4 style='text-align:center'>{song['song']}</h4>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<p style='text-align:center;color:#00d9ff'>{song['artist']}</p>",
            unsafe_allow_html=True
        )

        spotify_query = (
            f"{song['song']} {song['artist']}"
            .replace(" ","+")
        )

        st.link_button(
            "🟢 PLAY",
            f"https://open.spotify.com/search/{spotify_query}",
            use_container_width=True
        )
