from pydantic import ValidationError
from requests import get

from models.models import Task


def get_tasks() -> list[Task]:
    response = get("http://task_api:8032/tasks/?skip=0&limit=-1",
                   auth=("string","string"),
                   # headers={"accept": "application/json","Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmciLCJzY29wZXMiOltdLCJleHAiOjE3MzE3MTkyNTN9.3wpD_Xpm75UnhIa9MECKvijVB2cP6gvfAmEbf7siMIo"}
                   )

    # Check if the response was successful
    if response.status_code == 200:
        try:
            # Parse and validate the response JSON into a list of Task models
            tasks = [Task.model_validate(task) for task in response.json()]
            return tasks
        except ValidationError as e:
            # Handle validation errors (e.g., invalid data format)
            print(f"Validation error: {e}")
            return []
    else:
        # Handle error if response is not successful
        print(f"Error: {response.status_code} - {response.text}")
        return []