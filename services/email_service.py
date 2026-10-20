

class EmailService:
    """
    Dump class for sending email for order confirmation
    """
    SENDER_EMAIL = "noreply@example.com"
    MAIL_TEMPLATE = """\
        <html>
        <head>
            <style>
                a:link, a:visited {
                background-color: #f44336;
                color: white;
                padding: 14px 25px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                }

                a:hover, a:active {
                background-color: red;
                }
            </style>
        </head>
        <body>
            <p>Confirm the order request!</p>
            <p>
                <a href="{}">Confirm Order</a>
            </p>
        </body>
        </html>
    """

    def set_address(self, recipient: str) -> EmailService:
        """
        Sets the recipient's email address.
        """
        self.recipient = recipient
        return self

    def bind_email_template(self, link: str) -> EmailService:
        """
        Binds the provided link to the email template.
        """
        self.body = self.MAIL_TEMPLATE.format(link)
        return self


    def send_email(self) -> bool:
        """
        Simulates sending an email. In a real implementation, this would
        interface with an email server or service.
        """
        # For demonstration purposes, we'll just log the email sending.
        _LOGGER.info(f"Sending a confirmation email to {self.recipient} with subject '{self.subject}'")
        # Simulate successful email sending
        return True