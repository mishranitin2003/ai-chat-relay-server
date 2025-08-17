# OpenAI Relay Server

A production-ready FastAPI server that acts as a secure relay for OpenAI API calls with authentication, rate limiting, and streaming support.

## Features

- 🔐 **JWT Authentication** - Secure user authentication with token-based access
- ⚡ **Rate Limiting** - Token bucket algorithm with Redis backend
- 🌊 **Streaming Support** - Real-time streaming of OpenAI responses
- 🛡️ **Security** - CORS, security headers, input validation
- 📊 **Monitoring** - Health checks, metrics, and logging
- 🐳 **Docker Ready** - Production and development Docker configurations
- 🚀 **High Performance** - Async/await throughout, optimized for scale

## Quick Start

### Using Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd ai-chat-relay-server
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` file with your OpenAI API key and other settings.

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs (development only)

### Local Development

1. **Install Python 3.11+**

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh access token

### Chat

- `POST /api/v1/chat/completions` - Non-streaming chat completion
- `POST /api/v1/chat/completions/stream` - Streaming chat completion
- `GET /api/v1/chat/models` - Get available models

### Health

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with metrics

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT secret key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `DEFAULT_MODEL` | Default OpenAI model | `gpt-4o-mini` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["http://localhost:3000"]` |
| `RATE_LIMIT_REQUESTS` | Requests per window | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `3600` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./app.db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

### Rate Limiting

The server implements rate limiting using a token bucket algorithm:
- Default: 100 requests per hour per user/IP
- Configurable per endpoint
- Redis-backed for distributed deployments
- Graceful fallback to in-memory for development

### Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS configuration
- Security headers (XSS, CSRF, etc.)
- Request/response logging
- Input validation and sanitization

## Deployment

### Production Deployment

1. **Using Docker Compose**:
   ```bash
   # Copy production compose file
   cp docker-compose.prod.yml docker-compose.yml

   # Set environment variables
   export SECRET_KEY="your-secret-key"
   export OPENAI_API_KEY="your-openai-key"

   # Deploy
   docker-compose up -d
   ```

2. **Using Docker Swarm**:
   ```bash
   docker stack deploy -c docker-compose.prod.yml ai-chat-relay
   ```

3. **Environment Setup**:
   - Generate secure `SECRET_KEY`
   - Configure `ALLOWED_ORIGINS` for your frontend domains
   - Set up SSL certificates for HTTPS
   - Configure monitoring and alerting

### Monitoring

- Health endpoints for uptime monitoring
- Structured logging with configurable levels
- Metrics collection ready
- Error tracking and alerting

### Scaling

- Horizontal scaling with multiple replicas
- Redis for shared state (rate limiting, caching)
- Stateless design for load balancing
- Database connection pooling

## Development

### Project Structure

```
app/
├── main.py              # FastAPI application
├── core/                # Core configuration
│   ├── config.py        # Settings and environment
│   ├── security.py      # Authentication and security
│   └── rate_limiter.py  # Rate limiting logic
├── api/                 # API routes
│   └── v1/              # API version 1
│       └── endpoints/   # Endpoint modules
├── services/            # Business logic
├── models/              # Pydantic models
└── middleware/          # Custom middleware
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_chat.py -v
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues and discussions
