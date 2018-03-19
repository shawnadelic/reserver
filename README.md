# Reserver Reservation Management

This is an API for managing hotel reservation data.

## Setting up the Project
This project has been developed using Docker CE version
17.09.0 and Docker Compose version 1.16.1. It is possible
that other versions may have incompatibilities.

### 1. Clone project repository to local directory
Navigate to your desired directory and execute the following command
to clone the project repo:

`git clone https://github.com/shawnadelic/reserver`

### 2. Install Docker CE
Instructions for installing Docker CE on various platforms
can be found here:

https://docs.docker.com/install/

### 3. Install Docker Compose

Instructions for installing Docker Compose on various
platforms can be found here:
http://docs.docker.com/compose/install/

### 4. Build Docker images
Navigate to the project root (directory with `docker-compose.yml`) and
execute the following command to download and build the Docker images:

`docker-compose build`

### 5. Run Docker containers
Once the above is complete, execute the following command to start
the containers:

`docker-compose run`

Note: On initial setup, the Django project container may start before the
      Postgresql database container finishes setting up. If this happens,
      the best thing to do is simply to wait for the database container to
      finish setting up, then press Ctrl-C to stop Docker Compose, and one
      all of the containers have stopped, execute the Compose run command
      again.

### 6. Access container bash shell
Next, open a second terminal and execute the following command to list all
docker containers currently running:

`docker ps`

Find the the server container image (probably `reserver_server`), and
copy the container ID.

Next, execute the following command to access the container's bash shell,
replacing `CONTAINER_ID` with the container's ID hash.

`docker exec -t -i CONTAINER_ID bash`

### 7. Run project setup commands
From the project root, execute the following commands to set up project:

```
python3 manage.py migrate
python3 manage.py load_demo_data
```

Note: This command populates the project with test customers, destinations,
      and rooms, as well as a non-superuser test user (username: testuser,
      password: redcabbage).

### 8. Create a superuser
Execute the following command to create a superuser for the project:

```
python3 manage.py createsuperuser
```

## Running tests
To run tests, follow step 6 in the setup instructions to access the server
container's bash shell, then execute the following command to run the project's
test suite:

`pytest`

To also run the rate-limiting test, which takes 80+ seconds, execute the following
commands:

`pytest --slow`

## Project Notes

### Important URLs
* http://localhost:8000/admin/ - Django Admin
* http://localhost:8000/api/ - API Root
* http://localhost:8000/api-auth/login/ - Login page for browsable API
* http://localhost:8000/api-token-auth/login/ - API endpoint for creating user token
* http://localhost:8000/docs/ - Browse auto-generated API docs

### Models

Four basic resources are used to implement the reservations app:

* Destination - Hotel or motel facility with multiple rooms
* Room - Single room belong to a specific destination
* Customer - Contact information for a customer
* Reservation - Customer's reservation for a specific room and date range

Notes:

* Reservations cannot overlap date ranges for a specific room.
* Customer objects are not necessarily unique, although they can relate to
  multiple reservations
* Reservation GET views also provide a status indicating whether reservation
  is pending, in-house, or checked out.

### Rate Limiting/Throttling

A simple rate limiting has been implemented on reservation PUT and PATCH requests.

* If the user is a superuser, no rate limiting is done for any requests.
* Otherwise, for regular users, no more than 1 PUT or PATCH request per minute can be
  done on a single reservation (note, this doesn't apply to GET, POST, DELETE, etc.)
* Rate limiting still applies even if different non-superusers perform the update
  (i.e., user A changes the end date, then 30 seconds later user B tries to change
  the end date).

### Using API

The easiest way to test the API is to use Django Rest Frameworks' browseable API by
logging in at `/api-auth/login/`, then navigating to the api root at `/api/`.

Alternatively, an Authentication Token can be obtained using somethign like cURL by
first obtaining a CSRF Token by navigating to a login page in a web browser, then
execting a command such as the following (replacing `CSRF_TOKEN` with your actual token):

```
curl -d "username=testuser&password=redcabbage" -X POST http://localhost:8000/api-token-auth/login/ --cookie "csrftoken=CSRF_TOKEN"
```

This returns a JSON response containing a token. To make authenticated calls, do
something like the following (replacing AUTH_TOKEN with the returned token):

```
curl http://localhost:8000/api/ -H "Authorization: Token AUTH_TOKEN"
```
