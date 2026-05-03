# AWS Deployment (Terraform)

Gaia deploys to AWS on a single EC2 instance using Terraform and Docker Compose.

## Related Files

-   Terraform root: `infra/terraform/`
-   EC2 resource: `infra/terraform/ec2.tf`
-   Variables: `infra/terraform/variables.tf`
-   Bootstrap: `infra/terraform/command.sh`
-   Post-provision sync: `infra/terraform/provisioners.tf`
-   Outputs: `infra/terraform/outputs.tf`
-   Make targets: `Makefile` (`tf-init`, `tf-plan`, `tf-apply`, `tf-output`, `tf-destroy`)

## Environment Handling

-   `APP_ENV_FILE` from `Makefile` points to the local `.env` file
-   Terraform reads that file and injects it into EC2 bootstrap
-   The bootstrap writes `/opt/gaia/.env` and runs `docker compose`

## Runtime Services on EC2

The bootstrap/provisioners deploy these containers:

-   `plant-recognition`
-   `plant-care` (RAG + Groq)
-   `plant-care-llm` (Hugging Face fine-tuned flow)
-   `frontend` (nginx reverse proxy)

Before `tf-apply`, ensure the API images are pushed to Docker Hub with:

```bash
make push-apis
```

## Minimal Commands

```bash
make tf-init
make tf-apply AWS_KEY_NAME=misclavesaws
make tf-output
```
