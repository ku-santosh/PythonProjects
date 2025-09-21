Perspective APIThis project provides a robust and scalable CRUD (Create, Read, Update, Delete) API for managing user perspectives. The API is built with FastAPI, Pydantic, and SQLAlchemy, and uses a PostgreSQL database for data persistence. It follows a modular and clean architecture, making it easy to extend and maintain.Key FeaturesComplete CRUD Functionality: Full support for creating, reading, updating, and deleting user perspective data.Data Validation: Uses Pydantic schemas to validate incoming request data and ensure data integrity.Unique Constraints: Enforces uniqueness on the username field and prevents duplicate name values within column_state and sort_model.Database Integration: Connects to a PostgreSQL database using SQLAlchemy ORM.Containerized Environment: Packaged with Docker and Docker Compose for easy setup and deployment.Modular Architecture: The codebase is organized into dedicated folders for API routes, services, schemas, and models for better separation of concerns.PrerequisitesTo run this project, you need to have the following installed on your machine:DockerDocker ComposeGetting StartedClone the repository (or save the files):Ensure all the project files (app/, Dockerfile, docker-compose.yml, requirements.txt) are in a single directory.Build and run the containers:Navigate to the project's root directory in your terminal and run the following command. This will build the FastAPI application image and start both the application and the PostgreSQL database containers.docker-compose up --build

Access the API:Once the containers are running, the API will be accessible at http://localhost:8000. You can view the automatically generated interactive API documentation (Swagger UI) at http://localhost:8000/docs.API EndpointsThe API provides the following endpoints for managing perspectives:MethodEndpointDescriptionPOST/api/v1/perspectivesCreates a new perspective. Requires a unique username.GET/api/v1/perspectives/{username}Retrieves a single perspective by its username.PATCH/api/v1/perspectives/{username}Updates an existing perspective. Supports partial updates of fields.DELETE/api/v1/perspectives/{username}Deletes a perspective by its username.Project Structure.
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── perspective_routes.py  # API endpoints definition
│   ├── models/
│   │   └── perspective_model.py         # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── perspective_schemas.py       # Pydantic data validation schemas
│   ├── services/
│   │   └── perspective_service.py       # Business logic layer
│   ├── main.py                          # Application entry point
│   └── database.py                      # Database connection setup
├── Dockerfile                           # Docker build instructions
├── docker-compose.yml                   # Docker Compose configuration
└── requirements.txt                     # Python dependencies
