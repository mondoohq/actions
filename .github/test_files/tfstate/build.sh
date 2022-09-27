#!/bin/sh
terraform init
terraform plan -out plan
terraform apply plan
terraform show -json plan > plan.json
terraform show -json terraform.tfstate > state.json 