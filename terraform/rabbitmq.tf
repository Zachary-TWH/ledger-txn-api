resource "docker_image" "rabbitmq" {
  name = "rabbitmq:3-management"
}

resource "docker_container" "ledger_rabbitmq" {
  name  = "ledger-rabbitmq-tf"
  image = docker_image.rabbitmq.image_id

  ports {
    internal = 5672
    external = 5673  # different from your compose rabbitmq, to avoid clashing
  }

  ports {
    internal = 15672
    external = 15673  # management UI, also offset to avoid clashing
  }
}