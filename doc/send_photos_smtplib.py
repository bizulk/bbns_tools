#!/usr/bin/env python3

# code récupéré de ce [tutoriel](https://www.geeksforgeeks.org/send-mail-gmail-account-using-python/)
# simple mais ne marche pas car Google bloque les API qui ne son pas les siennes.
import smtplib 

# Compte expéditeur 
# todo : demander de le saisir
_sender_id="planningbbns@gmail.com"
_sender_pass="P@ssW0rd!"
_smtp_server='smtp.gmail.com'

# list of email_id to send the mail 
_lDest = ["selso.liberado@gmail.com" ] 
# Message to send
message = '''Bonjour, 
			Ci-joint la photo réalisée lors de la séance bébé nageur stéphanois,
			Bonne année !'''
	
for dest in _lDest: 
	s = smtplib.SMTP(_smtp_server, 587) 
	s.starttls() 
	s.login(_sender_id, _sender_pass) 
	s.sendmail(_sender_id, dest, message) 
	s.quit() 
