from locust import HttpUser, task, between


class MyUser(HttpUser):
    wait_time = between(1, 3)
    base_url = "https://smartarena-bbff190dd374.herokuapp.com/"

    def on_start(self):
        # Perform the initial authentication and obtain a token
        response = self.client.post("/login", json={"username": "test", "password": "hoooasdasda"})
        if response.status_code == 201:
            # If the login is successful, extract and save the token
            self.token = response.json().get("access")
            self.refresh = response.json().get("refresh")
        else:
            # Handle authentication failure as needed
            print("Authentication failed:", response.text)
            self.environment.runner.quit()

    @task
    def create_stadium(self):
        # Use the access token in the request headers
        headers = {"Authorization": f"Bearer {self.access}"}

        # Define the data for creating a stadium (replace with your own values)
        stadium_data = {
            "name": "new_stadium",
            "description": "example@gmail.com",
            "image": "https://example.com/image.png",
            "price": 150.45,
            "opening_time": "08:00:00",
            "closing_time": "22:00:00",
            "is_active": True,
            "region": "NewRegion",
            "district": "NewDistrict",
            "location": "3-uy"
        }

        # Make a POST request to create a stadium
        response = self.client.post("/stadium/", json=stadium_data, headers=headers)

        # Print the response status and content for debugging (optional)
        print(f"Create Stadium - Status Code: {response.status_code}, Response: {response.text}")

    @task
    def edit_stadium(self):
        # Use the access token in the request headers
        headers = {"Authorization": f"Bearer {self.access}"}

        # Define the data for editing a stadium (replace with your own values)
        stadium_id = 1  # Replace with the actual ID of the stadium to edit
        updated_data = {
            "name": "edited_stadium",
            "price": 200.0,
            "is_active": False,
        }

        # Make a PATCH request to edit the stadium
        response = self.client.patch(f"/stadium/edit?s={stadium_id}", json=updated_data, headers=headers)

        # Print the response status and content for debugging (optional)
        print(f"Edit Stadium - Status Code: {response.status_code}, Response: {response.text}")

        # You can add more tasks or continue testing other endpoints as needed



