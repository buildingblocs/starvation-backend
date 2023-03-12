import time
import uuid
from pathlib import Path

import kubernetes
import orjson
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
    # for i in range(10):
    # any amount of wait time lmao
    # bro you want someone to just be able to sleep for 70 years???
    # 10s TL
    for i in range(100):
        time.sleep(0.1)

        pod = client.read_namespaced_pod(name=sandbox_name, namespace="sandbox")

        if pod.status.phase != "Running":
            break

    print("Ending judging...")

    if pod.status.phase == "Running":
        print("Killing")
        client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox")
        return (False, 0)

    if pod.status.phase == "Failed":
        print("Bad exit code")
        return (False, 0)

    logs = client.read_namespaced_pod_log(name=sandbox_name, namespace="sandbox", follow=True)

    json_out = logs.strip()

    try:
        ret = orjson.loads(json_out.replace("'", '"'))
    except orjson.JSONDecodeError as e:
        return (False, f'{json_out}///{str(e)}')

    return (True, ret)


if __name__ != "__main__":
    print = dummy_print
