

# PeachPaymentsGatewayMock 

#### The following applies to `vscode` and other terminal users.
Start by creating a python runtime environment.
##### 1. Create a new Python runtime environment:
```shell
python3 -m venv venv
```

##### 2. switch to the new runtime environment with the following:
```shell
source venv/bin/activate
```

##### 3. Then install required Python libraries with:
```shell
pip install --upgrade pip; pip3 install -r requirements.txt
```

##### 4. Create a new `.env` document with:
```shell
cp env.sample .env
```
##### **Note:**
Be sure to edit values to match your environment.

##### 5. Run the server with:
```shell
flask run
```

##### You can test you api endpoint using the following example:
```shell
curl -X GET 'http://127.0.0.1:5000/v1/3ds_challenge/12345'
```

###### if successful, you can expect this json response:
```shell
{"error":"Transaction not found"}
```


##### Exit environment:
```shell
deactivate
```