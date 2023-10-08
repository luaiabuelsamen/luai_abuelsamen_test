import redis
import time

class GeoDistributedLRUCache:
    """
    GeoDistributedLRUCache - A high-performance Geo Distributed LRU cache with time expiration.

    This cache is designed to meet the requirements of Ormuco's distributed systems, including simplicity,
    resilience to network failures, real-time replication, data consistency, locality of reference,
    flexible schema support, and cache expiration.

    Usage:
    cache = GeoDistributedLRUCache("example_cache:", 3600, ["redis1.example.com", "redis2.example.com"])

    cache.set("user:123", "JohnDoe")
    result = cache.get("user:123")

    Attributes:
        cache_name (str): The prefix for all keys stored in the cache.
        ttl_seconds (int): Time to live (TTL) for cached items in seconds.
        redis_clients (list): List of Redis client instances for data replication.
    """

    def __init__(self, cache_name, ttl_seconds, redis_hosts):
        """
        Initialize a new GeoDistributedLRUCache instance.

        Args:
            cache_name (str): The cache name prefix.
            ttl_seconds (int): Time to live (TTL) for cached items in seconds.
            redis_hosts (list): List of Redis host addresses.
        """
        self.cache_name = cache_name
        self.ttl_seconds = ttl_seconds
        self.redis_clients = []
        for host in redis_hosts:
            try:
                client = redis.StrictRedis(host=host, port=6379, db=0)
                self.redis_clients.append(client)
            except Exception as e:
                print(f"Failed to connect to Redis at {host}: {str(e)}")

    def get(self, key):
        for client in self.redis_clients:
            try:
                data = client.get(self.cache_name + key)
                if data:
                    # Cache hit, update LRU
                    for r in self.redis_clients:
                        r.zadd(self.cache_name + "_lru", {key: int(time.time())})
                    return data.decode('utf-8')
            except Exception as e:
                print(f"Error accessing Redis at {client.connection_pool.connection_kwargs}: {str(e)}")
        return None

    def set(self, key, value):
        for client in self.redis_clients:
            try:
                client.set(self.cache_name + key, value)  # Change setex to set here
                client.expire(self.cache_name + key, self.ttl_seconds)  # Add expiration
            except Exception as e:
                print(f"Error accessing Redis at {client.connection_pool.connection_kwargs}: {str(e)}")

    def delete(self, key):
        """
        Remove a value from the cache.

        Args:
            key (str): The key to delete from the cache.
        """
        for client in self.redis_clients:
            try:
                client.delete(self.cache_name + key)
            except Exception as e:
                print(f"Error accessing Redis at {client.connection_pool.connection_kwargs}: {str(e)}")

    def purge_expired(self):
        """
        Periodically clean up expired keys in the cache.

        This method should be called at regular intervals to remove expired cache entries.
        """
        current_time = int(time.time())
        for client in self.redis_clients:
            try:
                # Get the expired keys from the LRU sorted set
                expired_keys = client.zrangebyscore(self.cache_name + "_lru", '-inf', current_time - self.ttl_seconds)
                
                if expired_keys:
                    # Remove expired keys from the cache and LRU sorted set
                    with client.pipeline() as pipe:
                        for key in expired_keys:
                            pipe.delete(self.cache_name + key)
                        pipe.zremrangebyscore(self.cache_name + "_lru", '-inf', current_time - self.ttl_seconds)
                        pipe.execute()
            except Exception as e:
                print(f"Error accessing Redis at {client.connection_pool.connection_kwargs}: {str(e)}")

    def local_cache_size(self):
        """
        Get the size of the local cache.

        Returns:
            int: The size of the local cache.
        """
        return self.redis_clients[0].zcount(self.cache_name + "_lru", '-inf', '+inf')
