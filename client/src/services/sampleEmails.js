// Sample emails for quick testing (as required by the spec).

export const SAMPLE_EMAILS = [
  {
    id: 'safe-business',
    label: 'Safe business email',
    tag: 'SAFE',
    subject: 'Q3 budget review — Tuesday 10:00 AM',
    sender: 'sarah.chen@acmecorp.com',
    body: `Hi Team,

This is a reminder that our Q3 budget review meeting is scheduled for Tuesday at 10:00 AM in Conference Room B. Please bring your updated department forecasts and the cost-savings summary we discussed last week.

The agenda is attached to the calendar invite. If you have any conflicts, let me know before end of day Monday so we can adjust.

Thanks,
Sarah Chen
Finance Manager, Acme Corp`,
  },
  {
    id: 'promo-spam',
    label: 'Promotional spam',
    tag: 'SPAM',
    subject: 'ACT NOW!! Unbelievable Deals Inside — 90% OFF!!!',
    sender: 'deals@bargain-blast-newsletter.biz',
    body: `Dear Customer,

You have been specially selected to receive an EXCLUSIVE 90% discount on all our products! This offer EXPIRES SOON so hurry and click the link below to claim your reward.

Click here: http://amazing-deals-4u.top/special-offer

Don't miss this once-in-a-lifetime opportunity. Limited stock available!

Unsubscribe here if you no longer wish to receive these messages.`,
  },
  {
    id: 'prize-scam',
    label: 'Prize / lottery scam',
    tag: 'SPAM',
    subject: 'CONGRATULATIONS! You have WON $5,000,000 USD',
    sender: 'claims@international-lottery-winners.com',
    body: `CONGRATULATIONS!!!

We are pleased to inform you that your email address has been selected as the WINNER of the International Lottery draw held this month. You have won $5,000,000 USD!

To claim your prize, you must confirm your details immediately. Please reply with your full name, address, phone number and bank account details so we can transfer your winnings.

Please treat this as URGENT. Your prize will expire within 48 hours if you do not respond.

Sincerely,
Dr. John Walker
Claims Department`,
  },
  {
    id: 'bank-phishing',
    label: 'Bank phishing email',
    tag: 'POSSIBLE PHISHING',
    subject: 'URGENT: Your account has been suspended',
    sender: 'security@securebank-alerts.com',
    body: `Dear Valued Customer,

We have detected unusual activity on your account and have temporarily SUSPENDED your access for your protection.

To verify your identity and restore access, you must confirm your account information within 24 hours. Failure to do so will result in permanent termination of your account.

Please click the link below to verify your account immediately:
http://83.102.44.9/securebank/verify

You will be asked to enter your username, password and credit card number for verification purposes.

Security Team
Secure Bank`,
  },
  {
    id: 'password-phishing',
    label: 'Password reset phishing',
    tag: 'POSSIBLE PHISHING',
    subject: 'Action Required: Verify your email password',
    sender: 'it-helpdesk@webmail-verify-service.net',
    body: `Dear User,

We are upgrading our email security systems. As part of this process, all users are required to verify their account to prevent it from being DEACTIVATED.

Please log in and confirm your password immediately using the link below:
https://bit.ly/verify-webmail-account

Warning: Accounts that fail to verify within 24 hours will be permanently locked.

Thank you for your cooperation.
IT Helpdesk`,
  },
  {
    id: 'job-scam',
    label: 'Job / money-mule scam',
    tag: 'SPAM',
    subject: 'Earn $500 per week working from home — No experience needed!',
    sender: 'hr@remote-jobs-offers-now.com',
    body: `Hello,

We found your resume online and believe you would be a perfect fit for our remote position. You can earn $500 - $1500 per week working just a few hours from home. No experience required!

As part of the role, you will receive payments into your bank account and transfer the funds to our clients. You keep a generous commission.

To get started, reply with your bank account details so we can process your first assignment.

This opportunity is limited — apply today!

Best regards,
Recruitment Team`,
  },
  {
    id: 'delivery-scam',
    label: 'Delivery / customs scam',
    tag: 'POSSIBLE PHISHING',
    subject: 'Your package is on hold — customs fee required',
    sender: 'notifications@parcel-tracking-service.top',
    body: `Dear Customer,

We attempted to deliver your package but it is currently on hold due to an unpaid customs fee of $3.49.

To release your package, please pay the outstanding fee by clicking the link below within 48 hours:
http://parcel-tracking-service.top/pay-fee

If the fee is not paid, your package will be returned to the sender and additional charges will apply.

Track your parcel now!
Customer Support`,
  },
]
