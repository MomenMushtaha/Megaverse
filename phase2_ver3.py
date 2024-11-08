import requests
import time
import numpy as np


class MegaverseManager:
    BASE_URL = "https://challenge.crossmint.com/api/"

    def __init__(self, candidate_id):
        self.candidate_id = candidate_id

    def fetch_map_content(self, goal=False):
        """Fetches the current or goal map configuration."""
        url = f"{self.BASE_URL}map/{self.candidate_id}"
        if goal:
            url += "/goal"
        response = requests.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                map_content = data.get("goal") if goal else data.get("map", {}).get("content")
                return map_content
            except ValueError:
                print("Failed to decode JSON from response.")
        else:
            print(f"Failed to fetch map: {response.status_code}, {response.text}")
        return None

    def modify_map_to_goal(self):
        """
        Modifies only necessary elements to align the original map with the goal map.

        Returns:
            int: Total number of modifications needed.
        """
        original_map_content = self.fetch_map_content(goal=False)
        goal_map_content = self.fetch_map_content(goal=True)

        if original_map_content is None or goal_map_content is None:
            print("Failed to fetch maps for modification.")
            return 0  # Return 0 modifications if fetching fails

        # Convert map contents to NumPy arrays for efficient comparison
        original_array = self.map_content_to_array(original_map_content, is_goal=False)
        goal_array = self.map_content_to_array(goal_map_content, is_goal=True)

        # for better debugging and tracking, print the arrays with better formatting
        print("\nOriginal Grid Map:")
        self.print_array_as_grid(original_array)
        print("#" * 160)
        print("#" * 160)
        print("\nGoal Grid Map:")
        self.print_array_as_grid(goal_array)

        # Create a boolean mask where the maps differ
        diff_mask = original_array != goal_array

        # Get the indices where changes are needed
        indices = np.argwhere(diff_mask)

        total_modifications_needed = len(indices)
        print(f"\nTotal modifications needed: {total_modifications_needed}")

        for row, col in indices:
            # Convert to native Python int
            row = int(row)
            col = int(col)

            original_cell = original_array[row, col]
            goal_cell = goal_array[row, col]

            # Print applicable cells being compared
            print(f"\nAt position ({row}, {col}):")
            print(f"Original cell: '{original_cell}'")
            print(f"Goal cell: '{goal_cell}'")

            time.sleep(0.5)  # Delay to avoid hitting rate limit
            if goal_cell == "SPACE":
                self.delete_object(row, col, original_cell)
            else:
                self.create_object(row, col, goal_cell)

        return total_modifications_needed

    def cell_dict_to_type(self, cell):
        """
        Converts a cell dictionary from the original map into a cell type string.
        """
        type_mapping = {
            0: 'POLYANET',
            1: 'SOLOON',
            2: 'COMETH'
        }
        cell_type_code = cell.get('type', None)
        if cell_type_code is None:
            return "SPACE"
        else:
            cell_type_str = type_mapping.get(cell_type_code, None)
            if cell_type_str == 'POLYANET':
                return 'POLYANET'
            elif cell_type_str == 'SOLOON':
                color = cell.get('color', '').upper()
                return f"{color}_SOLOON"
            elif cell_type_str == 'COMETH':
                direction = cell.get('direction', '').upper()
                return f"{direction}_COMETH"
            else:
                return "UNKNOWN"

    def map_content_to_array(self, map_content, is_goal=False):
        """Converts map content to a NumPy array of standardized cell types."""
        rows = len(map_content)
        cols = len(map_content[0])
        array = np.empty((rows, cols), dtype=object)

        for i in range(rows):
            for j in range(cols):
                cell = map_content[i][j]
                if is_goal:
                    # For goal map, cell is a string or None
                    cell_type = cell if cell is not None else "SPACE"
                else:
                    # For original map, cell is a dict or None
                    if cell is not None:
                        # Process the cell to reconstruct the cell type string
                        cell_type = self.cell_dict_to_type(cell)
                    else:
                        cell_type = "SPACE"

                # Standardize the cell type
                if cell_type is not None:
                    cell_type = str(cell_type).strip().upper()
                else:
                    cell_type = "SPACE"

                array[i, j] = cell_type
        return array

    def print_array_as_grid(self, array):
        """Prints the NumPy array in a grid format for better readability."""
        rows, cols = array.shape
        for i in range(rows):
            row_str = ''
            for j in range(cols):
                cell = array[i, j]
                if cell == 'SPACE':
                    cell_str = '     '  # Empty space for better alignment
                else:
                    # Shorten the cell representation for better readability
                    if 'POLYANET' in cell:
                        cell_str = ' P '
                    elif 'SOLOON' in cell:
                        color = cell.split('_')[0][0]  # First letter of color
                        cell_str = f'S{color}'
                    elif 'COMETH' in cell:
                        direction = cell.split('_')[0][0]  # First letter of direction
                        cell_str = f'C{direction}'
                    else:
                        cell_str = 'UNK'
                row_str += f"{cell_str:5}"
            print(row_str)

    def print_map_content_as_grid(self, map_content, is_goal=False):
        """Prints the map content in a grid format for better readability."""
        rows = len(map_content)
        cols = len(map_content[0])

        for i in range(rows):
            row_str = ''
            for j in range(cols):
                cell = map_content[i][j]
                if is_goal:
                    # For goal map, cell is a string or None
                    cell_type = cell if cell is not None else "SPACE"
                else:
                    # For original map, cell is a dict or None
                    if cell is not None:
                        cell_type = self.cell_dict_to_type(cell)
                    else:
                        cell_type = "SPACE"

                # Shorten the cell representation for better readability
                if cell_type == 'SPACE':
                    cell_str = '     '
                else:
                    if 'POLYANET' in cell_type:
                        cell_str = ' P '
                    elif 'SOLOON' in cell_type:
                        color = cell_type.split('_')[0][0]  # First letter of color
                        cell_str = f'S{color}'
                    elif 'COMETH' in cell_type:
                        direction = cell_type.split('_')[0][0]  # First letter of direction
                        cell_str = f'C{direction}'
                    else:
                        cell_str = 'UNK'

                row_str += f"{cell_str:5}"
            print(row_str)

    def create_object(self, row, column, goal_cell, retries=3):
        """Creates an object at the specified location with retries."""
        url = f"{self.BASE_URL}"
        data = {
            "candidateId": self.candidate_id,
            "row": int(row),
            "column": int(column)
        }

        goal_cell = goal_cell.strip().upper()

        if goal_cell == "POLYANET":
            url += "polyanets"
        elif "SOLOON" in goal_cell:
            color = goal_cell.split("_")[0].lower()
            url += "soloons"
            data["color"] = color
        elif "COMETH" in goal_cell:
            direction = goal_cell.split("_")[0].lower()
            url += "comeths"
            data["direction"] = direction
        elif goal_cell == "SPACE":
            # Nothing to create
            return True
        else:
            print(f"Unknown goal cell type: {goal_cell}")
            return False

        while retries > 0:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print(f"Created {goal_cell} at ({row}, {column})")
                time.sleep(0.2)
                return True
            elif response.status_code == 429:  # Handle rate limiting
                print(f"Rate limit hit; retrying in 2 seconds.")
                time.sleep(2)
                retries -= 1
            else:
                print(f"Failed to create {goal_cell} at ({row}, {column}): {response.status_code}, {response.text}")
                return False

        print(f"Giving up on {goal_cell} at ({row}, {column}) after retries.")
        return False

    def delete_object(self, row, column, original_cell, retries=3):
        """Deletes an object at the specified location with retries."""
        url = f"{self.BASE_URL}"
        data = {
            "candidateId": self.candidate_id,
            "row": int(row),
            "column": int(column)
        }

        original_cell = original_cell.strip().upper()

        if original_cell == "POLYANET":
            url += "polyanets"
        elif "SOLOON" in original_cell:
            url += "soloons"
        elif "COMETH" in original_cell:
            url += "comeths"
        elif original_cell == "SPACE":
            # Nothing to delete
            return True
        else:
            print(f"Unknown original cell type: {original_cell}")
            return False

        while retries > 0:
            response = requests.delete(url, json=data)
            if response.status_code == 200:
                print(f"Deleted {original_cell} at ({row}, {column})")
                return True
            elif response.status_code == 429:  # Handle rate limiting
                print(f"Rate limit hit; retrying in 2 seconds.")
                time.sleep(2)
                retries -= 1
            else:
                print(f"Failed to delete {original_cell} at ({row}, {column}): {response.status_code}, {response.text}")
                return False

        print(f"Giving up on deleting {original_cell} at ({row}, {column}) after retries.")
        return False


if __name__ == "__main__":
    candidate_id = "e172ee08-c186-4a8b-94f8-e95861c9243c"
    manager = MegaverseManager(candidate_id)
    total_changes = manager.modify_map_to_goal()
    print(f"\nTotal number of changes needed: {total_changes}")
