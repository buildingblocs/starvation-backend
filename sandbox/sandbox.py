import docker
import tarfile
import io
import time
import arrow
import datetime

def dummy_print(*args):
    pass

def sandbox(stdin, ans, ansfile):
    client = docker.from_env()

    with open('../docker/judge.tar', 'rb') as image_tar:
        image = client.images.load(image_tar.read())[0]

    container = client.containers.create(
        image,
        command=['sh', '-c', 'python soln.py < in'],
        mem_limit='128m',
        network_mode=None,
        stop_signal='SIGKILL',
        pids_limit=25
    )

    stdin = stdin.encode('utf-8')

    tarfh = io.BytesIO()
    stdinfh = io.BytesIO(stdin)
    with tarfile.open(fileobj=tarfh, mode='w:gz') as tar:
        tar.add(ansfile, arcname='soln.py')

        info = tarfile.TarInfo('in')
        info.size = len(stdin)
        info.mtime = time.time()
        tar.addfile(info, stdinfh)

    tarfh.seek(0)
    container.put_archive('./', tarfh)

    stdinfh.close()
    tarfh.close()

    print("Starting judging...")

    container.start()

    # 2s total wait time
    for i in range(20):
        time.sleep(0.1)

        container.reload()
        status = container.status

        if status == 'exited':
            break

    print("Ending judging...")

    container.reload()
    status = container.status
    output = container.logs(stdout=True, stderr=False).decode('utf-8')
    err = container.logs(stdout=False, stderr=True).decode('utf-8')

    oom = container.attrs["State"]["OOMKilled"]
    starttm = arrow.get(container.attrs["State"]["StartedAt"])
    endtm = arrow.get(container.attrs["State"]["FinishedAt"])
    runtime = endtm - starttm

    if runtime > datetime.timedelta(seconds=1):
        print("TLE")
        container.remove()
        return (False, 2)

    if oom:
        print('Out Of Memory')
        container.remove()
        return (False, 3)

    if status != 'exited':
        print('Killing')
        container.kill()
        container.remove()
        print('TLE')
        return (False, 2)

    if len(err) > 0:
        print("Status: Error")
        print(err)
        container.remove()
        return (False, 0, err)

    o = int(output.strip())
    if o == ans:
        print("AC")
        container.remove()
        return (True, runtime / datetime.timedelta(microseconds=1000))

    print(f"Output mismatch: expected '{ans}', got '{o}'")
    container.remove()
    return (False, 1, ans, o)

if __name__ != '__main__':
    print = dummy_print

if __name__ == '__main__':
    sandbox('1', 1, 'soln.py')
