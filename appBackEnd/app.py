from flask import Flask, request
from azure.storage.blob import BlobServiceClient, BlobClient
import json
from azure.core.exceptions import AzureError

app = Flask(__name__)

# Azure Blob Storage setup
connection_string = "DefaultEndpointsProtocol=https;AccountName=sademobankapi;AccountKey=+BuoJ/UwKfIBf9Rknb2oBO2za6Vd5GmMy07C9AgUaVQl3IdBfAuo49wJrQsrVnyaWRSPUB7s+0SA+AStEjqYZA==;EndpointSuffix=core.windows.net"
container_name = "bankdata"
blob_name = "customer.json"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# API Endpoints
@app.route('/')
def home():
    return 'Welcome to the Bank API App!'

@app.route('/api/customers/<customerId>', methods=['GET'])
def get_customer(customerId):
    print(f"Attempting to fetch customer with ID: {customerId}")

    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading blob data...")
        blob_data = blob_client.download_blob().readall()
        data = json.loads(blob_data)

        print("Blob data downloaded and parsed successfully")

        # Find the customer data by customerId
        customer_data = next((customer for customer in data if str(customer['id']) == customerId), None)

        if customer_data:
            print(f"Customer data found for ID {customerId}: {customer_data}")
            return customer_data, 200
        else:
            print(f"Customer data not found for ID: {customerId}")
            return {"message": "Customer not found"}, 404

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading existing customer data...")
        blob_data = blob_client.download_blob().readall()
        customers = json.loads(blob_data)

        print("Existing customer data downloaded successfully")

        # Fetch new customer data from request
        new_customer = request.json
        print(f"Received new customer data: {new_customer}")

        # Vulnerability: No input validation or sanitization is done
        # Add new customer to the list
        new_customer_id = max(customer['id'] for customer in customers) + 1  # Generating a new ID
        new_customer['id'] = new_customer_id
        customers.append(new_customer)

        # Update the Blob with the new customer list
        print(f"Adding new customer with ID {new_customer_id}...")
        blob_client.upload_blob(json.dumps(customers), overwrite=True)

        print("New customer added successfully")
        return {"message": "Customer created successfully", "id": new_customer_id}, 201

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 400

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

@app.route('/api/customers/<customerId>', methods=['PUT'])
def update_customer(customerId):
    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading existing customer data...")
        blob_data = blob_client.download_blob().readall()
        customers = json.loads(blob_data)

        print("Existing customer data downloaded successfully")

        # Fetch updated customer data from request
        updated_customer_data = request.json
        print(f"Received updated data for customer ID {customerId}: {updated_customer_data}")

        # Vulnerability: No authentication or authorization check
        # Vulnerability: No input validation or sanitization is done
        # Update the customer data
        customer_index = next((i for i, customer in enumerate(customers) if str(customer['id']) == customerId), None)
        
        if customer_index is not None:
            customers[customer_index].update(updated_customer_data)
            print(f"Updating customer data for ID {customerId}...")
            blob_client.upload_blob(json.dumps(customers), overwrite=True)
            print("Customer data updated successfully")
            return {"message": "Customer updated successfully"}, 200
        else:
            print(f"Customer with ID {customerId} not found")
            return {"message": "Customer not found"}, 404

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 400

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

    # Add a general catch-all return at the end of the function
    return {"message": "An unexpected error occurred"}, 500

@app.route('/api/customers/<customerId>', methods=['DELETE'])
def delete_customer(customerId):
    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading existing customer data...")
        blob_data = blob_client.download_blob().readall()
        customers = json.loads(blob_data)

        print("Existing customer data downloaded successfully")

        # Vulnerability: No authentication or authorization check
        # Delete the customer data
        customer_index = next((i for i, customer in enumerate(customers) if str(customer['id']) == customerId), None)
        if customer_index is not None:
            del customers[customer_index]

            # Update the Blob with the remaining customers
            print(f"Deleting customer data for ID {customerId}...")
            blob_client.upload_blob(json.dumps(customers), overwrite=True)

            print("Customer data deleted successfully")
            return {"message": "Customer deleted successfully"}, 200
        else:
            print(f"Customer with ID {customerId} not found")
            return {"message": "Customer not found"}, 404

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 400

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

@app.route('/api/customers/<customerId>/ssn', methods=['GET'])
def get_customer_ssn(customerId):
    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading existing customer data...")
        blob_data = blob_client.download_blob().readall()
        customers = json.loads(blob_data)

        print("Existing customer data downloaded successfully")

        # Vulnerability: No authentication or authorization check
        # Find the customer by ID and return the SSN
        customer = next((customer for customer in customers if str(customer['id']) == customerId), None)
        if customer is not None:
            ssn = customer.get('ssn')
            if ssn:
                print(f"Returning SSN for customer ID {customerId}")
                return {"ssn": ssn}, 200
            else:
                print(f"SSN not found for customer ID {customerId}")
                return {"message": "SSN not found"}, 404
        else:
            print(f"Customer with ID {customerId} not found")
            return {"message": "Customer not found"}, 404

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 400

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

@app.route('/api/customers/<customerId>/creditcards', methods=['GET'])
def get_customer_credit_cards(customerId):
    try:
        # Connect to the Azure Blob storage and retrieve the JSON data
        print("Connecting to Azure Blob Storage...")
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("Downloading existing customer data...")
        blob_data = blob_client.download_blob().readall()
        customers = json.loads(blob_data)

        print("Existing customer data downloaded successfully")

        # Vulnerability: No authentication or authorization check
        # Find the customer by ID and return the credit card information
        customer = next((customer for customer in customers if str(customer['id']) == customerId), None)
        if customer is not None:
            credit_cards = customer.get('credit_cards')
            if credit_cards:
                print(f"Returning credit card information for customer ID {customerId}")
                return {"credit_cards": credit_cards}, 200
            else:
                print(f"Credit card information not found for customer ID {customerId}")
                return {"message": "Credit card information not found"}, 404
        else:
            print(f"Customer with ID {customerId} not found")
            return {"message": "Customer not found"}, 404

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return {"message": "Invalid JSON data"}, 400

    except AzureError as e:
        print(f"An error occurred while accessing Azure Blob Storage: {e}")
        return {"message": "Failed to access Azure Blob Storage"}, 500

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"message": "Internal Server Error"}, 500

if __name__ == '__main__':
    app.run(debug=True)
