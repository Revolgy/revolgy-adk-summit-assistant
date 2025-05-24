<h1 align="center">
  <br>
  <a href="https://revolgy.com"><img src="assets/revolgy_logo.png" width="400px" alt="Revolgy"></a>
</h1>

# Revolgy Google Cloud Summit Assistant

This assistant is built using Agent Development Kit (ADK) from Google.
Frontend is a Streamlit chat application interface with Revolgy branding.

### How to run locally

The app consists of two separate directories representing backend and frontend services. These two applications can be run separately.

#### Frontend

1. Clone the repository and go to frontend directory

```
git clone <repo-url>.git
cd <repo-name>/frontend
```

2. Install the required packages

```
python3 -m pip install -r requirements.txt
```

3. Run the application

```
streamlit run app.py
```

_Note: you may need to open a new terminal window after installing the required packages._


#### Backend

1. Clone the repository and go to backend/summit-app directory

```
git clone <repo-url>.git
cd <repo-name>/backend/summit-app
```

2. Install the required packages

```
python3 -m pip install -r requirements.txt
```

3. Run the application with web UI or as a standalone API server

```
adk web # with a web UI
adk api_server # only the API server
```

### How to deploy to Cloud Run

You need a Google Cloud project with billing enabled and all necessary APIs (Artifact Registry, Cloud Run, etc.) enabled.

#### Frontend

1. **Create an Artifact Registry repository**  
   In your GCP project, create a Docker repository in your desired region.

2. **Build the Docker image**  
   From the `frontend` directory, run:
   ```
   docker build -t cloud-summit-demo-fe:latest .
   ```
   > **Note:** If you are on a Mac with Apple Silicon (M series), add `--platform linux/amd64`:
   > ```
   > docker build --platform linux/amd64 -t cloud-summit-demo-fe:latest .
   > ```

3. **Tag the image for Artifact Registry**  
   Replace `<gcp-region>`, `<project-id>`, `<repository-id>`, `<image-name>`, and `<tag>` as appropriate:
   ```
   docker tag cloud-summit-demo-fe:latest <gcp-region>.pkg.dev/<project-id>/<repository-id>/cloud-summit-demo-fe:latest
   ```

4. **Push the image to Artifact Registry**
   ```
   docker push <gcp-region>.pkg.dev/<project-id>/<repository-id>/cloud-summit-demo-fe:latest
   ```

5. **Deploy to Cloud Run**  
   Deploy the image as a new Cloud Run service. Make sure to set the port to `8501` (Streamlit default):
   ```
   gcloud run deploy <frontend-service-name> \
     --image <gcp-region>.pkg.dev/<project-id>/<repository-id>/cloud-summit-demo-fe:latest \
     --region <gcp-region> \
     --project <project-id> \
     --allow-unauthenticated \
     --port 8501
   ```

6. **Set backend URL as environment variable**  
   After deploying the backend and obtaining its URL, update the frontend Cloud Run service to include the backend URL (replace `<backend-url>`):
   ```
   gcloud run services update <frontend-service-name> \
     --region <gcp-region> \
     --project <project-id> \
     --update-env-vars BACKEND_URL=<backend-url>
   ```

#### Backend

1. **Navigate to the backend directory**  
   ```
   cd backend/summit-app
   ```

2. **Set required environment variables**  
   Make sure you are authenticated with `gcloud` and have the necessary permissions.

3. **Deploy to Cloud Run**  
   Replace placeholders as needed:
   ```
   gcloud run deploy <service-name> \
     --source . \
     --region $GOOGLE_CLOUD_LOCATION \
     --project $GOOGLE_CLOUD_PROJECT \
     --allow-unauthenticated \
     --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=1,VERTEXAI_DATASTORE_DOCS_ID=<datastore-id1>,VERTEXAI_DATASTORE_PRODUCT_RELEASES_ID=<datastore-id2>,VERTEXAI_DATASTORE_APIS_ID=<datastore-id3>"
   ```

4. **Verify the deployment**  
   After deployment, test the API with:
   ```
   curl -X POST <api_url>/apps/summit_app/users/user/sessions/s_124 \
     -H "Content-Type: application/json" \
     -d '{}'
   ```
   You should receive a response similar to:
   ```
   {"id":"s_124","appName":"summit_app","userId":"user","state":{},"events":[],"lastUpdateTime":1748114377.0}
   ```

## About Revolgy

[Revolgy](https://revolgy.com) helps businesses scale with secure, intelligent cloud solutions that solve what cloud alone can’t. From initial deployment and AI enablement to robust security, [Revolgy](https://revolgy.com) makes the cloud work for you.
