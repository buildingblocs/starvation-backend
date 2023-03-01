# Starvation-Backend

Usage steps:

1. Install `minikube`
2. Run `minikube docker-env` and copy the command.
3. Use docker to build `bbcs/server` (Dockerfile in server/src) and `bbcs/sandbox` (Dockerfile in server/src/sandbox)
4. Run `setup_k8s.py` in `server/k8s`, which will deploy the server.