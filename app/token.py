from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app import app


def generate_confirmation_token(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# 60*15, the link is active for 15 minutes
def confirm_token(token, expiration=900):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = serializer.loads(
			token,
			salt=app.config['SECURITY_PASSWORD_SALT'],
			max_age=expiration
		)
		return '<h1>User %s is confirmed!' % (user.username)
	except SignatureExpired:
		return '<h1>Token expired </h1>'
	except BadTimeSignature:
		return '<h1>Such token doesn\' exist! </h1>'
