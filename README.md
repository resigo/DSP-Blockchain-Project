# DSP Blockchain Project
Proof of concept of Linked Data modelled into the Blockchain.

## Run the Application
The repository has an application and back-end part, which runs on two different ports.

To run the application on port 5000 and connect it to the back-end at 8000, run the following commands in terminal:
> python run_app.py 5000 8000

Now, the back-end needs to be started. Open different terminal window and insert:

> set FLASK_APP=node_server.py
> python -m flask run --port 8000

## Run on Distributed Network
To add more servers into the network, follow steps in **Run the application** in the different terminals to simulate multiple servers.

Then connect the existing servers with vice-versa pair of cURL commands:
> curl -X POST http://localhost:8001/register_with  -d "{\\"node_address\\": \\"http://localhost:8000\\"}" -H "Content-Type:application/json"

## Original Code
The PoC blockchain code is built on top of the IBM Blockchain tutorial (https://github.com/satwikkansal/python_blockchain_app/tree/ibm_blockchain_post)
