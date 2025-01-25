# Viva Innovation Project
## Installation
### Dependencies
- Docker
- Docker Compose
### Steps
1. Clone the repository
2. Run `docker compose up`

# API Documentation
## Endpoints
### Health
#### GET /health
##### Description
Check the health of the API running
##### Response
```json
{
    "status": "ok"
}
```
### Users
#### POST /users/signup
##### Description
Create a new user
##### Request
```json
{
    "id": string,
    "email": string,
    "password": string,
}
```
##### Response
###### Success
```json
{
    "status": "ok"
}
```
#### POST /users/login
##### Description
Login a user
##### Request
```json
{
    "id": string,
    "password": string,
}
```
##### Response
###### Success
```json
{
    "access_token": string,
    "token_type": string,
}
```
#### POST /users/refresh
##### Description
Refresh the access token
##### Response
###### Success
```json
{
    "access_token": string,
    "token_type": string,
}
```
#### POST /users/logout
##### Description
Logout the user
##### Response
###### Success
```json
{
    "status": "ok"
}
```
