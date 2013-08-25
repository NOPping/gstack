from pyoauth2.provider import AuthorizationProvider

class CloudstackAuthorizationProvider(AuthorizationProvider):

    def validate_client_id(self, client_id):
        return True

    def validate_client_secret(self, client_id, client_secret):
        return True

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True
    
    def validate_access(self):
        return True

    def validate_scope(self, client_id, scope):
        return True

    def persist_authorization_code(self, client_id, code, scope):
        print 'persist authorization code'

    def persist_token_information(self, client_id, scope, access_token, token_type, expires_in, refresh_token, data):
        print 'persist token information'

    def from_authorization_code(self, client_id, code, scope):
        return {
            'client_id' : client_id,
            'code' : code,
            'scope' : scope,
        }

    def from_refresh_token(self, client_id, refresh_token, scope):
        return {
            'client_id' : client_id,
            'refresh_token' : refresh_token,
            'scope' : scope,
        } 

    def discard_authorization_code(self, client_id, code):
        print 'discarding auth code'

    def discard_refresh_token(self, client_id, refresh_token):
        print 'discarding refresh token'

    def discard_client_user_tokens(self, client_id, user_id):
        print 'discarding user token'