from restful_lib import Connection, ConnectionError
from microblog_exceptions import MicroBlogMsgLimitExceeded

class FailWhale(Exception):
    def __str__(self):
        return "Oh noes, the failwhale cometh!"

TWITTER_ENDPOINT = "http://twitter.com/statuses/update.json"

class Twitter(object):
    def __init__(self, username,password):
        self._conn = Connection(TWITTER_ENDPOINT, username, password)

    def post(self, message, clip_length=False):
        if isinstance(message, list):
            # Default to a joining up the list of words with a space
            message = " ".join(message)

        if len(message)>140:
            if clip_length:
                message = message[:140]
            else:
                raise MicroBlogMsgLimitExceeded

        resp = c.request_post("", args={"status":message})

        if resp.get('headers').get('status') not in ["200", 200, "204", 204]:
            raise FailWhale
