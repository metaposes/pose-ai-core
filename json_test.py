import redis
import math
Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, max_connections=10, decode_responses=True)
r = redis.Redis(connection_pool=Pool)
print(r.hgetall('squat' + str(0)))
print(r.hgetall('squat' + str(1)))
print(r.hlen('squat1'))
print(r.keys('squat*'))
print(math.degrees(math.atan2(1, -1)))