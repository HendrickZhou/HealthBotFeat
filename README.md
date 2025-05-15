# HealthBotFeat
Feature Storage service for health bot


# for testing script with interactive pdb
docker-compose run --rm --service-ports feature-api
# one example line for testing the fastAPI
curl -X GET "http://localhost:8000/steptime?userID=101&start=2021-01-26T00:00:00Z&stop=2022-01-26T23:59:59Z"

