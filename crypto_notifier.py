""""
    Just a simple program to email whoever/SMS email.
    Just modify the recipient
"""

import smtplib
import secrets
                
def sendEmail():
    
    email = secrets.GMAIL                    # your email
    password = secrets.G_PASS                # IF 2FA then input your generated email application password
    host = 'smtp.gmail.com'                 # SMTP server of your email provider
    port = '587'                            # SMTP port
    rcpt = secrets.RCPT 

    #rcpt = input("Enter in recipients address: ") 

    message = input("Enter in your message: ")

    # Sending Process
    try:

        server = smtplib.SMTP(host, port)

    except OSError:         # Note to self socket.error is merged as OSError now

        print("Hostname or port is incorrect...")
        server = None

    if server is not None:
        
        server.starttls()                   # TLS encrypt the connection
        
        try:

            login = server.login(email, password)

        except smtplib.SMTPAuthenticationError:

            print("Invalid login credentials, may need to create 'App Password in email settings'...")
            login = None

        # Secure the connection

        if login is not None:

            try:    

                server.sendmail(email,rcpt,message)
                print('Message Sent')
                server.quit()

            except smtplib.SMTPRecipientsRefused:

                print("Check recipients email...")
        else:

            print("Exiting...")
    else:

        print("Exiting...")

def startProgram():
    
    sendEmail()

def main():

    startProgram()

if __name__=="__main__":

    main()
    
