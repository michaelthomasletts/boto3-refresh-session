docker build -f tests/Dockerfile.ecs_test -t brs-ecs-test .
docker run --rm brs-ecs-test