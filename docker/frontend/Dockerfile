FROM nginx:1.27-alpine

COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY projects/frontend/index.html \
    projects/frontend/styles.css \
    projects/frontend/script.js \
    projects/frontend/login.html \
    projects/frontend/login.js \
    /usr/share/nginx/html/
COPY docker/frontend/api-bases.prod.js /usr/share/nginx/html/api-bases.js

EXPOSE 80
