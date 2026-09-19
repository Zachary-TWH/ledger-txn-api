resource "kubernetes_manifest" "api_service_monitor" {
  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "api-servicemonitor"
      namespace = "default"
      labels = {
        release = "monitoring"
      }
    }
    spec = {
      selector = {
        matchLabels = {
          app = "api"
        }
      }
      endpoints = [
        {
          port     = "http"
          path     = "/metrics"
          interval = "15s"
        }
      ]
    }
  }
}