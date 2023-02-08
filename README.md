# Docker Sandbox
(originally made for IO solution judging)

## Setup
1. Install docker

Follow instructions [here](https://docs.docker.com/get-docker/)
  
2. Install `pipenv` (virtual environment manager)

```
pip install --user pipenv
```

3. Install dependencies via `pipenv`

```
pipenv install
```

4. Activate the virtual environment

```
pipenv shell
```

5. Run `docker/judging-image.py` to make the judge image

```
cd docker
python judging-image.py
```

6. (optional) Test the sandbox

```
cd sandbox
python sandbox.py
```

## Usage
Run `validator.py` and provide a filename to test.
It will judge the code for you.



