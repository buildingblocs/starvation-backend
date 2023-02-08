import docker

client = docker.from_env()

image, logs = client.images.build(
    path='./',
    forcerm=True
)

for log in logs:
    print(log)

with open('judge.tar', 'wb') as f:
    for chunk in image.save():
        f.write(chunk)