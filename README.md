# Orbital Decay Predictor
### Visualize when and where space junk will soon de-orbit.  

# Execution


Orbital perturbation data is retrieved from [Celestrak](https://celestrak.org/) twice daily. 
The data is filtered to isolate objects in Low Earth Orbit (LEO), after which the SGP4 and Skyfield libraries are used 
to estimate their trajectories over the next seven days.

If an object’s altitude drops below the [Kármán line](https://en.wikipedia.org/wiki/K%C3%A1rm%C3%A1n_line) (100 km), 
it is flagged as having deorbited. The final 15 minutes of the object's flight path are then serialized into a 
GeoJSON file, uploaded to AWS S3, and rendered on a custom Mapbox web map.

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