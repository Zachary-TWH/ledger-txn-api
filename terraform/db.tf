resource "docker_image" "postgres" {
  name = "postgres:16"
}

resource "docker_container" "ledger_db" {
  name  = "ledger-db-tf"
  image = docker_image.postgres.image_id

  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=localtest",
    "POSTGRES_DB=ledger"
  ]

  ports {
    internal = 5432
    external = 5433  # different port than your compose db, to avoid clashing
  }
}