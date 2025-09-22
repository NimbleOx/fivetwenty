# Kubernetes Deployment

Deploy FiveTwenty applications on Kubernetes with container orchestration, auto-scaling, and enterprise-grade reliability.

## Overview

Kubernetes deployment provides powerful container orchestration with automatic scaling, rolling updates, service discovery, and robust infrastructure management. This approach is ideal for large-scale trading operations requiring high availability and scalability.

**Best for**: Enterprise trading operations, high-traffic applications, teams requiring advanced orchestration features, multi-environment deployments.

## Architecture Overview

```mermaid
graph TB
    A[Ingress Controller] --> B[Trading Service]
    B --> C[Trading Pods]
    C --> D[PostgreSQL StatefulSet]
    C --> E[Redis Cluster]
    F[Prometheus] --> C
    G[ConfigMaps] --> C
    H[Secrets] --> C
    I[PersistentVolumes] --> D

    style C fill:#e1f5fe
    style I fill:#f3e5f5
```

## Kubernetes Manifests

### Namespace and RBAC

```yaml
# k8s/00-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fivetwenty-trading
  labels:
    name: fivetwenty-trading
    environment: production

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fivetwenty-trading-sa
  namespace: fivetwenty-trading

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: fivetwenty-trading
  name: fivetwenty-trading-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: fivetwenty-trading-rolebinding
  namespace: fivetwenty-trading
subjects:
- kind: ServiceAccount
  name: fivetwenty-trading-sa
  namespace: fivetwenty-trading
roleRef:
  kind: Role
  name: fivetwenty-trading-role
  apiGroup: rbac.authorization.k8s.io
```

### Secrets Management

```yaml
# k8s/01-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: fivetwenty-secrets
  namespace: fivetwenty-trading
type: Opaque
data:
  # Base64 encoded values
  FIVETWENTY_LIVE_TOKEN: <base64-encoded-token>
  FIVETWENTY_OANDA_ACCOUNT: <base64-encoded-account-id>
  DATABASE_PASSWORD: <base64-encoded-db-password>
  REDIS_PASSWORD: <base64-encoded-redis-password>
  SENTRY_DSN: <base64-encoded-sentry-dsn>
  SLACK_WEBHOOK_URL: <base64-encoded-webhook-url>

---
apiVersion: v1
kind: Secret
metadata:
  name: registry-secret
  namespace: fivetwenty-trading
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

### ConfigMaps

```yaml
# k8s/02-configmaps.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fivetwenty-config
  namespace: fivetwenty-trading
data:
  FIVETWENTY_OANDA_ENVIRONMENT: "LIVE"
  LOG_LEVEL: "INFO"
  MAX_POSITION_SIZE: "100000"
  DAILY_LOSS_LIMIT: "1000.0000"
  METRICS_PORT: "8080"
  HEALTH_PORT: "8081"
  REDIS_URL: "redis://fivetwenty-redis:6379"
  DATABASE_URL: "postgresql://trading:$(DATABASE_PASSWORD)@fivetwenty-postgres:5432/trading_prod"

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  namespace: fivetwenty-trading
data:
  POSTGRES_DB: trading_prod
  POSTGRES_USER: trading
  PGDATA: /var/lib/postgresql/data/pgdata

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: fivetwenty-trading
data:
  redis.conf: |
    bind 0.0.0.0
    port 6379
    requirepass $(REDIS_PASSWORD)
    appendonly yes
    appendfsync everysec
    maxmemory 1gb
    maxmemory-policy allkeys-lru
    tcp-keepalive 60
    timeout 300
```

### PostgreSQL StatefulSet

```yaml
# k8s/03-postgres.yaml
apiVersion: v1
kind: Service
metadata:
  name: fivetwenty-postgres
  namespace: fivetwenty-trading
  labels:
    app: postgres
spec:
  ports:
  - port: 5432
    name: postgres
  clusterIP: None
  selector:
    app: postgres

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: fivetwenty-trading
spec:
  serviceName: fivetwenty-postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fivetwenty-secrets
              key: DATABASE_PASSWORD
        envFrom:
        - configMapRef:
            name: postgres-config
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        - name: postgres-config-volume
          mountPath: /etc/postgresql/postgresql.conf
          subPath: postgresql.conf
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - trading
            - -d
            - trading_prod
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - trading
            - -d
            - trading_prod
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-config-volume
        configMap:
          name: postgres-config
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
  namespace: fivetwenty-trading
data:
  init.sql: |
    -- Initialize database
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Create tables for trading application
    CREATE TABLE IF NOT EXISTS trades (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        instrument VARCHAR(50) NOT NULL,
        units INTEGER NOT NULL,
        price DECIMAL(10,5) NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        trade_type VARCHAR(20) NOT NULL
    );

    CREATE INDEX idx_trades_timestamp ON trades(timestamp);
    CREATE INDEX idx_trades_instrument ON trades(instrument);
```

### Redis Deployment

```yaml
# k8s/04-redis.yaml
apiVersion: v1
kind: Service
metadata:
  name: fivetwenty-redis
  namespace: fivetwenty-trading
  labels:
    app: redis
spec:
  ports:
  - port: 6379
    name: redis
  selector:
    app: redis

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: fivetwenty-trading
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        command:
        - redis-server
        - /etc/redis/redis.conf
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fivetwenty-secrets
              key: REDIS_PASSWORD
        volumeMounts:
        - name: redis-config
          mountPath: /etc/redis
        - name: redis-data
          mountPath: /data
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: fivetwenty-trading
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: fast-ssd
```

### Trading Application Deployment

```yaml
# k8s/05-trading-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fivetwenty-trading-app
  namespace: fivetwenty-trading
  labels:
    app: fivetwenty-trading-app
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fivetwenty-trading-app
  template:
    metadata:
      labels:
        app: fivetwenty-trading-app
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: fivetwenty-trading-sa
      imagePullSecrets:
      - name: registry-secret
      containers:
      - name: trading-app
        image: your-registry.com/fivetwenty-trading:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: metrics
          protocol: TCP
        - containerPort: 8081
          name: health
          protocol: TCP
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        envFrom:
        - configMapRef:
            name: fivetwenty-config
        - secretRef:
            name: fivetwenty-secrets
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: data
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /health
            port: health
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: health
          initialDelaySeconds: 30
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: health
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 10
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: logs
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: trading-data-pvc
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - fivetwenty-trading-app
              topologyKey: kubernetes.io/hostname
      tolerations:
      - key: "trading-workload"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: trading-data-pvc
  namespace: fivetwenty-trading
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd

---
apiVersion: v1
kind: Service
metadata:
  name: fivetwenty-trading-service
  namespace: fivetwenty-trading
  labels:
    app: fivetwenty-trading-app
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: metrics
    protocol: TCP
    name: metrics
  - port: 8081
    targetPort: health
    protocol: TCP
    name: health
  selector:
    app: fivetwenty-trading-app
```

### Horizontal Pod Autoscaler

```yaml
# k8s/06-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fivetwenty-trading-hpa
  namespace: fivetwenty-trading
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fivetwenty-trading-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: oanda_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

### Ingress Controller

```yaml
# k8s/07-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fivetwenty-trading-ingress
  namespace: fivetwenty-trading
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - trading.yourdomain.com
    secretName: fivetwenty-trading-tls
  rules:
  - host: trading.yourdomain.com
    http:
      paths:
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: fivetwenty-trading-service
            port:
              number: 8081
      - path: /metrics
        pathType: Prefix
        backend:
          service:
            name: fivetwenty-trading-service
            port:
              number: 8080

---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

## Monitoring Stack

### Prometheus Configuration

```yaml
# k8s/monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: fivetwenty-trading
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'fivetwenty-trading'
        environment: 'production'

    rule_files:
      - "/etc/prometheus/rules/*.yml"

    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
        - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
        - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
          action: keep
          regex: default;kubernetes;https

      - job_name: 'fivetwenty-trading-app'
        kubernetes_sd_configs:
        - role: pod
          namespaces:
            names:
            - fivetwenty-trading
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
          action: replace
          target_label: __metrics_path__
          regex: (.+)
        - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
          action: replace
          regex: ([^:]+)(?::\d+)?;(\d+)
          replacement: $1:$2
          target_label: __address__
        - action: labelmap
          regex: __meta_kubernetes_pod_label_(.+)
        - source_labels: [__meta_kubernetes_namespace]
          action: replace
          target_label: kubernetes_namespace
        - source_labels: [__meta_kubernetes_pod_name]
          action: replace
          target_label: kubernetes_pod_name

      - job_name: 'postgres'
        static_configs:
        - targets: ['postgres-exporter:9187']

      - job_name: 'redis'
        static_configs:
        - targets: ['redis-exporter:9121']

    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: fivetwenty-trading
data:
  trading.yml: |
    groups:
    - name: fivetwenty-trading-alerts
      rules:
      - alert: TradingAppDown
        expr: up{job="fivetwenty-trading-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Trading application is down"
          description: "Trading app {{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighMemoryUsage
        expr: (container_memory_working_set_bytes{container="trading-app"} / container_spec_memory_limit_bytes) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 80% for {{ $labels.pod_name }}"

      - alert: AccountBalanceLow
        expr: account_balance < 5000
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Account balance is low"
          description: "Account balance is {{ $value }}"

      - alert: DatabaseConnectionFailed
        expr: up{job="postgres"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "Cannot connect to PostgreSQL database"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: fivetwenty-trading
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        args:
        - --config.file=/etc/prometheus/prometheus.yml
        - --storage.tsdb.path=/prometheus/
        - --web.console.libraries=/etc/prometheus/console_libraries
        - --web.console.templates=/etc/prometheus/consoles
        - --storage.tsdb.retention.time=30d
        - --web.enable-lifecycle
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-rules
          mountPath: /etc/prometheus/rules
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-rules
        configMap:
          name: prometheus-rules
      - name: prometheus-storage
        persistentVolumeClaim:
          claimName: prometheus-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: fivetwenty-trading
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: fivetwenty-trading
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
```

### Grafana Dashboard

```yaml
# k8s/monitoring/grafana.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: fivetwenty-trading
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus:9090
      isDefault: true

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-config
  namespace: fivetwenty-trading
data:
  dashboards.yaml: |
    apiVersion: 1
    providers:
    - name: 'default'
      orgId: 1
      folder: ''
      type: file
      disableDeletion: false
      updateIntervalSeconds: 10
      options:
        path: /var/lib/grafana/dashboards

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: fivetwenty-trading
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fivetwenty-secrets
              key: GRAFANA_PASSWORD
        - name: GF_INSTALL_PLUGINS
          value: "grafana-kubernetes-app"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-datasources
          mountPath: /etc/grafana/provisioning/datasources
        - name: grafana-dashboard-config
          mountPath: /etc/grafana/provisioning/dashboards
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: grafana-storage
        persistentVolumeClaim:
          claimName: grafana-pvc
      - name: grafana-datasources
        configMap:
          name: grafana-datasources
      - name: grafana-dashboard-config
        configMap:
          name: grafana-dashboard-config

---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: fivetwenty-trading
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: fivetwenty-trading
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
```

## Security Configuration

### Pod Security Standards

```yaml
# k8s/security/pod-security.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fivetwenty-trading
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted

---
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: fivetwenty-trading-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: fivetwenty-trading-netpol
  namespace: fivetwenty-trading
spec:
  podSelector:
    matchLabels:
      app: fivetwenty-trading-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  - from:
    - namespaceSelector:
        matchLabels:
          name: fivetwenty-trading
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS to OANDA API
    - protocol: TCP
      port: 53   # DNS
    - protocol: UDP
      port: 53   # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: fivetwenty-trading
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
```

## Deployment Scripts

### Kubernetes Deployment Script

```bash
#!/bin/bash
# k8s-deploy.sh - Kubernetes deployment script

set -e

# Configuration
NAMESPACE="fivetwenty-trading"
IMAGE_TAG=${1:-latest}
REGISTRY=${REGISTRY:-"your-registry.com"}
APP_NAME="fivetwenty-trading"

echo "🚀 Starting Kubernetes deployment of $APP_NAME:$IMAGE_TAG"

# Check kubectl access
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Kubernetes cluster access confirmed"

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply security policies first
echo "🔒 Applying security policies..."
kubectl apply -f k8s/security/

# Apply secrets and configmaps
echo "📋 Applying configuration..."
kubectl apply -f k8s/01-secrets.yaml
kubectl apply -f k8s/02-configmaps.yaml

# Deploy database and cache
echo "🗃️ Deploying database and cache..."
kubectl apply -f k8s/03-postgres.yaml
kubectl apply -f k8s/04-redis.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# Deploy trading application
echo "📦 Deploying trading application..."
sed "s|your-registry.com/fivetwenty-trading:latest|$REGISTRY/$APP_NAME:$IMAGE_TAG|g" k8s/05-trading-app.yaml | kubectl apply -f -

# Apply autoscaling
kubectl apply -f k8s/06-hpa.yaml

# Apply ingress
kubectl apply -f k8s/07-ingress.yaml

# Deploy monitoring
echo "📊 Deploying monitoring stack..."
kubectl apply -f k8s/monitoring/

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available deployment/fivetwenty-trading-app -n $NAMESPACE --timeout=300s

# Verify deployment
echo "🔍 Verifying deployment..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Show status
echo "✅ Kubernetes deployment completed successfully"
echo ""
echo "📊 Monitoring URLs:"
echo "   - Prometheus: kubectl port-forward service/prometheus 9090:9090 -n $NAMESPACE"
echo "   - Grafana: kubectl port-forward service/grafana 3000:3000 -n $NAMESPACE"
echo ""
echo "🏥 Health check:"
echo "   kubectl port-forward service/fivetwenty-trading-service 8081:8081 -n $NAMESPACE"
echo "   curl http://localhost:8081/health"

# Run post-deployment tests
echo "🧪 Running post-deployment tests..."
kubectl run test-pod --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
  curl -f http://fivetwenty-trading-service:8081/health

echo "🎉 All tests passed!"
```

### Rolling Update Script

```bash
#!/bin/bash
# rolling-update.sh - Perform rolling update

set -e

NAMESPACE="fivetwenty-trading"
IMAGE_TAG=${1:-latest}
REGISTRY=${REGISTRY:-"your-registry.com"}
APP_NAME="fivetwenty-trading"

echo "🔄 Starting rolling update to $APP_NAME:$IMAGE_TAG"

# Update deployment image
kubectl set image deployment/fivetwenty-trading-app \
  trading-app=$REGISTRY/$APP_NAME:$IMAGE_TAG \
  -n $NAMESPACE

# Monitor rollout
kubectl rollout status deployment/fivetwenty-trading-app -n $NAMESPACE --timeout=600s

# Verify health
echo "🏥 Verifying application health..."
kubectl run health-check --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
  curl -f http://fivetwenty-trading-service:8081/health

echo "✅ Rolling update completed successfully"
```

## Backup and Disaster Recovery

### Database Backup CronJob

```yaml
# k8s/backup/postgres-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: fivetwenty-trading
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15-alpine
            command:
            - /bin/bash
            - -c
            - |
              BACKUP_FILE="/backup/postgres-backup-$(date +%Y%m%d-%H%M%S).sql.gz"
              pg_dump -h fivetwenty-postgres -U trading trading_prod | gzip > $BACKUP_FILE
              aws s3 cp $BACKUP_FILE s3://your-backup-bucket/postgres/
              echo "Backup completed: $BACKUP_FILE"
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: fivetwenty-secrets
                  key: DATABASE_PASSWORD
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

## Performance Optimization

### Resource Optimization

```yaml
# k8s/optimization/resource-quotas.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: fivetwenty-trading-quota
  namespace: fivetwenty-trading
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "20"
    secrets: "10"
    configmaps: "10"
    services: "10"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: fivetwenty-trading-limits
  namespace: fivetwenty-trading
spec:
  limits:
  - type: Container
    default:
      cpu: "500m"
      memory: "1Gi"
    defaultRequest:
      cpu: "250m"
      memory: "512Mi"
    max:
      cpu: "2000m"
      memory: "4Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
```

## Troubleshooting

### Common Kubernetes Issues

**Pod Scheduling Issues**:
```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name> -n fivetwenty-trading

# Check resource quotas
kubectl describe resourcequota -n fivetwenty-trading
```

**Networking Issues**:
```bash
# Test service connectivity
kubectl run debug --image=nicolaka/netshoot --rm -i --restart=Never -n fivetwenty-trading -- nslookup fivetwenty-postgres

# Check network policies
kubectl describe networkpolicy -n fivetwenty-trading
```

**Storage Issues**:
```bash
# Check PVC status
kubectl get pvc -n fivetwenty-trading

# Check storage class
kubectl get storageclass
```

### Performance Monitoring

```bash
# Monitor resource usage
kubectl top pods -n fivetwenty-trading
kubectl top nodes

# Check HPA status
kubectl get hpa -n fivetwenty-trading
kubectl describe hpa fivetwenty-trading-hpa -n fivetwenty-trading
```

Kubernetes deployment provides enterprise-grade container orchestration with automatic scaling, rolling updates, and comprehensive monitoring for production FiveTwenty trading applications.