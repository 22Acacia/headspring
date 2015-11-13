# headspring
generic-ish python source API

# deploy to GCP

# build the image:

docker build -t gcr.io/hx-test/prod-test .

# push to gcr.io:

gcloud docker push gcr.io/hx-test/prod-test

# create the cluster (note the scope):

gcloud container clusters create prod-test --num-nodes 1 --machine-type g1-small --scopes https://www.googleapis.com/auth/cloud-platform

# create the pod:

kubectl run prod-test --image=gcr.io/hx-test/prod-test --port=8080

# expose port 8080 to the outside world:

kubectl expose rc prod-test --create-external-load-balancer=true

# list the IP address the pod is listening on (this will take a few minutes to allocate the external IP):

kubectl get services prod-test

# curl some stuff to it:

curl -X POST -H "Content-Type:application/json" -d '{"name":"health","tags" : [ "traffic", "sustainability" ]}' [your IP]:8080/post
