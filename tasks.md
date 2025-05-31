# Ergo Price MCP Server - Task Breakdown

## Project Status: 🟡 In Progress
**Current Phase**: Phase 1 - Project Setup  
**Last Updated**: 2024-12-19  
**Next Milestone**: Basic project structure and CRUX API HTTP client

## 🎯 **Project Goal**
Build an MCP server that **consumes** the existing CRUX Finance API (https://api.cruxfinance.io) and exposes the data as MCP tools for LLM consumption via MCPO proxy.

**We are NOT recreating the CRUX API - only consuming it via HTTP requests.**

---

## Phase 1: Project Setup & Foundation 🏗️

### 1.1 Project Structure Setup
- [ ] **1.1.1** Create main project directory structure
  ```bash
  mkdir -p src/ergo_price_mcp/{tools,resources,api,cache,utils}
  mkdir -p tests/{unit,integration,fixtures}
  mkdir -p docs scripts
  ```
- [ ] **1.1.2** Initialize Python project with uv
  ```bash
  uv init ergo-price-mcp
  cd ergo-price-mcp
  ```
- [ ] **1.1.3** Create pyproject.toml with dependencies
  - Add mcp[cli], httpx, pydantic, python-dotenv, fastapi, uvicorn
  - Add dev dependencies: pytest, black, isort, mypy, pytest-asyncio
- [ ] **1.1.4** Create .env.example file with all required environment variables
- [ ] **1.1.5** Create .gitignore file (Python, IDE, environment files)
- [ ] **1.1.6** Create basic README.md with setup instructions

### 1.2 Configuration System
- [ ] **1.2.1** Create `src/ergo_price_mcp/utils/config.py`
  - Environment variable loading with pydantic settings
  - CRUX API base URL (https://api.cruxfinance.io)
  - API timeouts, cache TTLs
  - Validation for required settings
- [ ] **1.2.2** Create `src/ergo_price_mcp/utils/logging.py`
  - Structured logging setup with correlation IDs
  - Log levels configuration
  - Console and file output handlers

### 1.3 Basic Package Structure
- [ ] **1.3.1** Create all `__init__.py` files in package directories
- [ ] **1.3.2** Set up package version management
- [ ] **1.3.3** Create basic module imports and exports

---

## Phase 2: CRUX API HTTP Client Implementation 🔌

### 2.1 API Response Models & Schemas
- [ ] **2.1.1** Create `src/ergo_price_mcp/api/models.py`
  - **Purpose**: Define Pydantic models for CRUX API responses
  - ErgPriceResponse model (for `/coingecko/erg_price` endpoint)
  - ErgHistoryResponse model (for `/coingecko/erg_history` endpoint)
  - AssetInfoResponse model (for `/crux/asset_info/{token_id}` endpoint)
  - TokenInfoResponse model (for `/crux/token_info/{token_id}` endpoint)
  - SpectrumPriceResponse model (for `/spectrum/price` endpoint)
  - TradingViewResponse models (for `/trading_view/*` endpoints)
- [ ] **2.1.2** Create API error response models
  - Handle HTTP error responses from CRUX API
- [ ] **2.1.3** Add validation and type hints for all models

### 2.2 API Exception Handling
- [ ] **2.2.1** Create `src/ergo_price_mcp/api/exceptions.py`
  - CruxAPIError base exception
  - RateLimitError with retry-after parsing
  - TokenNotFoundError for 404 responses from CRUX
  - APITimeoutError for timeout handling
  - InvalidResponseError for malformed CRUX API responses

### 2.3 HTTP Client Implementation
- [ ] **2.3.1** Create `src/ergo_price_mcp/api/client.py` HTTP client class
  - **Purpose**: Make HTTP requests to CRUX Finance API
  - Async HTTP client using httpx
  - Base URL: https://api.cruxfinance.io
  - Request/response logging
  - Timeout configuration
- [ ] **2.3.2** Implement authentication handling (if required)
  - Check if CRUX API requires API keys
  - API key header injection if needed
- [ ] **2.3.3** Add retry logic with exponential backoff
  - Configurable retry attempts for failed requests to CRUX
  - Jitter for rate limiting
  - Circuit breaker pattern for API outages

### 2.4 CRUX API Endpoint Methods
- [ ] **2.4.1** Implement CoinGecko section endpoints
  - `get_erg_price()` -> calls `GET /coingecko/erg_price`
  - `get_erg_history(days: int = 7)` -> calls `GET /coingecko/erg_history`
- [ ] **2.4.2** Implement CRUX section endpoints
  - `get_asset_info(token_id: str)` -> calls `GET /crux/asset_info/{token_id}`
  - `get_token_info(token_id: str)` -> calls `GET /crux/token_info/{token_id}`
  - `get_circulating_supply(token_id: str)` -> calls `GET /crux/circulating_supply/{token_id}`
  - `get_gold_oracle_history()` -> calls `GET /crux/gold_oracle_history`
- [ ] **2.4.3** Implement Spectrum section endpoints
  - `get_spectrum_price()` -> calls `GET /spectrum/price`
  - `get_spectrum_price_stats()` -> calls `GET /spectrum/price_stats`
  - `get_spectrum_token_list()` -> calls `GET /spectrum/token_list`
- [ ] **2.4.4** Implement TradingView section endpoints
  - `get_trading_view_symbols()` -> calls `GET /trading_view/symbols`
  - `get_trading_view_history(symbol, from_date, to_date)` -> calls `GET /trading_view/history`
  - `search_trading_view(query: str)` -> calls `GET /trading_view/search`

### 2.5 HTTP Client Testing
- [ ] **2.5.1** Create unit tests for HTTP client
  - Mock HTTP responses from CRUX API endpoints
  - Test error handling scenarios
  - Test retry logic
- [ ] **2.5.2** Create integration tests with real CRUX API
  - Test actual HTTP calls to https://api.cruxfinance.io
  - Test rate limiting behavior
  - Test timeout handling

---

## Phase 3: Basic MCP Server Setup ⚙️

### 3.1 MCP Server Foundation
- [ ] **3.1.1** Create `src/ergo_price_mcp/server.py`
  - Import MCP Server from python SDK
  - Basic server initialization with name and version
  - Stdio transport setup for development
- [ ] **3.1.2** Implement server capabilities declaration
  - Tools capability (we'll expose CRUX API calls as tools)
  - Resources capability (for static data)
  - Basic server info handler

### 3.2 MCP Protocol Handlers
- [ ] **3.2.1** Implement initialization handler
  - Server capabilities negotiation
  - Client information logging
- [ ] **3.2.2** Add basic error handling
  - MCP protocol error responses
  - Logging of all requests/responses
- [ ] **3.2.3** Create health check mechanism
  - Server status monitoring
  - CRUX API connectivity checks

### 3.3 Development Setup
- [ ] **3.3.1** Create development runner script
  - `python -m ergo_price_mcp.server` entry point
  - Development logging configuration
- [ ] **3.3.2** Test basic MCP server connectivity
  - Use MCP client to test connection
  - Verify protocol handshake
- [ ] **3.3.3** Create debug mode with verbose logging

---

## Phase 4: MCP Tools Implementation (CRUX API Bridges) 🛠️

### 4.1 Price Lookup Tools
- [ ] **4.1.1** Create `src/ergo_price_mcp/tools/price_tools.py`
- [ ] **4.1.2** Implement `get_erg_price` MCP tool
  - **Purpose**: Bridge to CRUX `/coingecko/erg_price` endpoint
  - Tool description and parameters for LLM
  - Call CRUX API client internally
  - Format CRUX API response for LLM consumption
  - Error handling with user-friendly messages
- [ ] **4.1.3** Implement `get_erg_history` MCP tool
  - **Purpose**: Bridge to CRUX `/coingecko/erg_history` endpoint
  - Accept time period parameter (days)
  - Return formatted price history from CRUX
  - Handle date range validation
- [ ] **4.1.4** Implement `get_spectrum_price` MCP tool
  - **Purpose**: Bridge to CRUX `/spectrum/price` endpoint
  - Current Spectrum DEX prices from CRUX API
- [ ] **4.1.5** Implement `get_spectrum_price_stats` MCP tool
  - **Purpose**: Bridge to CRUX `/spectrum/price_stats` endpoint
  - 24h volume, change percentage from CRUX

### 4.2 Asset Information Tools
- [ ] **4.2.1** Create `src/ergo_price_mcp/tools/asset_tools.py`
- [ ] **4.2.2** Implement `get_asset_info` MCP tool
  - **Purpose**: Bridge to CRUX `/crux/asset_info/{token_id}` endpoint
  - Token ID parameter validation
  - Call CRUX API and format response
  - Handle token not found gracefully
- [ ] **4.2.3** Implement `get_token_info` MCP tool
  - **Purpose**: Bridge to CRUX `/crux/token_info/{token_id}` endpoint
  - Token details from CRUX API
- [ ] **4.2.4** Implement `get_circulating_supply` MCP tool
  - **Purpose**: Bridge to CRUX `/crux/circulating_supply/{token_id}` endpoint
  - Current circulating supply from CRUX

### 4.3 Market Data Tools
- [ ] **4.3.1** Create `src/ergo_price_mcp/tools/market_tools.py`
- [ ] **4.3.2** Implement `get_gold_oracle_history` MCP tool
  - **Purpose**: Bridge to CRUX `/crux/gold_oracle_history` endpoint
  - Historical gold price data from CRUX
- [ ] **4.3.3** Implement `get_trading_view_symbols` MCP tool
  - **Purpose**: Bridge to CRUX `/trading_view/symbols` endpoint
  - Available trading symbols from CRUX
- [ ] **4.3.4** Implement `get_trading_view_history` MCP tool
  - **Purpose**: Bridge to CRUX `/trading_view/history` endpoint
  - OHLCV data from CRUX API
- [ ] **4.3.5** Implement `search_tokens` MCP tool
  - **Purpose**: Bridge to CRUX `/trading_view/search` endpoint
  - Token search via CRUX API

### 4.4 Tool Registration & Testing
- [ ] **4.4.1** Register all tools with MCP server
  - Proper tool schemas and descriptions for LLM
  - Parameter validation before calling CRUX API
- [ ] **4.4.2** Create unit tests for each tool
  - Mock CRUX API responses
  - Test parameter validation
  - Test error scenarios
- [ ] **4.4.3** Test tools with actual MCP client
  - Verify tool discovery
  - Test tool execution (actual calls to CRUX)
  - Validate response formats

---

## Phase 5: MCP Resources Implementation 📚

### 5.1 Static Resources
- [ ] **5.1.1** Create `src/ergo_price_mcp/resources/static_resources.py`
- [ ] **5.1.2** Implement supported tokens list resource
  - URI: `ergo://tokens/supported`
  - Get token list from CRUX `/spectrum/token_list` endpoint
- [ ] **5.1.3** Implement API status resource
  - URI: `ergo://status/api`
  - Health checks for CRUX API endpoints
- [ ] **5.1.4** Implement market overview resource
  - URI: `ergo://market/overview`
  - Aggregate data from multiple CRUX endpoints

### 5.2 Dynamic Resources
- [ ] **5.2.1** Create `src/ergo_price_mcp/resources/dynamic_resources.py`
- [ ] **5.2.2** Implement token price resources
  - URI pattern: `ergo://prices/{token_id}`
  - Real-time price data from CRUX API
- [ ] **5.2.3** Implement price history resources
  - URI pattern: `ergo://history/{token_id}`
  - Historical data from CRUX API
- [ ] **5.2.4** Implement trading pairs resources
  - URI pattern: `ergo://pairs/{base_token}`
  - Trading pairs from CRUX API

### 5.3 Resource Handler Registration
- [ ] **5.3.1** Register all resources with MCP server
  - List resources handler
  - Read resource handler (calls CRUX API)
- [ ] **5.3.2** Add resource caching logic
  - Cache CRUX API responses appropriately
  - Cache static resources longer
  - Cache dynamic resources briefly
- [ ] **5.3.3** Test resource access and updates

---

## Phase 6: Caching & Performance 🚀

### 6.1 Cache Implementation
- [ ] **6.1.1** Create `src/ergo_price_mcp/cache/memory_cache.py`
  - **Purpose**: Cache CRUX API responses to reduce API calls
  - In-memory LRU cache with TTL
  - Thread-safe cache operations
  - Cache statistics tracking
- [ ] **6.1.2** Implement cache decorators
  - Tool response caching (cache CRUX API responses)
  - Resource response caching
  - Configurable TTL per CRUX endpoint
- [ ] **6.1.3** Add cache warming strategies
  - Pre-load frequently accessed CRUX data
  - Background refresh for expired data

### 6.2 Rate Limiting (for CRUX API calls)
- [ ] **6.2.1** Implement CRUX API rate limiting
  - Per-endpoint rate limits for CRUX
  - Sliding window rate limiting
  - Parse rate limit headers from CRUX responses
- [ ] **6.2.2** Add request queuing
  - Queue requests during CRUX rate limits
  - Priority queue for different CRUX request types
- [ ] **6.2.3** Implement circuit breaker
  - Fail fast during CRUX API outages
  - Automatic recovery detection

### 6.3 Performance Optimization
- [ ] **6.3.1** Add request batching where possible
  - Batch multiple CRUX API calls if supported
  - Optimize CRUX API call patterns
- [ ] **6.3.2** Implement connection pooling
  - Reuse HTTP connections to CRUX API
  - Connection timeout management
- [ ] **6.3.3** Add performance monitoring
  - Track CRUX API request timing
  - Cache hit rate tracking
  - CRUX API response time monitoring

---

## Phase 7: MCPO Integration & Testing 🧪

### 7.1 MCPO Proxy Setup
- [ ] **7.1.1** Create MCPO configuration file
  - JSON config for MCP server command
  - Environment variable setup
- [ ] **7.1.2** Test MCP server with MCPO proxy
  - Start server with `uvx mcpo --port 8000 --api-key "secret" -- uv run python -m ergo_price_mcp.server`
  - Verify OpenAPI schema generation for our CRUX bridge tools
  - Test API endpoints at localhost:8000
- [ ] **7.1.3** Create startup scripts
  - Development startup script
  - Production startup script

### 7.2 Integration Testing
- [ ] **7.2.1** Create end-to-end test suite
  - Test MCP protocol communication
  - Test MCPO proxy integration
  - Test actual CRUX API interactions
- [ ] **7.2.2** Performance testing
  - Load testing with multiple requests to CRUX
  - Memory usage profiling
  - Stress testing CRUX rate limits
- [ ] **7.2.3** Error scenario testing
  - CRUX API downtime simulation
  - Network timeout testing
  - Invalid parameter handling

### 7.3 Claude Desktop Integration
- [ ] **7.3.1** Create Claude Desktop configuration
  - JSON config file setup
  - Environment variable configuration
- [ ] **7.3.2** Test with Claude Desktop
  - Server discovery and connection
  - Tool execution through Claude (calls CRUX API)
  - Resource access verification
- [ ] **7.3.3** Document integration steps
  - Step-by-step setup guide
  - Troubleshooting common issues

---

## Phase 8: Documentation & Deployment 📖

### 8.1 Documentation
- [ ] **8.1.1** Create comprehensive API reference
  - All MCP tools and their parameters
  - How each tool maps to CRUX API endpoints
  - All resources and their URIs
  - Response format examples
- [ ] **8.1.2** Write deployment guide
  - Local development setup
  - Production deployment options
  - Docker containerization
- [ ] **8.1.3** Create troubleshooting guide
  - Common CRUX API error scenarios
  - Performance tuning tips
  - Debugging techniques

### 8.2 Docker & Containerization
- [ ] **8.2.1** Create Dockerfile
  - Multi-stage build for production
  - Minimal base image
  - Health check configuration
- [ ] **8.2.2** Create docker-compose.yml
  - Development environment
  - Environment variable setup
  - Volume mounting for development
- [ ] **8.2.3** Test containerized deployment
  - Build and run Docker image
  - Test with MCPO proxy in container
  - Verify CRUX API connectivity

### 8.3 CI/CD Pipeline
- [ ] **8.3.1** Create GitHub Actions workflow
  - Automated testing on PR
  - Code quality checks (black, isort, mypy)
  - Test coverage reporting
- [ ] **8.3.2** Add release automation
  - Version tagging
  - Docker image publishing
  - PyPI package publishing
- [ ] **8.3.3** Set up monitoring
  - Health check endpoints
  - Metrics collection
  - Error alerting

---

## Testing Checklist ✅

### Unit Tests
- [ ] HTTP client methods (CRUX API calls)
- [ ] MCP tool functions
- [ ] Resource handlers
- [ ] Cache operations
- [ ] Error handling

### Integration Tests
- [ ] MCP protocol communication
- [ ] CRUX API integration (real HTTP calls)
- [ ] MCPO proxy functionality
- [ ] Claude Desktop integration

### Performance Tests
- [ ] Load testing (100+ concurrent requests to CRUX)
- [ ] Memory usage profiling
- [ ] Cache performance benchmarks
- [ ] CRUX API rate limit handling

---

## Known Issues & Risks ⚠️

### Technical Risks
- [ ] **CRUX API Rate Limiting**: Rate limits unknown, need to discover
- [ ] **CRUX API Stability**: External API reliability dependency
- [ ] **Token ID Format**: Validation of Ergo token ID format for CRUX calls
- [ ] **Data Consistency**: Price data synchronization across CRUX endpoints

### Implementation Challenges
- [ ] **Error Handling**: Graceful degradation when CRUX API is down
- [ ] **Caching Strategy**: Balance between freshness and CRUX API usage
- [ ] **Resource Usage**: Memory management for CRUX response data
- [ ] **Authentication**: CRUX API key management if required

### Deployment Considerations
- [ ] **Environment Variables**: Secure API key storage for CRUX
- [ ] **Network Access**: Firewall rules for CRUX API access
- [ ] **Monitoring**: Health checks and alerting setup
- [ ] **Scaling**: Handle multiple concurrent CRUX API calls

---

## Success Criteria 🎯

### Minimum Viable Product (MVP)
- [ ] **Basic MCP server** responding to protocol messages
- [ ] **Core price tools** working (calling CRUX `/coingecko/erg_price`, `/crux/asset_info`)
- [ ] **MCPO integration** with working OpenAPI endpoints
- [ ] **Error handling** for CRUX API failure scenarios
- [ ] **Basic caching** to avoid excessive CRUX API calls

### Production Ready
- [ ] **All CRUX endpoints** accessible via MCP tools
- [ ] **Comprehensive error handling** for CRUX API issues
- [ ] **Performance optimized** with caching and rate limiting for CRUX
- [ ] **Full test coverage** (>90%)
- [ ] **Documentation complete** with CRUX API mapping examples
- [ ] **Deployment ready** with Docker and CI/CD

### Future Enhancements
- [ ] **Real-time updates** if CRUX API supports WebSockets
- [ ] **Data aggregation** across multiple CRUX endpoints
- [ ] **Enhanced caching** strategies for CRUX data
- [ ] **Monitoring** of CRUX API health and performance

---

**Next Steps**: Start with Phase 1.1 - Project Structure Setup
**Key Focus**: We are building an HTTP client to consume CRUX Finance API and expose it via MCP tools 