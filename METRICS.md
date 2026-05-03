# ManTarang — Metrics & Confidence Explained

This document explains every number the system shows you: how each
metric is calculated, what it means, and how the overall confidence
score is derived.

---

## Per-Track Metrics

Every recommended track gets four independent scores (0 – 100).

### 1. Genre Match  `genre_match`

**What it measures:** How closely the track's genres overlap with
the target genres extracted from your query.

**How it's calculated:**

```
genre_match = genre_overlap_score(track_genres, target_genres) × 100
```

`genre_overlap_score` is a Jaccard-like function with substring
tolerance:

```python
def _genre_overlap_score(track_genres, target_genres):
    if not target_genres:
        return 0.0
    matches = sum(
        1 for tg in target_genres
        if any(tg in g or g in tg for g in track_genres)
    )
    return matches / len(target_genres)
```

- A track tagged `["alternative rock", "art rock"]` against a target
  of `["art rock", "alternative rock"]` scores **100 %**.
- A track tagged `["pop"]` against `["indie rock", "folk"]` scores **0 %**.
- Substring matching means `"lo-fi hip hop"` matches the target
  `"lo-fi"`.

**Weight in relevance:** 45 %

---

### 2. Popularity Fit  `popularity_fit`

**What it measures:** How popular the track is on a 0–100 scale
(sourced directly from `track_popularity` in the dataset).

**How it's calculated:**

```
popularity_fit = track_popularity   # already 0–100 in the CSV
```

A score of 80 means the track has high mainstream appeal.
A score of 20 means it is more niche or underground.

This is not about whether the song *fits* your taste for popular
music — it is used as a quality/discovery signal blended with the
other metrics.

**Weight in relevance:** 30 %

---

### 3. Artist Credibility  `artist_score`

**What it measures:** How established the artist is, using their
total follower count as a proxy for credibility and discoverability.

**How it's calculated:**

```python
artist_score = min(100, max(0, (log10(max(followers, 1)) / 8) * 100))
```

| Followers | artist_score |
|-----------|-------------|
| 10 k      | ~37          |
| 100 k     | ~50          |
| 1 M       | ~62          |
| 10 M      | ~75          |
| 100 M     | ~87          |

Log-normalisation prevents mega-artists from dominating while still
rewarding established acts over unknowns.

**Weight in relevance:** 25 %

---

### 4. Overall Relevance  `relevance`

**What it measures:** A single 0–100 score that blends the three
metrics above into one headline number.

**Formula:**

```
relevance = (genre_match × 0.45)
          + (popularity_fit × 0.30)
          + (artist_score × 0.25)
```

This is the score shown in the circular ring on each track card.

---

## Per-Track Confidence  `confidence`

**What it measures:** How confident the system is that *this
specific track* is a good recommendation, independently of relevance.

**Formula:**

```
confidence = (genre_match × 0.50)
           + (artist_score × 0.30)
           + (popularity_fit × 0.20)
           all divided by 100   →   0.0 – 1.0
```

Confidence weights genre match and artist credibility more heavily
than relevance does, because a song in exactly the right genre from
a credible artist is more reliably a good pick than a merely popular
song.

| confidence | label    | meaning                              |
|------------|----------|--------------------------------------|
| ≥ 0.80     | High     | Strongly on-target                  |
| 0.60–0.79  | Good     | Solid match, minor gaps              |
| 0.40–0.59  | Moderate | Partial match or niche genre          |
| < 0.40     | Low      | Weak signal, possibly a fallback     |

---

## Aggregate / System Metrics

After all tracks are scored the system computes session-level stats.

### avg_relevance / avg_genre_match / avg_confidence

Simple arithmetic means across all returned tracks.

### system_confidence

A composite session-level confidence that combines track-level
confidence with two bonuses:

```
system_confidence =
    avg_confidence × 100 × 0.75   # base from per-track scores
  + strategy_premium               # bonus by strategy type
  + diversity_bonus                # bonus for genre variety
```

**Strategy premiums:**

| Strategy         | Premium |
|------------------|---------|
| `artist_match`   | +10     |
| `similarity`     | +8      |
| `genre_mood`     | +6      |
| `text_match`     | +4      |
| `popular_fallback` | +0   |

Artist-match and similarity strategies are the most precise; the
popular-fallback is a last resort with no premium.

**Diversity bonus:**
```
diversity_bonus = min(10, genre_diversity)
```
Returns up to 10 extra points when the result set covers many
distinct genres, rewarding broad, useful recommendations.

### genre_diversity / artist_diversity

- `genre_diversity` — number of *distinct* genre tags across all
  returned tracks.
- `artist_diversity` — number of distinct artists across all
  returned tracks.

Both are raw counts (not percentages). The UI converts them to
approximate 0–100 display values for the bar charts.

---

## Strategy Selection

The system picks a recommendation strategy per query:

| Strategy          | Triggered when                                         |
|-------------------|--------------------------------------------------------|
| `artist_match`    | Query contains an artist name found in the dataset     |
| `similarity`      | Same as artist_match; ranks by genre overlap           |
| `genre_mood`      | Query matches mood keywords (sad, chill, dark…)         |
| `text_match`      | Keywords from query match track/artist names           |
| `popular_fallback`| No strong signal found; returns diverse popular tracks |

The strategy is shown next to the system confidence in the quality panel.

---

## Data Sources

| Column used           | CSV file                     |
|-----------------------|------------------------------|
| `track_popularity`    | `track_data_final.csv`       |
| `artist_followers`    | `track_data_final.csv`       |
| `artist_genres`       | `track_data_final.csv`       |
| Genre enrichment      | `spotify_data clean.csv`     |

Both CSVs are merged at startup into a single artist → genre lookup
table, boosting genre coverage from ~49 % to ~61 % of all tracks.
