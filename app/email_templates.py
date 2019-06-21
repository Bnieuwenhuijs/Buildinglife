import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT= 465
MAIL_USERNAME= 'buildinglife.no.reply@gmail.com'
MAIL_PASSWORD= 'r2ItgT62'


def generate_html_mail(subject, body, to_addr, from_addr):
	"""Send an HTML email using the given subject, body, etc."""

	# Create message container - the correct MIME type is multipart/alternative here!
	message = MIMEMultipart('alternative')
	message['subject'] = subject
	message['To'] = to_addr
	message['From'] = from_addr
	message.preamble = """
This message is in HTML only, which your mail reader doesn't seem to support!
"""

	# Record the MIME type text/html.
	html_body = MIMEText(body, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	message.attach(html_body)

	return message.as_string()

	# The actual sending of the e-mail
	'''
	server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
	server.login(MAIL_USERNAME, MAIL_PASSWORD)

	server.sendmail(from_addr, [to_addr], message.as_string())
	server.quit()
	'''


def read_filecontent(filename):
	with open(filename, 'r') as content_file:
		content = content_file.read()
	return content



def welcome_email_body(fullname, link):

	return """
	<meta charset="utf-8" />
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
	<meta name="viewport">
	<title>
		BuildingLife Dashboard
	</title>
	<meta content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0, shrink-to-fit=no' name='viewport' />
	<!--     Fonts and icons     -->
	<link href="https://fonts.googleapis.com/css?family=Montserrat:400,700,200" rel="stylesheet" />
	<link href="https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css" rel="stylesheet">

	<!-- CSS Files -->
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.2/css/all.min.css">
	<link rel="stylesheet" href="http://www.buildinglife.nl/static/Front_end/css/style.css">
</head>
<body>
	<div class="header-area">
		<div class="container">
			<div class="row">
				<div class="col-md-12 col-sm-12">
					<!-- Navigation -->
					<nav class="navbar navbar-default">
						<div class="navbar-header">
							<a class="navbar-brand page-scroll sticky-logo" href="index" style="padding: 2px 0px">
								<img src="http://www.buildinglife.nl/static/Front_end/img/Logo_Horizontaal2.png" style="height: 50pt; width: 200pt" >
							</a>
						</div>
					</nav>
				</div>
			</div>
		</div>
	</div>

	<div class="about-area area-padding" style="margin-top: 80px;">
		<div class="container">
			<div class="row">
				<div class="col-md-6 col-sm-6 col-xs-12">
					<div class="well-middle">
						<div class="single-well">
							<h4 class="sec-head">Congratulations %s!</h4>
							<p>
							We've successfully created your account.
							<br>
							Click <a href="%s">here</a> to confirm your email with BuildingLife!
							<br>
							<br>
							Thanks,<br>
							BuildingLife Team.</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="contact-area">
		<div class="contact-inner">
			<div class="contact-overly"></div>
				<div class="container ">
				<div class="row">
					<!-- Start contact icon column -->
					<div class="col-md-6 col-sm-6 col-xs-12">
						<div class="footer-content">
							<div class="footer-head">
								<div class="footer-logo">
									<h2><span>Building</span>Life</h2>
								</div>

								<p>Our goal is to accelerate the circularity within the construction sector. </p>
								<div class="footer-icons">
									<ul>
										<li>
											<a href="#"><i class="fab fa-facebook-square"></i></a>
										</li>
										<li>
											<a href="#"><i class="fab fa-twitter-square"></i></a>
										</li>
										<li>
											<a href="#"><i class="fab fa-pinterest-square"></i></a>
										</li>
									</ul>
								</div>
							</div>
						</div>
					</div>
					<div class="col-md-4 col-sm-4 col-xs-12">
						<div class="footer-content">
							<div class="footer-head">
								<h4>information</h4>
								<p>
									You can contact us through the following contact details.
								</p>
								<div class="footer-contacts">
									<p><span>Tel:</span> +31 624362571</p>
									<p><span>Email:</span> contact@buildinglife.nl</p>
									<p><span>Working Hours:</span> 9am-6pm</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</body>
	""" % (fullname, link)
