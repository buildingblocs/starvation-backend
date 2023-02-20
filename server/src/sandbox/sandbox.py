import time
import uuid
from pathlib import Path

import kubernetes
import yaml


def dummy_print(*args):
    pass


kubernetes.config.load_incluster_config()
fp = Path(__file__).parent.absolute()

client = kubernetes.client.CoreV1Api()


def sandbox(solution_content):
    sandbox_name = f"sandbox-{uuid.uuid4()}"

    with open(fp / "sandbox-deployment.yml") as f:
        dep = yaml.safe_load(f)
        dep["metadata"]["name"] = sandbox_name
        dep["spec"]["containers"][0]["args"] = [solution_content]
        pod = client.create_namespaced_pod(body=dep, namespace="sandbox")

    # wait for pod to be ready
    while True:
        pod = client.read_namespaced_pod(name=sandbox_name, namespace="sandbox")
        if pod.status.phase != "Pending":
            break
        time.sleep(0.1)

    print("Starting judging...")

    # 1s total wait time
    for i in range(10):
        time.sleep(0.1)

        pod = client.read_namespaced_pod(name=sandbox_name, namespace="sandbox")

        if pod.status != "Running":
            break

    print("Ending judging...")

    if pod.status == "Running":
        print("Killing")
        client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox", grace_period_seconds=0)
        return (False, 0)

    logs = client.read_namespaced_pod_log(name=sandbox_name, namespace="sandbox")

    return (True, logs.strip())


if __name__ != "__main__":
    print = dummy_print
