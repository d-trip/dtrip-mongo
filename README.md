# dtrip-mongo
Mongo database for dtrip.app

## Run Docker:
```
docker run --restart unless-stopped --name dtrip-mongo-parser -t -d \
  -e MONGO_HOST= \
  -e MONGO_USER= \
  -e MONGO_PASSWORD= \
  avral/dtrip-mongo python main.py <flags>
```

## Flags:
`--resync` Update all accounts.  
`--swm` Collect all SteemitWorldMap posts  
`--block` The block number from which to start synchronization  
`--current` Start synchronization from current head block  

## Example:
Collect all data and start streaming blocks
```
python main.py --resync --swm --current
```
