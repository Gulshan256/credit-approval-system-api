
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

7. Data Import
   Before starting the development server, run the following script to import data from Excle(xlsx) files:
  
   ```bash
   python import_data.py

   ```

8. To use PostgreSQL, comment out the following lines in `ApprovalHub/settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
   }
   ```

   and uncomment the following lines:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': '(databse name)',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```


9. Database Sequence Reset Note: This step is required only if you are using PostgreSQL as the database. If you are using SQLite, skip this step.

  To ensure proper auto-incrementing sequence, set the next value of the sequence:
  
   ```bash
   python manage.py dbshell
   ```
   ```bash
   SELECT setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM customer) + 1);
   SELECT setval('loan_id_seq', (SELECT MAX(id) FROM loan) + 1);
   ```
## Usage

### Start the Development Server

```bash
python manage.py runserver
```

The API will be accessible at `http://127.0.0.1:8000/`.

### Available Endpoints

- **Register Customer:**
  `POST /register/`
  
  Request Body:

  ```json
  {
    "first_name ": "Rohan",
    "last_name": "Sharma",
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

