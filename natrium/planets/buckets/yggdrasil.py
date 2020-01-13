from natrium.planets.buckets import cache_pool
from conf import config

cache_pool.setup({
    "yggdrasil.authserver.user.verify.cooldown": {
        "default_expire_delta": {
            "seconds": 0.5
        }
    },
    "yggdrasil.authserver.authenticate.token_pool": {
        "default_expire_delta": config['token']['validate']['maya-configure']
    },
    "yggdrasil.sessionserver.joinserver": {
        "default_expire_delta": {
            "seconds": 30
        }
    }
})
user_auth_cooling_bucket = cache_pool.getBucket("yggdrasil.authserver.user.verify.cooldown")
auth_token_pool = cache_pool.getBucket("yggdrasil.authserver.authenticate.token_pool")
session_server_join = cache_pool.getBucket("yggdrasil.sessionserver.joinserver")