resource "kubernetes_ingress_v1" "api" {
  metadata {
    name = "api-ingress"
    annotations = {
      "kubernetes.io/ingress.class" = "nginx"
    }
  }

  spec {
    ingress_class_name = "nginx"

    rule {
      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = "api"
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}