import os
import json
import argparse
from dotenv import load_dotenv
from google.cloud import storage, aiplatform
import vertexai
from vertexai.vision_models import MultiModalEmbeddingModel


class VectorDBManager:
    """Manages the lifecycle and data ingestion for a Vertex AI Vector Search Database."""

    def __init__(self, env_file=".env.dev"):
        # Encapsulate state: Load variables upon instantiation
        load_dotenv(env_file)
        self.project_id = os.getenv("PROJECT_ID")
        self.region = os.getenv("REGION")
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        self.index_id = os.getenv("INDEX_ID")
        self.endpoint_id = os.getenv("ENDPOINT_ID")

        if not all([self.project_id, self.region, self.bucket_name]):
            raise ValueError(f"Missing core environment variables in {env_file}.")

        self.bucket_uri = f"gs://{self.bucket_name}/new_data/"

        # Initialize Google Cloud clients
        vertexai.init(project=self.project_id, location=self.region)
        aiplatform.init(project=self.project_id, location=self.region)
        self.storage_client = storage.Client(project=self.project_id)

    def ingest_data(self, text: str, filename: str = "new_data/batch_001.json"):
        """Generates a multimodal embedding and streams it to Google Cloud Storage."""
        print(f"Generating 1,408-dimension vector for: '{text}'...")
        model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
        embeddings = model.get_embeddings(contextual_text=text)

        record = {"id": "doc-001", "embedding": embeddings.text_embedding}
        jsonl_content = json.dumps(record) + "\n"

        print(f"Uploading to gs://{self.bucket_name}/{filename}...")
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(jsonl_content, content_type="application/json")
        print("✅ Upload complete!")

    def deploy(self, deployment_id: str = "rag_dev_v1"):
        """Instructs the Index to read new GCS data, then mounts to the Endpoint."""
        if not self.index_id or not self.endpoint_id:
            raise ValueError("INDEX_ID and ENDPOINT_ID required for deployment.")

        my_index = aiplatform.MatchingEngineIndex(index_name=self.index_id)
        my_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self.endpoint_id
        )

        print(f"1. Updating Index from {self.bucket_uri}...")
        my_index.update_embeddings(
            contents_delta_uri=self.bucket_uri, is_complete_overwrite=False
        )

        print("\n2. Deploying Index to Endpoint (⏳ this takes ~40 minutes)...")
        my_endpoint.deploy_index(index=my_index, deployed_index_id=deployment_id)
        print("\n✅ Database is live and mounted.")

    def teardown(self):
        """Spins down active compute nodes to stop GCP billing."""
        if not self.endpoint_id:
            raise ValueError("ENDPOINT_ID required for teardown.")

        my_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self.endpoint_id
        )
        deployed_indexes = my_endpoint.deployed_indexes

        if not deployed_indexes:
            print("🟢 Endpoint is already empty. You are not being billed!")
            return

        print(
            f"🟡 Found {len(deployed_indexes)} active deployment(s). Spinning down..."
        )
        for active_index in deployed_indexes:
            index_id = active_index.deployed_index_id
            print(f"Undeploying '{index_id}'...")
            my_endpoint.undeploy_index(deployed_index_id=index_id)

        print("✅ Teardown complete! Billing has stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vertex AI Vector Database Manager")
    parser.add_argument(
        "action", choices=["ingest", "deploy", "teardown"], help="Action to perform"
    )
    parser.add_argument(
        "--text",
        type=str,
        default="Vertex AI handles multimodal vectors fast.",
        help="Text to embed (only used with 'ingest')",
    )

    args = parser.parse_args()
    manager = VectorDBManager()

    if args.action == "ingest":
        manager.ingest_data(text=args.text)
    elif args.action == "deploy":
        manager.deploy()
    elif args.action == "teardown":
        manager.teardown()
