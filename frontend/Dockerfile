# Stage 1: Prepare static assets and non-root config
FROM alpine:3.20 AS prep

WORKDIR /prep
COPY nginx.conf .
COPY index.html .
RUN sed -i 's/listen\s*80;/listen 8080;/g' nginx.conf

# Stage 2: Minimal Nginx runtime as non-root
FROM nginx:1.27-alpine

COPY --from=prep /prep/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=prep /prep/index.html /usr/share/nginx/html/index.html

RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx
EXPOSE 8080