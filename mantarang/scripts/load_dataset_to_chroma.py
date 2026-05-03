import csv
import os
import chromadb
from tqdm import tqdm

def load_dataset_to_chroma(csv_path: str, chroma_path: str, collection_name: str = "music_tracks"):
    """Loads a track dataset into ChromaDB."""
    print(f"Loading dataset from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=chroma_path)
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    documents = []
    metadatas = []
    ids = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(tqdm(reader, desc="Processing rows")):
            # Expected columns: track_id, track_name, track_popularity, artist_name, artist_genres, etc.
            artist = row.get("artist_name", "Unknown Artist")
            title = row.get("track_name", "Unknown Title")
            track_id = row.get("track_id", f"track_{i}")
            popularity = row.get("track_popularity", 0)
            genres = row.get("artist_genres", "")
            
            doc_text = f"{artist} - {title}"
            
            meta = {
                "artist": artist,
                "title": title,
                "source": "csv_dataset",
                "popularity": int(popularity) if str(popularity).isdigit() else 0,
                "genres": genres
            }
            
            documents.append(doc_text)
            metadatas.append(meta)
            ids.append(track_id)
            
            # Batch insert every 1000 records
            if len(documents) >= 1000:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                documents = []
                metadatas = []
                ids = []
                
    # Insert remaining records
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
    print(f"Successfully loaded dataset into ChromaDB at {chroma_path}")
    print(f"Collection '{collection_name}' now has {collection.count()} items.")

if __name__ == "__main__":
    # Adjust path assuming the script is run from project root and dataset is in parent dir
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "track_data_final.csv")
    chroma_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")
    
    os.makedirs(chroma_db_path, exist_ok=True)
    load_dataset_to_chroma(dataset_path, chroma_db_path)
