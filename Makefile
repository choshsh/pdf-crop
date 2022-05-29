.PHONY: remote local deploy layer

export APP_NAME=pdfcrop

remote:
	sls invoke -f ${APP_NAME}  --data '{"bucket_name":"aws-frontend-s3-202202","object_key":"DB_260(01037691746).pdf"}'

local:
	sls invoke local -f ${APP_NAME} --data '{"bucket_name":"aws-frontend-s3-202202","object_key":"DB_260(01037691746).pdf"}'

deploy:
	sls deploy -f ${APP_NAME}

layer:
	pip3 install -r requirements.txt -t layers/python
