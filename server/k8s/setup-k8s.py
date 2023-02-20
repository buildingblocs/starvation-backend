from pathlib import Path

import kubernetes
import yaml

kubernetes.config.load_kube_config()
fp = Path(__file__).parent.absolute()

# create namespace if not exists
client = kubernetes.client.CoreV1Api()
networking = kubernetes.client.NetworkingV1Api()
rbac = kubernetes.client.RbacAuthorizationV1Api()

with open(fp / "server-namespace.yml") as f:
    ns = yaml.safe_load(f)
    try:
        client.create_namespace(body=ns)
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        client.replace_namespace(name="server", body=ns)

with open(fp / "sandbox-namespace.yml") as f:
    ns = yaml.safe_load(f)
    try:
        client.create_namespace(body=ns)
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        client.replace_namespace(name="sandbox", body=ns)

with open(fp / "sandbox-networkpolicy.yml") as f:
    np = yaml.safe_load(f)
    try:
        networking.create_namespaced_network_policy(body=np, namespace="sandbox")
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        networking.replace_namespaced_network_policy(body=np, name="default-deny-networking", namespace="sandbox")

with open(fp / "sandbox-pods-role.yml") as f:
    role = yaml.safe_load(f)
    try:
        rbac.create_namespaced_role(body=role, namespace="sandbox")
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        rbac.replace_namespaced_role(body=role, name="server-sandbox-pods", namespace="sandbox")

with open(fp / "server-serviceaccount.yml") as f:
    svcacct = yaml.safe_load(f)
    try:
        client.create_namespaced_service_account(body=svcacct, namespace="server")
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        client.replace_namespaced_service_account(body=svcacct, name="bbcs-server", namespace="server")


with open(fp / "sandbox-pods-rolebinding.yml") as f:
    rolebinding = yaml.safe_load(f)
    try:
        rbac.create_namespaced_role_binding(body=rolebinding, namespace="sandbox")
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        rbac.replace_namespaced_role_binding(body=rolebinding, name="server-sandbox-pods-binding", namespace="sandbox")

# start deployment
apps = kubernetes.client.AppsV1Api()
with open(fp / "server-deployment.yml") as f:
    dep = yaml.safe_load(f)
    try:
        apps.create_namespaced_deployment(body=dep, namespace="server")
    except kubernetes.client.ApiException as e:
        if e.reason != "Conflict":
            raise
        apps.delete_namespaced_deployment(name="server-deployment", namespace="server")
        apps.create_namespaced_deployment(body=dep, namespace="server")
