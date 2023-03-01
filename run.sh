# run.sh

# server
docker build -t bbcs/server ./server

# simulator
docker build -t bbcs/sandbox ./simulator

python k8s/setup-k8s.py
kubectl get deployments --namespace server
kubectl logs deployment/server-deployment --namespace server

kubectl expose deployment server-deployment --type=LoadBalancer --port=3000 --namespace server

minikube service server-deployment -n server
