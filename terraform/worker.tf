resource "kubernetes_deployment" "worker" {
  metadata {
    name = "worker"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "worker"
      }
    }

    template {
      metadata {
        labels = {
          app = "worker"
        }
      }

      spec {
        container {
          name              = "worker"
          image             = "ghcr.io/zachary-twh/ledger-txn-api:latest"
          image_pull_policy = "Always"
          command           = ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]

          env {
            name  = "DATABASE_URL"
            value = "postgresql://postgres:localtest@postgres:5432/ledger"
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