import time
import requests


class MegaverseManager:
    """Manages the grid and interactions within the Megaverse."""
    BASE_URL = "https://challenge.crossmint.io/api/"
    CANDIDATE_ID = "e172ee08-c186-4a8b-94f8-e95861c9243c"

    def fetch_map_content(self):
        """Fetches the map content from the specified URL."""
        url = f"{self.BASE_URL}map/{self.CANDIDATE_ID}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('map', {}).get('content', [])
        else:
            print(f"Failed to fetch map content: {response.status_code}")
            return []

    def delete_object(self, row, column, obj_type, additional_params=None):
        """Deletes an object at the specified row and column."""
        if obj_type == "polyanet":
            url = f"{self.BASE_URL}polyanets"
        elif obj_type == "soloon":
            url = f"{self.BASE_URL}soloons"
        elif obj_type == "cometh":
            url = f"{self.BASE_URL}comeths"
        else:
            print(f"Unknown object type at ({row}, {column})")
            return False

        payload = {
            "row": row,
            "column": column,
            "candidateId": self.CANDIDATE_ID
        }
        if additional_params:
            payload.update(additional_params)

        response = requests.delete(url, json=payload)
        if response.status_code == 200:
            print(f"Successfully deleted {obj_type} at ({row}, {column})")
            return True
        elif response.status_code == 405:
            print(f"Method Not Allowed: Failed to delete {obj_type} at ({row}, {column})")
            return False
        else:
            print(f"Failed to delete {obj_type} at ({row}, {column}): {response.status_code}")
            return False

    def clear_non_space_objects(self):
        """Clears all objects that are not SPACE by deleting them."""
        map_content = self.fetch_map_content()
        if not map_content:
            print("Map content is empty or couldn't be fetched.")
            return

        for row_idx, row in enumerate(map_content):
            for col_idx, cell in enumerate(row):
                if cell is None:
                    continue  # Skip SPACE cells

                obj_type = None
                additional_params = {}
                if cell.get("type") == 0:  # Polyanet
                    obj_type = "polyanet"
                elif cell.get("type") == 1:  # Soloon
                    obj_type = "soloon"
                    additional_params["color"] = cell.get("color", "white")
                elif cell.get("type") == 2:  # Cometh
                    obj_type = "cometh"
                    additional_params["direction"] = cell.get("direction", "up")

                if obj_type:
                    success = self.delete_object(row_idx, col_idx, obj_type, additional_params)
                    # Wait between API calls to avoid hitting rate limits
                    time.sleep(0.5)
                    # Retry logic if delete fails
                    retries = 3
                    while not success and retries > 0:
                        time.sleep(1)
                        success = self.delete_object(row_idx, col_idx, obj_type, additional_params)
                        retries -= 1
                    if not success:
                        print(f"Giving up on deleting {obj_type} at ({row_idx}, {col_idx}) after retries.")


if __name__ == "__main__":
    manager = MegaverseManager()
    # Clear all objects that are not SPACE
    manager.clear_non_space_objects()
