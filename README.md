
```markdown
# Credit Approval System  API

Credit Approval System  API is a Django application that provides RESTful APIs for managing customer loans.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Gulshan256/credit-approval-system-api.git
   ```

2. Navigate to the project directory:

   ```bash
   cd loan-management-api
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Apply migrations:

   ```bash
   python manage.py migrate
   ```

## Usage

### Start the Development Server

```bash
python manage.py runserver
```

The API will be accessible at `http://127.0.0.1:8000/`.

### Available Endpoints

- **Register Customer:**
  `POST /register-customer`
  
  Request Body:

  ```json
  {
    "first_name ": "John",
    "last_name": "Doe",
    "age" :21,
    "monthly_income": 100000,
    "phone_number": 1234567890
    }


- **View Loan Details:**
  `GET /view-loan/<loan_id>`

- **View Loans by Customer ID:**
  `GET /view-loans/<customer_id>`

- **Check Eligibility:**
  `POST /check-eligibility`

  Request Body:

  ```json
  {
    "customer_id": 123,
    "loan_amount": 100000,
    "interest_rate": 15,
    "tenure": 12
  }
  ```

- **Create Loan:**
  `POST /create-loan`

  Request Body:

  ```json
  {
    "customer_id": 123,
    "loan_amount": 100000,
    "interest_rate": 15,
    "tenure": 12
  }
  ```

## API Documentation

For detailed API documentation, visit [API Documentation](#).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

Replace placeholders like `your-username` with your actual username. Additionally, add specific information about your API documentation if it's generated and hosted elsewhere. Adjust the content to fit your project structure and details.