bridge-network

```
docker network create --gateway 172.19.0.1 --subnet 172.19.0.0/24 msa-network
```



```
docker run -it --name users -p 5002:5000 --net msa-network --ip 172.19.0.2 upi907/users
```



```
docker run -it --name totalcal_driving -p 5003:5000 --net msa-network --ip 172.19.0.3 upi907/totalcal_driving 
```



```
docker run -it --name driving_date -p 5004:5000 --net msa-network --ip 172.19.0.4 upi907/driving_date
```



```
docker run -it --name driving_score -p 5005:5000 --net msa-network --ip 172.19.0.5 upi907/driving_score 
```



```
docker run -it --name front -p 3000:3000 --net msa-network --ip 172.19.0.6 upi907/front
```



