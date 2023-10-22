# Auto Generating Migrations (FastAPI + SQLAlchemy + Alembic)

### Video Tutorial
[Click here](https://youtu.be/HuOG7VS8qvE)

### Installation & Configuration
- Clone this repository in your local machine by typing `git@github.com:Describly/fastapi-sqlalchemy-alembic.git`. 
- Open the Terminal and navigate to the project folder.
- Run `docker volume create describly_mysql_data` to create a docker volue in you machine. Required to persist the mysql data.
- Below will be your mysql connection details
```bash
MYSQL_HOST=mysql
MYSQL_USER=root
MYSQL_PASSWORD=Describly&123
MYSQL_DB=fastapi
MYSQL_PORT=3306
```
You do not need to change anything here, but if you would like to change the username, password or database name, you can modify it at this point in the `.env` file attached to this project. 

### Building the Project
- We can start building our projects by running `docker-compose build`
- One build is done, run `docker-compose up` to start the services. Leave this terminal open to check the logs.
- To stop the services you can press `Ctrl + C` - (Control + C)

### Commands
- To Generate the Migration From Model
```
docker-compose run fastapi-service /bin/sh -c "alembic revision --autogenerate -m "create my table table""
```
- To Apply the Migration to Database
```
docker-compose run fastapi-service /bin/sh -c "alembic upgrade head"
```
- To Revert last applied migration
```
docker-compose run fastapi-service /bin/sh -c "alembic downgrade -1"
```

# Accessing the Applications
- FastAPI Application Status [http://localhost:8000](http://localhost:8000)
- API Documentation [http://localhost:8000/docs](http://localhost:8000/docs)
- Database Access [http://localhost:8080](http://localhost:8080) - use the above detail to login.
- Mailpit [http://localhost:8025](http://localhost:8025)
# fastapi-sqlalchemy-alembic
