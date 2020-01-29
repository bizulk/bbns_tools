#!/usr/bin/env python3
# __author__ Selso LIBERADO
# todo : utiliser log, argument et mdp en cli,
# Ce script permet d'envoyer les photos des animations aux parents
# les mails et fichier de photos sont dans un fichier excel (ods)

# Voir la zone paramétrage pour les envois

# Ci-dessous toutes les dépendances pour gmail
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import base64
from apiclient import errors, discovery
import mimetypes


import pdb
import time
from pathlib import Path
import os
import sys

###############################################################################
# Paramétrage :

# Pour tester le script et avoir le log de l'envoi qui sera réalisé
DONT_SEND_MAIL = True

# nom du fichier contenant la liste des photos XLSX or ODS
FILE_INPUT = "..\\20191229_BBNS_ListePresence_mail.xlsx"

# TODO : importer le get_data depuis le bon module en fonction de l'extension
if Path(FILE_INPUT).suffix == ".ods":
    from pyexcel_ods import get_data
else:
    from pyexcel_xlsx import get_data

# Sheet name
FILE_SHEET = "Sheet1"
# Colonne contenant l'email
COL_MAIL = "Parents::Email"
# Colonne contenant les numéros de photos (séparés par une virgule)
COL_PHOTO = "no photo"

# Chemin vers les photos à adapter selon votre cas
PHOTO_PATH = "/Users/selsoliberado/Downloads/PHOTOS_NOEL_BBN_2018/"

MAIL_BODY = """Bonjour,
			Ci-joint une photo prise lors de la séance Bébé Nageur Stéphanois, au gouter de noël.
			Nous vous souhaitons Bonne année.
			L'équipe des BBNS. 
			"""
MAIL_SUBJECT = "Bébé Nageurs Stéphanois : photo du gouter de noël"

###############################################################################
# CONSTANTES
#  gmail : autorisation If modifying these scopes, delete the file token.json.
SCOPES = "https://www.googleapis.com/auth/gmail.send"


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

  Args:
	sender: Email address of the sender.
	to: Email address of the receiver.
	subject: The subject of the email message.
	message_text: The text of the email message.

  Returns:
	An object containing a base64url encoded email object.
	"""
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {"raw": raw}


###############################################################################
def send_message(service, user_id, message):
    """Send an email message.

  Args:
	service: Authorized Gmail API service instance.
	user_id: User's email address. The special value "me"
	can be used to indicate the authenticated user.
	message: Message to be sent.

  Returns:
	Sent Message.
	"""
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print("Message Id:", message["id"])
        return message
    except errors.HttpError as error:
        print("An error occurred:", error)
        return None


###############################################################################
def create_message_with_attachment(sender, to, subject, message_text, file):
    """Create a message for an email.

  Args:
	sender: Email address of the sender.
	to: Email address of the receiver.
	subject: The subject of the email message.
	message_text: The text of the email message.
	file: The path to the file to be attached.

  Returns:
	An object containing a base64url encoded email object.
	"""
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
        main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        fp = open(file, "rb")
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == "image":
        fp = open(file, "rb")
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == "audio":
        fp = open(file, "rb")
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, "rb")
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(msg)

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
    return {"raw": raw}


def calc_photolist(strPhotoList):
    """ Retourne une liste de fichier photo généré à partir d'une liste
		param strPhotoList : une liste séparée par ',' des numéros de photos.
		Contient le format de fichier de l'appareil photo, à adapter au besoin
	"""
    # spliter la liste
    listNo = list( filter(None, strPhotoList.split(",") ) )
    lret = []
    for no in listNo:
        lret.append("DSCF" + no + ".JPG")
    return lret


###############################################################################
def parse_file(file):
    """ Parse le fichier d'entrée pour récupérer le mail et le nom du fichier photo
		:param file Nom du chemin vers le fichier
		:return une liste de tuple.
	"""
    lret = []
    data = get_data(file)
    # todo : faire quelques checks pour vérifier le bon format
    # on fait sauter l'entete
    # Récupérer les index des colonnes qui nous intéressent
    idx_mail = data[FILE_SHEET][0].index(COL_MAIL)
    idx_photo = data[FILE_SHEET][0].index(COL_PHOTO)

    try:
        for row in data[FILE_SHEET][1:]:
            mail = row[idx_mail]
            listPhoto = calc_photolist(row[idx_photo])
            for photo in listPhoto:
                lret.append( (mail, photo) )
    except IndexError as e:
        pdb.set_trace()
    return lret


###############################################################################
def main():
    """ Utiliser l'API google pour envoyer les mails avec photos aux parents
		On parse le fichier ods des parents pour récupérer les fichiers à envoyer
	"""
    # Début de code piqué du quickstart pour utiliser le token d'accès au service.

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)

    service = build("gmail", "v1", http=creds.authorize(Http()))

    # Creation du message pour chaque 'cliché' et envoi au parent
    liste = parse_file(FILE_INPUT)
    for idx, item in enumerate(liste):
        addr = item[0]
        photo = item[1]
        print("{2} Envoi à {0} la photo {1} : ".format(addr, photo, idx + 1), end="")
        if Path(PHOTO_PATH + photo).is_file():
            if DONT_SEND_MAIL is True:
                continue
            msg = create_message_with_attachment(
                "Bébés Nageurs Stéphanois",
                addr,
                MAIL_SUBJECT,
                MAIL_BODY,
                PHOTO_PATH + photo,
            )
            if send_message(service, "planningbbns@gmail.com", msg) is not None:
                print("OK")
                # on attend un peu juste par précaution vis à vis du serveur de mail
                time.sleep(0.5)
            else:
                print("Erreur d'envoi")
        else:
            print("Erreur le fichier n'existe pas, on passe au suivant")
        # On force l'affichage de la ligne
        sys.stdout.flush()


###############################################################################
if __name__ == "__main__":
    main()
