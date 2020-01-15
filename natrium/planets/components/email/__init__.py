import zmail
from conf import config

emailer = zmail.server(**config['natrium']['email']['args'])

