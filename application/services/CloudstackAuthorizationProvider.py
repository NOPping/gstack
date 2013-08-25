from pyoauth2.provider import AuthorizationProvider

class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        """ Can we call to Cloudstack to check if a client id exists """
        return True

    def validate_client_secret(self, client_id, client_secret):
        """ Can we call to Cloudstack to see if their secret key exists
            A messy implementation of this would be to just call any user
            api command and check that it gives a successful response
        """
        return True

    def validate_redirect_uri(self, client_id, redirect_uri):
        """ Ensure the app knows the redirect_uri """
        return True
    
    def validate_access(self):
        """ Related to validation of OAuth token generation
            Not sure if important for our purposes
        """
        return True

    def validate_scope(self, client_id, scope):
        """ I see no issues in leaving this as true. We do not know what
            scope(s) GCE may use. User will be restricted access by their
            CS client key and secret anyways
        """
        return True

    def persist_authorization_code(self, client_id, code, scope):
        """ Store code with expiry """
        print 'persist authorization code'

    def persist_token_information(self, client_id, scope, access_token, token_type, expires_in, refresh_token, data):
        """ Store all token information """
        print 'persist token information'

    def from_authorization_code(self, client_id, code, scope):
        """ Return stored auth code """
        return {
            'client_id' : client_id,
            'code' : code,
            'scope' : scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        """ return stored refresh token """
        return {
            'client_id' : client_id,
            'refresh_token' : refresh_token,
            'scope' : scope,
        } 

    def discard_authorization_code(self, client_id, code):
        """ Remove auth code """
        print 'discarding auth code'

    def discard_refresh_token(self, client_id, refresh_token):
        """ Remove auth token """
        print 'discarding refresh token'

    def discard_client_user_tokens(self, client_id, user_id):
        """ remove client tokens """
        print 'discarding user token'