sudo docker build -f /data/llm_web/MedicalInsights/Dockerfile -t llm_web:latest . --build-arg HTTP_PROXY=http://10.31.65.233:3128 --build-arg HTTPS_PROXY=http://10.31.65.233:3128
