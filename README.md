# etl-003_extract

# Development (running locally)
```sh
docker run --rm \
	-v $(pwd)/src:/etl/src \
	--name etl_demo \
	base_006_http:latest

# optional to get the manifest only -- useful for batching
docker run --rm \
	-e MANIFEST_ONLY=yep \
	-v $(pwd)/src:/etl/src \
	--name etl_demo \
	base_006_http:latest

```

# Docker Image Development & Publication

## Build Updated Image

```sh
docker build -t etl-003_extract:develop -f ./Dockerfile .
```

## Run Fresh Build

The only thing to pass in at runtime is output directory

```sh
docker run --rm \
	-v $(pwd)/src/output:/etl/src/output \
	--name etl_demo \
	etl-003_extract:develop
```

## Release
```sh
docker tag \
	etl-003_extract:develop \
	etl-003_extract:latest
```

## Publish
```sh
docker push etl-003_extract:latest
```

https://www2.census.gov/geo/tiger/TIGER2020/2020_TL_Shapefiles_File_Name_Definitions.pdf


https://www.starkandwayne.com/blog/bash-for-loop-over-json-array-using-jq/