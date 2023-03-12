# run.sh
# set docker cr to minikube
eval $(minikube -p minikube docker-env)

# server
docker build -t bbcs/server ./server

# simulator
docker build -t bbcs/sandbox ./simulator

# use helm to setup k8s
helm upgrade --install starvation-backend ./helm

# python k8s/setup-k8s.py
# kubectl get deployments --namespace server
# kubectl logs deployment/server-deployment --namespace server

# kubectl expose deployment server-deployment --type=LoadBalancer --port=3000 --namespace server

minikube service server-service -n server --url
