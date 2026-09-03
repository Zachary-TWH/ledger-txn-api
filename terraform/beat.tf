resource "kubernetes_deployment" "beat" {
  metadata {
    name = "beat"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "beat"
      }
    }

    template {
      metadata {
        labels = {
          app = "beat"
        }
      }

      spec {
        container {
          name              = "beat"
          image             = "ghcr.io/zachary-twh/ledger-txn-api:latest"
          image_pull_policy = "Always"
          command           = ["celery", "-A", "app.celery_app", "beat", "--loglevel=info"]


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