**About**
This blockchain project was done as part of "Python, JS & React | Build a Blockchain & Cryptocurrency" course by David Joseph Katz, you can check the course at: https://www.udemy.com/course/python-js-react-blockchain/?couponCode=ST21MT121624

--------------------------------------------------------------------------------------------------------------------------------------------

**Activate the virtual environment**

```
.\blockchain-env\Scripts\activate
```

**Install all packages**

```
pip3 install -r requirements.txt
```

**Running modules**

```
To run modules use the -m commando and . instead of /, eg.:
python3 -m backend.blockchain.block
```

**TODO**
```
-> create another function that changes the hash based in the given order
-> use the "^" instead of "" to avoid generating same hashs in different values
```

**Run the tests**

Make sure to activate the virtual environment.

```
python -m pytest backend/tests
```

**Run the application and API**

Make sure to activate the cirtual environment.

```
python -m backend.app
```

**Run a peer insntance**

Make sure to activate the virtual environment.

´´´
set PEER=True
python -m backend.app
´´´

**Run the frontend**

In the frontend directory:

´´´
npm run start
´´´

**Seed the backend with data**

Make sure to activate the virtual environment.

```
set SEED_DATA=True
python -m backend.app
```
