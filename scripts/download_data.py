import os
import urllib.request
import sys

def download_file(url, output_path):
    print(f"Downloading {url} to {output_path}...")
    try:
        urllib.request.urlretrieve(url, output_path)
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Success! Size: {size:.2f} MB")
    except Exception as e:
        print(f"Failed to download {url}. Error: {e}")

if __name__ == "__main__":
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(cwd, "data", "raw")
    
    osm_url = "https://download.geofabrik.de/europe/france/bretagne-latest.osm.pbf"
    osm_path = os.path.join(raw_dir, "bretagne-latest.osm.pbf")
    download_file(osm_url, osm_path)
    
    snap_url = "https://snap.stanford.edu/data/as-caida20071105.txt.gz"
    snap_path = os.path.join(raw_dir, "as-caida20071105.txt.gz")
    download_file(snap_url, snap_path)
