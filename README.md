# Orbital Decay Predictor
Visualize when and where space junk will soon de-orbit


## Architecture
```mermaid
graph TD;
    SGP4(SGP4)-->Docker;
    Skyfield(Skyfield)-->Docker(Docker);
    Docker-->ECR("Amazon ECR (Elastic Container Registry)");
    ECR-->ECS(ECS);
    ECS-->S3(Amazon S3);
    celestrak.org(celestrak.org) -->ECS("Amazon ECS (Elastic Container Service)");
    EventBridge(Amazon Event Bridge)-->ECS
    S3-->CloudFront(Amazon Cloud Front);
    click SGP4 "https://pypi.org/project/sgp4/" "Go to SGP4 documentation"
    click Skyfield "https://rhodesmill.org/skyfield/" "Go to Skyfield documentation"
    click celestrak.org "celestrak.org" "Go to celestrak.org"
```