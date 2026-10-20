import json
import logging

from datetime import datetime

import redis

_LOGGER = logging.getLogger(__name__)


class RedisRepository:
    """
    abstraction layer for managaing REDIS cache memory - managing connection with Redis DB,
    inserting, listing, deleting records
    """
    def __init__(self, _host: str, _port: int, _db: int):
        self._host = _host
        self._port = _port
        self._db = _db
        self._redis = self._connect()


    def __del__(self):
        if getattr(self, "_redis", None) is not None:
            self._redis.close()


    def _connect(self):
        _redis = redis.Redis(self._host, self._port, self._db)
        try:
            _redis.ping()
        except redis.exceptions.ConnectionError:
            _LOGGER.error("ERROR: [] Can not connect to DB")
            return None
        except redis.exceptions.TimeoutError:
            _LOGGER.error("ERROR: [] Connection timeout reached out")
            return None
        return _redis


    def get(self, pattern: str):
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            return None
        return self._redis.get(pattern)


    def get_keys(self, pattern: str):
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            return []

        keys = []
        cursor = 0
        while True:
            cursor, batch = self._redis.scan(cursor=cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        return keys


    def set(self, key: str, value: dict):
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            print("ERROR: could not reach to redis before set operation")
            return None

        if self._set(key, str(json.dumps(value))):
            return value
        return None


    def _set(self, key: str, value: dict):
        
        memory_error_msg = "ERROR during set operation [{}]: DB is out of memory"
        timeout_error_msg = "ERROR during set operation [{}]: timeout reached out"
        general_redis_error_msg = "ERROR during set operation: [{}]: Error occured in Redis"
        
        if self._redis is None:
            return False
        operation_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self._redis.set(key, value)
        except redis.exceptions.OutOfMemoryError:
            _LOGGER.error(memory_error_msg.format(operation_date))
            print(memory_error_msg.format(operation_date))
            return False
        except redis.exceptions.TimeoutError:
            print(timeout_error_msg.format(operation_date))
            _LOGGER.error(timeout_error_msg.format(operation_date))
            return False
        except redis.exceptions.RedisError:
            print(general_redis_error_msg.format(operation_date))
            _LOGGER.error(general_redis_error_msg.format(operation_date))
            return False
        
        return True


    def delete(self, pattern: str):
        
        operation_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            print(general_redis_error_msg.format(operation_date))
            _LOGGER.error(general_redis_error_msg.format(operation_date))
            return 0

        total_deleted = 0
        cursor = 0
        while True:
            cursor, keys = self._redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                total_deleted += self._redis.delete(*keys)
            if cursor == 0:
                break
        return total_deleted


    def hset(self, key, mapping):
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            return None
        return self._redis.hset(key, mapping=mapping)


    def hgetall(self, key):
        if self._redis is None:
            self._redis = self._connect()
        if self._redis is None:
            return None
        return self._redis.hgetall(key)
