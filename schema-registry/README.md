### Install and integrate Schema Registry

1- Install Postgres on OKE


```
helm repo add bitnami https://charts.bitnami.com/bitnami

[opc@bastion streaming]$ helm install pg-release bitnami/postgresql
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /home/opc/.kube/config
WARNING: Kubernetes configuration file is world-readable. This is insecure. Location: /home/opc/.kube/config
NAME: pg-release
LAST DEPLOYED: Sun Oct 29 03:44:53 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: postgresql
CHART VERSION: 13.1.5
APP VERSION: 16.0.0

** Please be patient while the chart is being deployed **

PostgreSQL can be accessed via port 5432 on the following DNS names from within your cluster:

    pg-release-postgresql.default.svc.cluster.local - Read/Write connection

To get the password for "postgres" run:

    export POSTGRES_PASSWORD=$(kubectl get secret --namespace default pg-release-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

To connect to your database run the following command:

    kubectl run pg-release-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:16.0.0-debian-11-r13 --env="PGPASSWORD=$POSTGRES_PASSWORD" \
      --command -- psql --host pg-release-postgresql -U postgres -d postgres -p 5432

    > NOTE: If you access the container using bash, make sure that you execute "/opt/bitnami/scripts/postgresql/entrypoint.sh /bin/bash" in order to avoid the error "psql: local user with ID 1001} does not exist"

To connect to your database from outside the cluster execute the following commands:

    kubectl port-forward --namespace default svc/pg-release-postgresql 5432:5432 &
    PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U postgres -d postgres -p 5432

WARNING: The configured password will be ignored on new installation in case when previous PostgreSQL release was deleted through the helm command. In that case, old PVC will have an old password, and setting it through helm won't take effect. Deleting persistent volumes (PVs) will solve the issue.
```

Get Postgres password
```
[opc@bastion streaming]$ export POSTGRES_PASSWORD=$(kubectl get secret --namespace default pg-release-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
[opc@bastion streaming]$ echo $POSTGRES_PASSWORD
GfSXdxXd6C

[opc@bastion streaming]$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
pg-release-postgresql-0   1/1     Running   0          3m27s
[opc@bastion streaming]$ kubectl get svc
NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
kubernetes                 ClusterIP   10.96.0.1       <none>        443/TCP,12250/TCP   115d
pg-release-postgresql      ClusterIP   10.96.166.176   <none>        5432/TCP            3m44s
pg-release-postgresql-hl   ClusterIP   None            <none>        5432/TCP            3m44s

```
Create Postgres client 
```
[opc@bastion streaming]$  kubectl run pg-release-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:16.0.0-debian-11-r13 --env="PGPASSWORD=$POSTGRES_PASSWORD"  --command -- psql --host pg-release-postgresql -U postgres -d postgres -p 5432
If you don't see a command prompt, try pressing enter.

postgres=#
```

2- Install APICUR (https://www.apicur.io) on OKE
Create following namespace and deployment in OKE

```
kubectl create namespace apicur

vi apicur-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apicur-deployment
  namespace: apicur
  labels:
    app: apicur
spec:
  replicas: 1
  selector:
    matchLabels:
      app: apicur
  template:
    metadata:
      labels:
        app: apicur
    spec:
      containers:
      - name: apicur
        image: apicurio/apicurio-registry-jpa:latest
        ports:
        - containerPort: 8080
        env:
        - name: QUARKUS_DATASOURCE_USERNAME
          value: postgres
        - name: QUARKUS_DATASOURCE_PASSWORD
          value: GfSXdxXd6C
        - name: QUARKUS_DATASOURCE_URL
          value: jdbc:postgresql://pg-release-postgresql.default.svc.cluster.local:5432/postgres
---
apiVersion: v1
kind: Service
metadata:
  name: apicur-service
  namespace: apicur
spec:
  type: NodePort
  selector:
    app: apicur
  ports:
    - port: 8080[
      targetPort: 8080
      nodePort: 30100

```
Get list of artifacts 

```
curl -X GET -H "Content-type: application/json" http://172.16.1.125:30100/api/artifacts
```

Create sample schema
```
[opc@bastion streaming]$ curl -X POST -H "Content-type: application/json; artifactType=JSON" -H "X-Registry-ArtifactId: iotDeviceTemprature" --data '{"deviceId":"100","deviceLocation":"inventory","deviceTemp":"20"}' http://172.16.1.125:30100/api/artifacts
{"createdOn":1698567297781,"modifiedOn":1698567297781,"id":"iotDeviceTemprature","version":1,"type":"JSON","globalId":1,"state":"ENABLED"}

[opc@bastion streaming]$ curl -X GET -H "Content-type: application/json" http://172.16.1.125:30100/api/artifacts
["iotDeviceTemprature"]

[opc@bastion streaming]$ curl -X GET -H "Content-type: application/json" http://172.16.1.125:30100/api/artifacts/iotDeviceTemprature
{"deviceId":"100","deviceLocation":"inventory","deviceTemp":"20"}
```
Update artifact
```
[opc@bastion streaming]$ curl -X PUT -H "Content-type: application/json; artifactType=JSON" --data '{"deviceId":"100","deviceLocation":"inventory","deviceTemp":"20", "timestamp":"2023-10-29 19:24:08"}' http://172.16.1.125:30100/api/artifacts/iotDeviceTemprature
{"createdOn":1698567297781,"modifiedOn":1698567977065,"id":"iotDeviceTemprature","version":3,"type":"JSON","globalId":11,"state":"ENABLED"}

[opc@bastion streaming]$ curl -X GET -H "Content-type: application/json" http://172.16.1.125:30100/api/artifacts/iotDeviceTemprature
{"deviceId":"100","deviceLocation":"inventory","deviceTemp":"20", "timestamp":"2023-10-29 19:24:08"}
```

3- Provison OSS )OCI Streaming Service)

Create stream instance

<img width="1623" alt="image" src="https://github.com/omidizadkhasti/oci-streaming/assets/79064307/8641d78e-9369-46cc-a543-8646f5cd3949">

Create Kafka Connect Configuration for Stream instance

<img width="1064" alt="image" src="https://github.com/omidizadkhasti/oci-streaming/assets/79064307/6a03a74d-328f-4c6e-a024-129037ceeb6e">

instalkl confluent-kafka python libraries.

```
python3.9 -m pip install confluent-kafka
Defaulting to user installation because normal site-packages is not writeable
Collecting confluent-kafka
  Downloading confluent_kafka-2.3.0-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (4.0 MB)
     |████████████████████████████████| 4.0 MB 43.1 MB/s
Installing collected packages: confluent-kafka
Successfully installed confluent-kafka-2.3.0
```

Create sample producer python script

```
from confluent_kafka import Producer

producer_conf = {'bootstrap.servers': 'lsrdtszyacea.streaming.ap-melbourne-1.oci.oraclecloud.com:9092'}
sasl_conf = {'security.protocol':'SASL_SSL','sasl.mechanism':'PLAIN','sasl.username':'apaccpt03/oracleidentitycloudservice/omid.izadkhasti@oracle.com/ocid1.streampool.oc1.ap-melbourne-1.amaaaaaap77apcqa7t4whz6xuhv33f6xsul2dkdn3ewmxbs3lsrdtszyacea','sasl.password':'r6Ubv{j<rZNn+<vf9v<M'}

producer_conf.update(sasl_conf)
print(producer_conf)

producer = Producer(producer_conf)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

data = '{"messageId":100,"message":"test message"}'
producer.produce('mytopic', data.encode('utf-8'), callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
producer.flush()

[opc@bastion streaming]$ python3.9 producer.py
{'bootstrap.servers': 'lsrdtszyacea.streaming.ap-melbourne-1.oci.oraclecloud.com:9092', 'security.protocol': 'SASL_SSL', 'sasl.mechanism': 'PLAIN', 'sasl.username': 'apaccpt03/oracleidentitycloudservice/omid.izadkhasti@oracle.com/ocid1.streampool.oc1.ap-melbourne-1.amaaaaaap77apcqa7t4whz6xuhv33f6xsul2dkdn3ewmxbs3lsrdtszyacea', 'sasl.password': 'r6Ubv{j<rZNn+<vf9v<M'}

%5|1698630950.589|PARTCNT|rdkafka#producer-1| [thrd:main]: Topic mytopic partition count changed from 1 to 0
Message delivered to mytopic [0]
```
sample consumer python script
```
from confluent_kafka import Consumer

consumer_conf = {'bootstrap.servers': 'lsrdtszyacea.streaming.ap-melbourne-1.oci.oraclecloud.com:9092',
                 'group.id': 'mygroup',
                 'auto.offset.reset': 'earliest'
                }
sasl_conf = {'security.protocol':'SASL_SSL','sasl.mechanism':'PLAIN','sasl.username':'apaccpt03/oracleidentitycloudservice/omid.izadkhasti@oracle.com/ocid1.streampool.oc1.ap-melbourne-1.amaaaaaap77apcqa7t4whz6xuhv33f6xsul2dkdn3ewmxbs3lsrdtszyacea','sasl.password':'r6Ubv{j<rZNn+<vf9v<M'}

consumer_conf.update(sasl_conf)

consumer = Consumer(consumer_conf)

consumer.subscribe(['mytopic'])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

consumer.close()

[opc@bastion streaming]$ python3.9 consumer.py
Received message: {"messageId":100,"message":"test message"}
```


4-
