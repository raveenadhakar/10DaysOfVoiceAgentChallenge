# Fraud Alert Voice Agent

A professional voice agent that handles fraud detection calls for SecureBank, verifying suspicious transactions with customers.

## Overview

The Fraud Alert Agent simulates a bank's fraud detection department calling customers about suspicious transactions. It follows a secure verification process and updates case status based on customer responses.

## Features

- **Professional Persona**: Calm, reassuring fraud detection representative
- **Secure Verification**: Uses security questions (never asks for PINs or full card numbers)
- **Transaction Details**: Reads out suspicious transaction information
- **Case Management**: Updates fraud case status in database
- **Multiple Outcomes**: Handles confirmed safe, confirmed fraud, and verification failure scenarios

## Database Structure

The agent uses `fraud_cases.json` to store fraud cases:

```json
{
  "fraud_cases": [
    {
      "userName": "John",
      "securityIdentifier": "12345",
      "cardEnding": "4242",
      "transactionAmount": "$1,247.99",
      "transactionName": "ABC Industry",
      "transactionTime": "November 26, 2025 at 11:42 PM",
      "transactionCategory": "e-commerce",
      "transactionSource": "alibaba.com",
      "transactionLocation": "Shanghai, China",
      "securityQuestion": "What is your mother's maiden name?",
      "securityAnswer": "Smith",
      "status": "pending_review",
      "outcome": null
    }
  ]
}
```

## Call Flow

1. **Introduction**: Agent introduces itself as SecureBank's Fraud Detection Department
2. **Load Case**: Agent asks for customer name and loads their fraud case
3. **Verification**: Agent asks security question to verify identity
4. **Transaction Details**: If verified, agent reads out suspicious transaction details
5. **Confirmation**: Agent asks if customer made the transaction
6. **Resolution**: 
   - If customer confirms → Mark as "confirmed_safe"
   - If customer denies → Mark as "confirmed_fraud", block card, initiate dispute
   - If verification fails → Mark as "verification_failed", advise to contact bank

## Available Functions

### `load_fraud_case_by_username(user_name: str)`
Loads a fraud case from the database by customer name.

### `verify_customer_identity(answer: str)`
Verifies customer identity using their security answer.

### `record_transaction_confirmation(customer_made_transaction: bool)`
Records whether the customer confirms or denies making the transaction.

### `get_case_status()`
Returns the current status of the fraud case.

### `end_fraud_call()`
Ends the call with appropriate closing based on case status.

## Case Statuses

- **pending_review**: Initial state, awaiting customer verification
- **verification_failed**: Customer failed identity verification
- **confirmed_safe**: Customer confirmed the transaction as legitimate
- **confirmed_fraud**: Customer denied the transaction, card blocked

## Running the Agent

### Option 1: Using Room Metadata (Recommended)

When creating a LiveKit room, set the metadata to "fraud":

```python
# In your room creation code
room = await livekit.create_room(
    name="fraud-alert-session",
    metadata="fraud"  # This tells the agent to use FraudAlertAgent
)
```

### Option 2: Modify Default Agent

Edit `backend/src/agent.py` and change the default agent type:

```python
# In the entrypoint function
agent_type = ctx.room.metadata or "fraud"  # Change default to "fraud"
```

### Option 3: Frontend Configuration

Update your frontend to specify the agent type when connecting to the room.

## Testing

Run the test suite:

```bash
cd backend
uv run pytest tests/test_fraud_agent.py -v
```

All tests should pass, covering:
- Fraud case state management
- Loading cases by username
- Identity verification (success and failure)
- Transaction confirmation (safe and fraudulent)
- Case status tracking
- Call ending scenarios

## Sample Fraud Cases

The database includes 4 sample fraud cases:

1. **John** - $1,247.99 from ABC Industry (China)
   - Security Answer: Smith
   
2. **Sarah** - $3,599.00 from Luxury Electronics (Nigeria)
   - Security Answer: Boston
   
3. **Michael** - $899.50 from Premium Fashion (Russia)
   - Security Answer: Buddy
   
4. **Emily** - $2,150.00 from International Travel (Thailand)
   - Security Answer: Blue

## Security Best Practices

✅ **DO:**
- Use security questions for verification
- Mask card numbers (show only last 4 digits)
- Provide clear next steps
- Log all case updates

❌ **DON'T:**
- Ask for full card numbers
- Request PINs or passwords
- Store sensitive authentication data
- Make medical or legal claims

## Example Conversation

```
Agent: Hello, this is Alex from SecureBank's Fraud Detection Department. 
       I'm calling about a suspicious transaction on your account. 
       May I have your name please?

Customer: This is John.

Agent: Thank you, John. I have your case pulled up. For security purposes, 
       I need to verify your identity before we proceed. 
       What is your mother's maiden name?

Customer: Smith.

Agent: Thank you for verifying your identity. Now, let me tell you about 
       the suspicious transaction we detected. On November 26, 2025 at 
       11:42 PM, we noticed a charge of $1,247.99 to ABC Industry from 
       Shanghai, China. The transaction was made through alibaba.com for 
       e-commerce. Did you make this purchase?

Customer: No, I didn't make that purchase.

Agent: I understand, and I'm sorry this happened to you. For your protection, 
       I'm taking immediate action. I've blocked your card ending in 4242 
       to prevent any further unauthorized charges. We're initiating a 
       dispute for the $1,247.99 charge, and you should see that amount 
       credited back to your account within 5-7 business days. A new card 
       will be sent to your address on file within 3-5 business days. 
       You will not be held responsible for this fraudulent charge. 
       Is there anything else you'd like me to clarify?
```

## Integration with Frontend

The agent sends real-time updates via data channel:

```typescript
// Listen for fraud updates
room.on('dataReceived', (data) => {
  const message = JSON.parse(data);
  if (message.type === 'fraud_update') {
    // Update UI with fraud case details
    updateFraudDisplay(message.data);
  }
});
```

## Troubleshooting

**Issue**: Agent doesn't load fraud case
- **Solution**: Verify `fraud_cases.json` exists in backend directory
- **Solution**: Check that username matches exactly (case-insensitive)

**Issue**: Verification always fails
- **Solution**: Check security answer matches exactly (case-insensitive, trimmed)

**Issue**: Database not updating
- **Solution**: Ensure write permissions for `fraud_cases.json`
- **Solution**: Check logs for save errors

## Future Enhancements

- [ ] Support for multiple fraud cases per customer
- [ ] DTMF input for phone keypad responses
- [ ] SMS verification codes
- [ ] Integration with real fraud detection systems
- [ ] Multi-language support
- [ ] Voice biometric verification
- [ ] Real-time fraud scoring
- [ ] Telephony integration with LiveKit Telephony

## License

This is a demo/educational implementation. Do not use with real customer data or in production without proper security review.
