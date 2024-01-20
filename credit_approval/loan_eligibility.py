


def calculate_credit_score(data):
	"""
	Calculates a credit score based on loan history and activity.

	Args:
	data: A dictionary containing the following keys:
		- past_loans_paid_on_time: Percentage of past loans paid on time (0-100).
		- num_past_loans: Number of loans taken in the past.
		- current_year_loans: Number of loans taken in the current year.
		- loan_approved_volume: Loan approved volume (e.g., total amount).
		- current_loans_sum: Sum of current loan balances.
		- approved_limit: Approved credit limit.

	Returns:
	The calculated credit score (0-100).
	"""

	# Define weights for each factor
	weights = {
		"past_loans_paid_on_time": 0.4,
		"num_past_loans": 0.25,
		"current_year_loans": 0.2,
		"loan_approved_volume": 0.1,
	}

	# Score each factor
	scores = {
		"past_loans_paid_on_time": {
			100: 5,
			95: 4,
			90: 3,
			80: 2,
			0: 1,
		}.get(data["past_loans_paid_on_time"], 0),
		"num_past_loans": {
			0: 5,
			3: 4,
			6: 3,
			9: 2,
			12: 1,
		}.get(data["num_past_loans"], 1),
		"current_year_loans": {
			0: 5,
			2: 4,
			4: 3,
			6: 1,
		}.get(data["current_year_loans"], 1),
		"loan_approved_volume": {
			"High": 5,
			"Moderate": 3,
			"Low": 1,
		}.get(data["loan_approved_volume"], 1),
	}

	# Check if current loans exceed approved limit
	if data["current_loans_sum"] > data["approved_limit"]:
		return 0

	# Calculate weighted score
	weighted_score = sum(weights[factor] * scores[factor] for factor in scores)

	# Scale score to desired range (e.g., 0-100)
	score_range = 100
	score = int(weighted_score / sum(weights.values()) * score_range)

	return score




# test that the function works
data = {
	"past_loans_paid_on_time": 100,
	"num_past_loans": 10,
	"current_year_loans": 1,
	"loan_approved_volume": "High",
	"current_loans_sum": 999,
	"approved_limit": 10000,
}

# print(calculate_credit_score(data))



def calculate_monthly_installment(loan_amount, interest_rate, tenure):
	monthly_installment = round(loan_amount * (1 + interest_rate / 100) / tenure)
	return monthly_installment


def calculate_credit_score(past_loans_paid, num_loans, loan_activity_current_year, approved_volume, current_loans_sum, approved_limit):
    max_possible_num_loans=12
    max_possible_activity = 12
    max_possible_approved_volume = 1000000
    # Normalize values
    normalized_past_loans_paid = past_loans_paid / 100
    normalized_num_loans = num_loans / max_possible_num_loans
    normalized_loan_activity = loan_activity_current_year / max_possible_activity
    normalized_approved_volume = approved_volume / max_possible_approved_volume

    # Assign weights
    weight_past_loans_paid = 0.4
    weight_num_loans = 0.1
    weight_loan_activity = 0.2
    weight_approved_volume = 0.3

    # Calculate component scores
    score_past_loans_paid = normalized_past_loans_paid * weight_past_loans_paid
    score_num_loans = (1 - normalized_num_loans) * weight_num_loans
    score_loan_activity = normalized_loan_activity * weight_loan_activity
    score_approved_volume = normalized_approved_volume * weight_approved_volume

    # Check if sum of current loans > approved limit
    if current_loans_sum > approved_limit:
        final_credit_score = 0
    else:
        # Combine component scores
        final_credit_score = score_past_loans_paid + score_num_loans + score_loan_activity + score_approved_volume

    return final_credit_score *100

# print(calculate_credit_score(100, 10, 1, 100000, 999, 10000))
