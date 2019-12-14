from natrium import cache_pool
from conf import config
from natrium.util.objective_dict import ObjectiveDict

Config = ObjectiveDict(config)

cache_pool.setup({
    "natrium.tokens": {
        "default_expire_delta": Config.natrium.token_expire
    }, # 令牌
    "natrium.authenticate.verify.locks": { 
        "default_expire_delta": {
            "seconds": 1
        }
    }, # 验证提交凭据时的冷却限制,
    "natrium.tokens.danger.abandoned": {}
})
TokenBucket = cache_pool.getBucket("natrium.tokens")
VerifyLocks = cache_pool.getBucket("natrium.authenticate.verify.locks")