terraform {
  required_providers {
    mock = {
      source  = "mocknetwork/mock/mock"
      version = "1.0.0"
    }
  }
}

provider "mock" {}

resource "mock_network_resource" "example" {
  name = "test-virtual-network"
}

output "network_id" {
  value = mock_network_resource.example.id
}
