import pytest

from db_manager import VectorDBManager


@pytest.fixture
def mock_env(monkeypatch):
    """Fakes the environment variables so we don't need a .env file."""
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("REGION", "us-east1")
    monkeypatch.setenv("GCS_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("INDEX_ID", "test-index-123")
    monkeypatch.setenv("ENDPOINT_ID", "test-endpoint-123")


@pytest.fixture
def mock_gcp_clients(mocker):
    """Replaces the heavy Google Cloud SDKs with cardboard cutouts."""
    mocker.patch("db_manager.vertexai.init")
    mocker.patch("db_manager.aiplatform.init")
    mocker.patch("db_manager.storage.Client")


def test_init_fails_without_env_vars(monkeypatch):
    """Test that our class safely crashes if secrets are missing."""
    monkeypatch.delenv("PROJECT_ID", raising=False)

    # We expect a ValueError to be raised here
    with pytest.raises(ValueError, match="Missing core environment variables"):
        VectorDBManager(env_file="dummy.env")


def test_ingest_data(mock_env, mock_gcp_clients, mocker):
    """Test that we generate a vector and send it to the right GCS bucket."""
    # 1. Intercept the Embedding Model
    mock_model_class = mocker.patch("db_manager.MultiModalEmbeddingModel")
    mock_model_instance = mock_model_class.from_pretrained.return_value

    # 2. Fake the math (pretend Google returned this vector)
    mock_model_instance.get_embeddings.return_value.text_embedding = [0.1, 0.2, 0.3]

    # 3. Run our actual code
    manager = VectorDBManager(env_file="dummy.env")
    manager.ingest_data("Hello AI")

    # 4. Assertions: Did our code ask Google to do the right things?
    mock_model_instance.get_embeddings.assert_called_once_with(
        contextual_text="Hello AI"
    )
    manager.storage_client.bucket.assert_called_once_with("test-bucket")


def test_deploy(mock_env, mock_gcp_clients, mocker):
    """Test that we update the index and mount it to the endpoint."""
    mock_index = mocker.patch("db_manager.aiplatform.MatchingEngineIndex")
    mock_endpoint = mocker.patch("db_manager.aiplatform.MatchingEngineIndexEndpoint")

    manager = VectorDBManager(env_file="dummy.env")
    manager.deploy(deployment_id="test_deploy_1")

    # Verify we told GCP to read the bucket, then mount the index
    mock_index.return_value.update_embeddings.assert_called_once()
    mock_endpoint.return_value.deploy_index.assert_called_once()


def test_teardown_with_active_indexes(mock_env, mock_gcp_clients, mocker):
    """Test that we successfully shut down billing if nodes are active."""
    mock_endpoint = mocker.patch("db_manager.aiplatform.MatchingEngineIndexEndpoint")

    # Fake the GCP state: Pretend there is 1 active node running right now
    mock_active_index = mocker.MagicMock()
    mock_active_index.deployed_index_id = "test_deploy_1"
    mock_endpoint.return_value.deployed_indexes = [mock_active_index]

    manager = VectorDBManager(env_file="dummy.env")
    manager.teardown()

    # Verify we specifically told GCP to kill that exact node
    mock_endpoint.return_value.undeploy_index.assert_called_once_with(
        deployed_index_id="test_deploy_1"
    )
