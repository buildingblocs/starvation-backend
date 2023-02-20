echo Running ISort...
python -m isort .
echo

echo Running Black...
python -m black --line-length 120 --extend-exclude postgres_data .
echo

echo Running Flake8...
python -m flake8 .
echo