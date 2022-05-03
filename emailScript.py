import smtplib

def send_notification(message, recipient="sebastianag2002@gmail.com"):

    message = "plant moisture levels are low, water in a few days"
    sender = "sebastiandeveloperemail@gmail.com"
    password = "Pikachu44!"

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.sendmail(sender, recipient, message)
    server.quit()

if __name__ == "__main__":
    #send_notification("plant moisture levels are low, remember to water slightly!")
    pass
