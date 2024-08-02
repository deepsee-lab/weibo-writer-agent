# Milvus

## GitHub

https://github.com/milvus-io/milvus

## Docs

https://milvus.io/docs/overview.md

https://milvus.io/docs/install_standalone-docker.md

## Run

###### Docker

确保已安装 Docker，并正确启动，安装教程：https://docs.docker.com/engine/install/

研发环境建议使用 Docker 桌面版，下载链接： https://www.docker.com/products/docker-desktop/

###### Command

```bash
# Download the installation script
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

# Start the Docker container
# docker rm milvus-standalone
bash standalone_embed.sh start
docker logs milvus-standalone -f

# Stop Milvus
bash standalone_embed.sh stop

# Delete Milvus data
bash standalone_embed.sh delete
```
