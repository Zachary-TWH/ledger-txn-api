resource "kubernetes_deployment" "api" {
  metadata {
    name = "api"
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "api"
      }
    }

    template {
      metadata {
        labels = {
          app = "api"
        }
      }

      spec {
        container {
          name              = "api"
          image             = "ghcr.io/zachary-twh/ledger-txn-api:latest"
          image_pull_policy = "Always"

          port {
            container_port = 8000
          }

          env {
            name  = "DATABASE_URL"
            value = "postgresql://postgres:localtest@postgres:5432/ledger"
          }
          env {
            name  = "REDIS_HOST"
            value = "redis"
          }
          env {
            name  = "RABBITMQ_URL"
            value = "amqp://guest:guest@rabbitmq:5672//"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "api" {
  metadata {
    name = "api"
  }

  spec {
    type = "NodePort"

    selector = {
      app = "api"
    }

    port {
      port        = 8000
      target_port = 8000
    }
  }
}