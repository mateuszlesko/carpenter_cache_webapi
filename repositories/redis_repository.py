""" build-in imports """
import json
import logging
from datetime import datetime

""" 3rd party imports """
import redis

""" internal imports """

_LOGGER = logging.getLogger(__name__)


class RedisRepository:
    """
    abstraction layer for managaing REDIS cache memory - managing connection with Redis DB,
    inserting, listing, deleting records
    """
    
    """ managed shared redis sessions context """
    __connections : dict[str, redis.Redis] = {}
    do_connections_contain = lambda key : key in __class__.__connections.keys()


    @staticmethod
    def create_instance(_conn_name : str, _host : str, _port: int, _db: int):
        redis_repo = RedisRepository()
        redis_repo._host = _host
        redis_repo._port = _port
        redis_repo._db = _db
        redis_repo._connection_name = _conn_name
        if not __class__.do_connections_contain(_conn_name):
            __class__.__connections[_conn_name] = __class__._connect(_host, _port, _db)
        
        return redis_repo


    @staticmethod
    def destruct_instance(conn_name):

        if __class__.do_connections_contain(conn_name):
            __class__.__connections.pop(conn_name, None)
            return conn_name
        else:
            return None


    @staticmethod
    def _connect(host, port, db):

        operation_time = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        connection_error_msg = "ERROR: [{}]: Can not connect to DB".format(operation_time)
        timeout_error = "ERROR: [{}]: Connection timeout reached out".format(operation_time)
        db_conn = redis.Redis(host, port, db)
        
        try:
            db_conn.ping()
        except redis.exceptions.ConnectionError:
            _LOGGER.error(connection_error_msg)
            print(connection_error_msg)
            return None
        except redis.exceptions.TimeoutError:
            _LOGGER.error(timeout_error)
            print(timeout_error)
            return None

        return db_conn

    
    def get_context(self):
        return dict( name = self._conn_name, host = self._host, port = self._port, db = self._db)


    def get_record_by_key(self, conn_name : str, pattern: str):

        if not __class__.do_connections_contain(conn_name):
            return None
  
        return __class__.__connections[conn_name].get(pattern)


    def get_keys(self, conn_name,pattern: str):

        if not __class__.do_connections_contain(conn_name):
            return []

        keys = []
        cursor = 0
        while True:
            cursor, batch = __class__.__connections[conn_name].scan(cursor=cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        return keys


    def set_record(self, conn_name : str, key : str, value : dict):

        if not __class__.do_connections_contain(conn_name):
            print("ERROR: could not get redis connection context")
            return None
  
        if self._set_record(conn_name, key, str(json.dumps(value))):
            return value
        return None


    def _set_record(self, conn_name : str, key : str, value : dict):
        
        memory_error_msg = "ERROR during set operation [{}]: DB is out of memory"
        timeout_error_msg = "ERROR during set operation [{}]: timeout reached out"
        general_redis_error_msg = "ERROR during set operation: [{}]: Error occured in Redis"
        
        operation_time = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

        try:
            __class__.__connections[conn_name].set(key, value)
        except redis.exceptions.OutOfMemoryError:
            _LOGGER.error(memory_error_msg.format(operation_time))
            print(memory_error_msg.format(operation_time))
            return False
        except redis.exceptions.TimeoutError:
            print(timeout_error_msg.format(operation_time))
            _LOGGER.error(timeout_error_msg.format(operation_time))
            return False
        except redis.exceptions.RedisError:
            print(general_redis_error_msg.format(operation_time))
            _LOGGER.error(general_redis_error_msg.format(operation_time))
            return False
        
        return True


    def delete_record(self, conn_name : str, pattern: str):
        
        operation_time = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        
        if not __class__.do_connections_contain(conn_name):
            print("ERROR [{}]: could not get redis connection context".format(operation_time))
            return None

        total_deleted = 0
        cursor = 0
        while True:
            cursor, keys = __class__.__connections[conn_name].scan(cursor=cursor, match=pattern, count=100)
            if keys:
                total_deleted += __class__.__connections[conn_name].delete(*keys)
                print("SUCCESS [{}]: deletion {}".format(operation_time, str(*keys)))
            if cursor == 0:
                break
        return total_deleted


    def hset(self, conn_name, key, mapping):

        operation_time = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

        if not __class__.do_connections_contain(conn_name):
            print("ERROR [{}]: could not get redis connection context".format(operation_time))
            return None
        return __class__.__connections[conn_name].hset(key, mapping=mapping)


    def hgetall(self, conn_name, key):

        operation_time = str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

        if not __class__.do_connections_contain(conn_name):
            print("ERROR [{}]: could not get redis connection context".format(operation_time))
            return None
        
        return __class__.__connections[conn_name].hgetall(key)
