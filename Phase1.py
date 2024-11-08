import requests
from time import sleep

class MegaverseObject:
    """Base class for Megaverse entities, handling API requests."""
    BASE_URL = "https://challenge.crossmint.io/api/"

    def __init__(self, candidate_id):
        self.candidate_id = candidate_id

    def _make_request(self, method, endpoint, data, retries=5):
        """Handles API requests with retry logic for rate limiting."""
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(retries):
            try:
                response = requests.request(method, url, json=data)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = 2 ** attempt
                    print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    sleep(wait_time)  # Exponential backoff
                else:
                    print(f"Error {response.status_code} for {method} on {url}: {response.text}")
                    break
            except requests.RequestException as e:
                print(f"Request exception: {e}")
                sleep(2 ** attempt)
        return None

class Polyanet(MegaverseObject):
    """Represents a Polyanet entity with create and delete operations."""
    def create(self, row, column):
        data = {"candidateId": self.candidate_id, "row": row, "column": column}
        return self._make_request("POST", "polyanets", data)

    def delete(self, row, column):
        data = {"candidateId": self.candidate_id, "row": row, "column": column}
        return self._make_request("DELETE", "polyanets", data)

class MegaverseManager:
    """Manages the grid and shapes within the Megaverse."""
    def __init__(self, candidate_id, grid_size=11):
        self.candidate_id = candidate_id
        self.grid_size = grid_size
        self.polyanet = Polyanet(candidate_id)

    def clear_grid(self):
        """Clears the entire grid by deleting all entities."""
        positions = [(row, col) for row in range(self.grid_size) for col in range(self.grid_size)]
        self._process_positions(positions, self.polyanet.delete)

    def create_x_shape(self, padding=2):
        """
        Creates an 'X' shape on the grid with specified padding.
        The 'X' spans from (padding, padding) to (grid_size - padding - 1, grid_size - padding - 1).
        """
        start = padding
        end = self.grid_size - padding  # Exclusive in range

        # Generate positions for the X shape
        positions = set()
        for i in range(start, end):
            positions.add((i, i))  # Backslash diagonal
            positions.add((i, start + end - 1 - i))  # Slash diagonal

        self._process_positions(positions, self.polyanet.create)

    def _process_positions(self, positions, action):
        """Processes a list of positions with the given action (create/delete)."""
        for row, column in positions:
            action(row, column)
            sleep(0.5)  # Adjust delay as needed to avoid rate limits

if __name__ == "__main__":
    candidate_id = "e172ee08-c186-4a8b-94f8-e95861c9243c"
    manager = MegaverseManager(candidate_id)

    # Step 1: Clear the grid
    manager.clear_grid()

    # Step 2: Create the X-shaped pattern with 2-element padding
    manager.create_x_shape(padding=2)
