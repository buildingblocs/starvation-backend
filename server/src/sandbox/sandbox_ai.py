import time
from typing import Mapping, Tuple, Union, Any
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


def runner(solution_content: str, level: int) -> Tuple[bool, Mapping[str, Any]]:
    sandbox_name = f"sandbox-{uuid.uuid4()}"

    with open(fp / "sandbox-deployment.yml") as f:
        dep = yaml.safe_load(f)
        dep["metadata"]["name"] = sandbox_name
        dep["spec"]["containers"][0]["args"] = [solution_content, "", str(level)]
        pod = client.create_namespaced_pod(body=dep, namespace="sandbox")

    # wait for pod to be ready
    while True:
        pod = client.read_namespaced_pod(name=sandbox_name, namespace="sandbox")
        if pod.status.phase != "Pending": # type: ignore
            break
        time.sleep(0.1)

    print("Starting judging...")
    start = time.time()

    # 1s total wait time
    # for i in range(10):
    # any amount of wait time lmao
    # bro you want someone to just be able to sleep for 70 years???
    # 60s TL
    for i in range(600):
        time.sleep(0.1)

        pod = client.read_namespaced_pod(name=sandbox_name, namespace="sandbox")

        if pod.status.phase != "Running": # type: ignore
            break

    print("Ending judging...")
    runtime = time.time() - start

    if pod.status.phase == "Running": # type: ignore
        print("Killing")
        client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox")
        return (False, {"error": "Time limit exceeded", "runtime": runtime})
    
    logs = client.read_namespaced_pod_log(name=sandbox_name, namespace="sandbox", follow=True)

    json_out = logs.strip()

    if pod.status.phase == "Failed": # type: ignore
        print("Bad exit code")
        client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox")
        return (False, {"error": "Internal sandbox error: bad exit code", "details": json_out, "runtime": runtime})

    try:
        ret = orjson.loads(json_out.replace("'", '"'))
    except orjson.JSONDecodeError as e:
        client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox")
        return (False, {"error": str(e), "details": json_out, "runtime": runtime})

    client.delete_namespaced_pod(name=sandbox_name, namespace="sandbox")
    return (True, ret)


if __name__ != "__main__":
    print = dummy_print
