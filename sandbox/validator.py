from sys import stdin, stdout
import sandbox

import docker
import tqdm
import multiprocessing

from pprint import pprint

generators = [lambda a: a]

def sandbox_wrapper(tuple):
    return sandbox.sandbox(*tuple)

def validate(filename):
    res = []
    for i, st in enumerate(generators):
        print(f'Subtask {i + 1}')

        params = []
        for tc in range(20):
            params.append((str(tc), tc, filename))

        print("Starting testing...")

        cres = []
        with multiprocessing.Pool(4) as p:
            for result in tqdm.tqdm(p.imap(sandbox_wrapper, params), total=20):
                cres.append(result)
                if not result[0]:
                    p.terminate()
                    break
        
        cres_padded = [cres[i] if i < len(cres) else (None,) for i in range(20)]
        res.append(cres_padded)

    pprint(res)
    return res


if __name__ == '__main__':
    filename = input().strip()
    validate(filename)