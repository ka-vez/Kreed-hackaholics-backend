from langchain_core.tools import tool

accounts = {
    "2064350220": {
        "name": "Adegbite David",
        "bank": "Kuda bank"
    },
    "6176833371": {
        "name": "Jethro Daspan",
        "bank": "Fidelity Bank"
    }
}

@tool
def extra_data():
    """This is additional data on who Adegbite David is"""

    return "He is a back-end developer"

@tool
def transfer_money(receipients_account_number, receipients_bank_name, amount):
    """Transfer money to a recipient's bank account.
    
    Args:
        receipients_account_number: The 10-digit account number of the recipient
        receipients_bank_name: The name of the recipient's bank (e.g., 'Kuda bank', 'Fidelity Bank')
        amount: The amount of money to transfer (in Naira)
    
    Returns:
        A success message confirming the transfer with recipient name and amount
    """
    # Convert account number to string and remove .0 if present
    account_str = str(receipients_account_number).replace('.0', '')
    
    # Check if account exists BEFORE trying to access it
    if account_str not in accounts:
        return f"❌ Account {account_str} not found"
    
    receipients_name = accounts[account_str]['name']
    message = f"✅ N{int(amount)} Transfer to {receipients_name} - {receipients_bank_name} Successful"
    
    return message

@tool
def buy_airtime(phone_number, network, amount):
    """Purchase airtime for a phone number.
    
    Args:
        phone_number: The phone number to recharge
        network: The mobile network (e.g., 'MTN', 'Glo', 'Airtel', '9mobile')
        amount: The amount of airtime to purchase (in Naira)
    
    Returns:
        A success message confirming the airtime purchase
    """
    # Convert phone number to string and remove .0 if present
    phone_str = str(phone_number).replace('.0', '')
    message = f"✅ N{int(amount)} {network} airtime successfully sent to {phone_str}"
    return message

@tool
def buy_data(phone_number, network, amount):
    """Purchase data bundle for a phone number.
    
    Args:
        phone_number: The phone number to send data to
        network: The mobile network (e.g., 'MTN', 'Glo', 'Airtel', '9mobile')
        amount: The amount/value of data bundle to purchase (in Naira)
    
    Returns:
        A success message confirming the data purchase
    """
    # Convert phone number to string and remove .0 if present
    phone_str = str(phone_number).replace('.0', '')
    message = f"✅ N{int(amount)} {network} data bundle successfully sent to {phone_str}"
    return message

@tool
def buy_electricity(meter_number, amount):
    """Purchase electricity units for a meter.
    
    Args:
        meter_number: The electricity meter number
        amount: The amount of electricity units to purchase (in Naira)
    
    Returns:
        A success message confirming the electricity purchase
    """
    # Convert meter number to string and remove .0 if present
    meter_str = str(meter_number).replace('.0', '')
    message = f"✅ N{int(amount)} electricity units successfully loaded to meter {meter_str}"
    return message