# Enterprise Architecture Documentation
## Government Assistance Workforce Backend System

### Version: 1.0.0
### Last Updated: August 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Security Architecture](#security-architecture)
4. [Module Documentation](#module-documentation)
5. [API Documentation](#api-documentation)
6. [Service Layer](#service-layer)
7. [Data Architecture](#data-architecture)
8. [Integration Points](#integration-points)
9. [Performance & Optimization](#performance--optimization)
10. [Deployment & Operations](#deployment--operations)
11. [Monitoring & Observability](#monitoring--observability)
12. [Environment Configuration](#environment-configuration)

---

## Executive Summary

The Government Assistance Workforce Backend is an enterprise-grade, AI-powered system designed to facilitate government assistance programs through intelligent workforce management and document processing. Built on modern cloud-native principles, the system leverages Azure services, OpenAI, and advanced security measures to provide scalable, secure, and efficient operations.

### Key Features
- **AI-Powered Document Intelligence**: Automated document processing and analysis
- **Secure Prompt Management**: LLM-Guard integration for prompt injection protection
- **Multi-tenant Architecture**: Isolated data and processing per tenant
- **Real-time Analytics**: Comprehensive metrics and monitoring
- **Azure Integration**: Deep integration with Azure services (Service Bus, Cosmos DB, Storage, Key Vault)

### Technology Stack
- **Runtime**: Python 3.11
- **Framework**: FastAPI with async/await support
- **Database**: Azure Cosmos DB with SQL Server fallback
- **Message Queue**: Azure Service Bus
- **AI/ML**: OpenAI GPT-4, Azure Document Intelligence
- **Security**: LLM-Guard, Azure Key Vault, JWT authentication
- **Monitoring**: OpenTelemetry, Azure Monitor

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web Apps, Mobile Apps, API Consumers)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│  (FastAPI + Middleware + Authentication)                     │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Service    │    │   Service    │    │   Service    │
│   Layer      │    │   Layer      │    │   Layer      │
│ (Business    │    │ (Document    │    │ (Workforce   │
│  Logic)      │    │  Processing) │    │  Management) │
└──────────────┘    └──────────────┘    └──────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│         (Repositories + Database Abstraction)                │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Azure       │    │  Azure       │    │  Azure       │
│  Cosmos DB   │    │  Service Bus │    │  Storage     │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Component Architecture

The system follows a layered architecture pattern with clear separation of concerns:

1. **Presentation Layer** (`/api`): RESTful API endpoints
2. **Business Logic Layer** (`/services`): Core business operations
3. **Data Access Layer** (`/repository`): Database operations
4. **Core Infrastructure** (`/core`): Shared utilities and configurations
5. **Security Layer**: Cross-cutting security concerns

---

## Security Architecture

### LLM-Guard Integration

The system implements comprehensive prompt injection protection using LLM-Guard with ONNX optimization.

#### Configuration
```python
# Environment Variables for LLM-Guard
LLM_GUARD_USE_ONNX=true          # Enable/disable ONNX optimization
LLM_GUARD_LOW_MEMORY_MODE=true   # Enable low memory mode
LLM_GUARD_THRESHOLD=0.5          # Risk threshold (0.0-1.0)
LLM_GUARD_CACHE_TTL=300          # Cache TTL in seconds
LLM_GUARD_CACHE_SIZE=1000        # Maximum cache entries
```

#### Security Modes
- **Development**: Permissive (threshold: 0.7)
- **Staging**: Balanced (threshold: 0.5)
- **Production**: Strict (threshold: 0.3)

### Authentication & Authorization

- **JWT-based Authentication**: Secure token-based auth
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **Azure AD Integration**: Enterprise SSO support
- **API Key Management**: For service-to-service communication

### Data Protection

- **Encryption at Rest**: Azure-managed encryption
- **Encryption in Transit**: TLS 1.2+ enforced
- **Key Management**: Azure Key Vault integration
- **PII Protection**: Automatic redaction and anonymization

---

## Module Documentation

### Core Modules (`/src/core`)

#### 1. Configuration Management (`config.py`)
Centralized configuration using Pydantic Settings:
- Environment-specific configurations
- Azure service connections
- Feature flags
- Security settings

#### 2. LLM Guard Configuration (`llm_guard_config.py`)
Advanced security configuration for prompt injection protection:
- Dynamic threshold management
- ONNX optimization controls
- Memory management settings
- Performance tuning

#### 3. Database Management (`database.py`)
Database connection pooling and session management:
- Async SQLAlchemy integration
- Connection pooling
- Transaction management
- Query optimization

#### 4. Dependency Injection (`container.py`)
IoC container for service resolution:
- Service registration
- Lifecycle management
- Dependency resolution

#### 5. Exception Handling (`exceptions.py`, `azure_exceptions.py`)
Comprehensive error handling:
- Custom exception hierarchy
- Azure-specific exceptions
- Error recovery strategies

### Service Layer (`/src/services`)

#### 1. LLM Guard Service (`llm_guard_service.py`)
**Purpose**: Real-time prompt injection detection and prevention

**Key Features**:
- ONNX-optimized inference
- In-memory caching with TTL
- Async operation support
- Memory-aware processing
- Performance metrics collection

**Methods**:
- `scan_prompt()`: Synchronous prompt scanning
- `scan_prompt_async()`: Asynchronous prompt scanning
- `get_metrics()`: Performance metrics retrieval
- `update_threshold()`: Dynamic threshold adjustment

**Performance Characteristics**:
- Average latency: <10ms with ONNX
- Memory usage: ~200-500MB with low memory mode

#### 2. Workforce Agent Service (`workforce_agent_service.py`)
Manages AI-powered workforce agents:
- Agent lifecycle management
- Task distribution
- Performance tracking
- Agent collaboration

#### 3. Document Service (`document_service.py`)
Document processing pipeline:
- PDF/DOCX extraction
- OCR integration
- Metadata extraction
- Content indexing

#### 4. Analytics Service (`analytics_service.py`)
Real-time analytics and reporting:
- Usage metrics
- Performance analytics
- Cost tracking
- Trend analysis

### Repository Layer (`/src/repository`)

Data access patterns implementing Repository pattern:

#### Key Repositories:
- `WorkforceAgentsRepository`: Agent data management
- `DocumentRepository`: Document storage and retrieval
- `TopicRepository`: Topic categorization
- `AnalyticsRepository`: Metrics persistence

### API Layer (`/src/api`)

#### Endpoints Structure:
```
/api/
├── /workforce-agent/     # Workforce management
├── /documents/           # Document operations
├── /analytics/           # Analytics and reporting
├── /llm-guard/          # Security metrics
│   ├── /metrics         # Performance metrics
│   ├── /health          # Health check
│   └── /cache/clear     # Cache management
└── /admin/              # Administrative operations
```

### Utility Modules (`/src/utils`)

#### 1. Prompt Security (`prompt_security.py`)
Additional security layers:
- Input sanitization
- Output validation
- Pattern matching
- Content filtering

#### 2. RAG Pipeline (`/RAG_Pipeline/`)
Retrieval-Augmented Generation implementation:
- Document chunking
- Embedding generation
- Similarity search
- Context assembly

#### 3. Function Validators
Input/output validation utilities:
- Schema validation
- Type checking
- Business rule enforcement

---

## API Documentation

### LLM-Guard Metrics API

#### GET `/api/llm-guard/metrics`
Returns comprehensive metrics about LLM-Guard performance.

**Response**:
```json
{
  "metrics": {
    "total_scans": 10000,
    "cache_hits": 8000,
    "cache_misses": 2000,
    "blocked_prompts": 150,
    "allowed_prompts": 9850,
    "average_scan_time_ms": 8.5,
    "memory_usage_mb": 256.3,
    "peak_memory_usage_mb": 512.7
  },
  "configuration": {
    "threshold": 0.5,
    "cache_enabled": true,
    "cache_ttl": 300,
    "onnx_enabled": true,
    "low_memory_mode": true
  },
  "memory": {
    "current_usage_mb": 256.3,
    "peak_usage_mb": 512.7
  }
}
```

#### POST `/api/llm-guard/cache/clear`
Clears the LLM-Guard cache.

#### GET `/api/llm-guard/health`
Health check endpoint for monitoring.

---

## Performance & Optimization

### ONNX Optimization

The system uses ONNX Runtime for significant performance improvements:

#### Performance Benchmarks:
| Configuration | Latency (ms) | Throughput (QPS) | Memory (MB) |
|--------------|-------------|------------------|-------------|
| CPU (no ONNX) | 50-100 | 10-20 | 800-1200 |
| CPU (ONNX) | 5-15 | 65-200 | 400-600 |
| CPU (ONNX + Low Mem) | 8-20 | 50-125 | 200-400 |
| GPU (ONNX) | 2-5 | 200-500 | 600-1000 |

### Memory Optimization Strategies

1. **Low CPU Memory Mode**: Reduces model memory footprint by 40-60%
2. **Lazy Loading**: Models loaded on-demand
3. **Cache Management**: TTL-based eviction
4. **Process Monitoring**: Real-time memory tracking

### Caching Strategy

In-memory caching implementation using `cachetools.TTLCache`:
- **Cache Type**: In-memory TTL-based cache
- **Default TTL**: 5 minutes (300 seconds), configurable via `LLM_GUARD_CACHE_TTL`
- **Cache Size**: 1000 entries by default, configurable via `LLM_GUARD_CACHE_SIZE`
- **Key Generation**: SHA-256 hashing of prompts for cache keys
- **Thread Safety**: Built-in thread-safe operations
- **Cache Metrics**: Hit/miss tracking for performance monitoring

---

## Deployment & Operations

### Environment Requirements

```yaml
Production:
  Python: 3.11.x
  Memory: 4-8 GB
  CPU: 4-8 cores
  Storage: 50 GB SSD
  
Staging:
  Python: 3.11.x
  Memory: 2-4 GB
  CPU: 2-4 cores
  Storage: 20 GB SSD
```

### Azure Resource Requirements

- **Azure Cosmos DB**: RU/s based on workload
- **Azure Service Bus**: Standard/Premium tier
- **Azure Storage**: Hot tier for active documents
- **Azure Key Vault**: Standard tier
- **Azure Monitor**: Application Insights

### Deployment Process

1. **Infrastructure Provisioning**: Terraform/ARM templates
2. **Configuration Management**: Azure App Configuration
3. **Secret Management**: Azure Key Vault
4. **Container Deployment**: Docker/AKS
5. **Health Checks**: Readiness/Liveness probes

---

## Monitoring & Observability

### Metrics Collection

#### Application Metrics:
- Request latency (p50, p95, p99)
- Error rates
- Throughput
- Resource utilization

#### Business Metrics:
- Documents processed
- Agents active
- Tasks completed
- User engagement

### Logging Strategy

Structured logging with correlation IDs:
```python
logger.info("Processing document", extra={
    "document_id": doc_id,
    "correlation_id": correlation_id,
    "user_id": user_id,
    "operation": "document_processing"
})
```

### Alerting Rules

- **Critical**: Response time > 1s, Error rate > 5%
- **Warning**: Memory usage > 80%, CPU > 70%
- **Info**: Cache hit ratio < 60%

---

## Environment Configuration

### Required Environment Variables

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=xxx
AZURE_TENANT_ID=xxx
AZURE_CLIENT_ID=xxx
AZURE_CLIENT_SECRET=xxx

# Database
DATABASE_URL=xxx
COSMOS_DB_ENDPOINT=xxx
COSMOS_DB_KEY=xxx

# Service Bus
SERVICE_BUS_CONNECTION_STRING=xxx
SERVICE_BUS_QUEUE_NAME=xxx

# OpenAI
OPENAI_API_KEY=xxx
OPENAI_MODEL=gpt-4

# LLM-Guard
LLM_GUARD_USE_ONNX=true
LLM_GUARD_LOW_MEMORY_MODE=true
LLM_GUARD_THRESHOLD=0.5
LLM_GUARD_CACHE_TTL=300
LLM_GUARD_CACHE_SIZE=1000

# Monitoring
APPLICATION_INSIGHTS_KEY=xxx
OTEL_EXPORTER_OTLP_ENDPOINT=xxx
```

### Security Best Practices

1. **Never commit secrets**: Use Azure Key Vault
2. **Rotate credentials**: Implement rotation policies
3. **Least privilege**: Minimal permissions per service
4. **Network isolation**: Private endpoints where possible
5. **Audit logging**: Track all security events

---

## Troubleshooting Guide

### Common Issues

#### High Memory Usage
**Symptoms**: Memory usage > 1GB
**Solutions**:
1. Enable `LLM_GUARD_LOW_MEMORY_MODE=true`
2. Disable ONNX: `LLM_GUARD_USE_ONNX=false`
3. Reduce cache size: `LLM_GUARD_CACHE_SIZE=500`
4. Implement model unloading after idle periods

#### Slow Response Times
**Symptoms**: Latency > 100ms
**Solutions**:
1. Enable ONNX: `LLM_GUARD_USE_ONNX=true`
2. Increase cache TTL: `LLM_GUARD_CACHE_TTL=600`
3. Scale horizontally (add instances)
4. Optimize database queries

#### Prompt Injection False Positives
**Symptoms**: Legitimate prompts blocked
**Solutions**:
1. Adjust threshold: `LLM_GUARD_THRESHOLD=0.7`
2. Review blocked prompts in logs
3. Implement whitelist patterns
4. Fine-tune model if necessary

---

## Maintenance & Updates

### Regular Maintenance Tasks

**Daily**:
- Monitor error logs
- Check resource utilization
- Review security alerts

**Weekly**:
- Clear old cache entries
- Review performance metrics
- Update security signatures

**Monthly**:
- Security patches
- Dependency updates
- Performance optimization review
- Cost analysis

### Upgrade Path

1. **Testing**: Validate in staging environment
2. **Backup**: Database and configuration backup
3. **Deployment**: Blue-green deployment strategy
4. **Validation**: Health checks and smoke tests
5. **Rollback**: Prepared rollback plan

---

## Support & Contact

### Internal Support
- **Development Team**: dev-team@organization.com
- **DevOps Team**: devops@organization.com
- **Security Team**: security@organization.com

### External Dependencies
- **Azure Support**: Premium support tier
- **OpenAI Support**: Enterprise agreement
- **LLM-Guard**: GitHub issues/discussions

---

## Appendices

### A. Glossary
- **ONNX**: Open Neural Network Exchange
- **QPS**: Queries Per Second
- **TTL**: Time To Live
- **RU/s**: Request Units per second (Cosmos DB)
- **JWT**: JSON Web Token

### B. References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure Documentation](https://docs.microsoft.com/azure/)
- [LLM-Guard Documentation](https://github.com/protectai/llm-guard)
- [OpenTelemetry Documentation](https://opentelemetry.io/)

### C. Version History
- v1.0.0 (2025-08): Initial documentation
  - Added ONNX optimization
  - Implemented memory tracking
  - Enhanced security configuration

---

*This document is maintained by the Engineering Team and should be updated with each major release.*