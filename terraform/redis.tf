resource "docker_image" "redis" {
  name = "redis:7-alpine"
}

resource "docker_container" "ledger_redis" {
  name  = "ledger-redis-tf"
  image = docker_image.redis.image_id

  ports {
    internal = 6379
    external = 6380  
  }
}