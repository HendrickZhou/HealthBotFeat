#HealthBotFeat
Feature Storage service for health bot

# setup 
create docker network and volume first

# design note
using external volume due the convenience of development

# for testing script with interactive pdb
docker-compose run --rm --service-ports feature-api
# one example line for testing the fastAPI
curl -X GET "http://localhost:8000/features/standtime?userID=101&now=2021-01-18T13:42:44.000Z"

# docker related
// take down the whole thing:
docker compose --profile app
down
// rebuild 
docker-compose build feature-api
// up profile
docker-compose --profile app up -d
or
docker-compose up -d feature-api
// force clean start
docker-compose down
docker-compose build feature-api
docker-compose up -d

# for migrating the hostmachine for now:
you need to create external network: shared-influx-network
`docker network create shared-influx-network`
you also need to deal with the external volume: infra_influxdb-data
This is a bit complicated, you need a tmp container that deal with the data directly, it's considered bad practice to directly work with the actual path docker handle the volume.
for source & target machine, you both need a tmp container:

`docker run --rm \
  -v infra_influxdb-data:/data \
  -v $(pwd):/backup \
  alpine \
  sh -c "cd /data && tar czf /backup/influxdb_backup.tar.gz ."
`
then copy the file to your target machine, if in macos, you can directly use sftp or scp. Let's say you put the zip file under /tmp directory under target machine.
then you need to
`docker volume create infra_influxdb-data`

`
docker run --rm \
  -v infra_influxdb-data:/data \
  -v /tmp:/backup \
  alpine \
  sh -c "cd /data && tar xzf /backup/influxdb_backup.tar.gz"
`

