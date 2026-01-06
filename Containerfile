FROM ghcr.io/nginx/nginx-unprivileged:1.29.3-alpine

COPY index.html /usr/share/nginx/html/index.html
