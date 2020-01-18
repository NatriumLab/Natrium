from conf import config
from natrium.planets.buckets import cache_pool
from natrium.util.objective_dict import ObjectiveDict

Config = ObjectiveDict(config).natrium

cache_pool.setup({
    "natrium.tokens": {
        "default_expire_delta": Config["token"]["expire"]
    }, # 令牌
    "natrium.authenticate.verify.locks": { 
        "default_expire_delta": {
            "seconds": 1
        }
    }, # 验证提交凭据时的冷却限制,
    "natrium.tokens.danger.abandoned": {},
    "natrium.authserver.validate.ipLocks": {
        "default_expire_delta": {
            "seconds": 3
        }
    },
    "natrium.mostima.register.request.ipLocks": {
        "default_expire_delta": {
            "seconds": 5
        }
    },
    "natrium.mostima.register.requests": {
        "default_expire_delta": {
            "seconds": 180
        }
    }
})
TokenBucket = cache_pool.getBucket("natrium.tokens")
VerifyLocks = cache_pool.getBucket("natrium.authenticate.verify.locks")
ValidateIpLocks = cache_pool.getBucket("natrium.authserver.validate.ipLocks")

MostimaBuckets = ObjectiveDict({
    "requestLimit": cache_pool.getBucket("natrium.mostima.register.request.ipLocks"),
    "requests": cache_pool.getBucket("natrium.mostima.register.requests")
})