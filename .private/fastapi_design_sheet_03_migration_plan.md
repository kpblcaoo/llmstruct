# FastAPI Design Sheet #03: Migration to Custom Implementation

**Date**: 2024-03-26  
**Author**: Claude + @kpblcaoo  
**Status**: Design Phase  
**Related**: fastapi_design_sheet_01_architecture.md, fastapi_design_sheet_02_implementation.md  

---

## 🎯 MIGRATION STRATEGY OVERVIEW

### Why Migrate from FastAPI?

**Performance Bottlenecks** (when they occur):
- CLI subprocess overhead becomes significant at scale
- FastAPI's reflection-heavy nature impacts response times
- Memory usage grows with concurrent requests
- WebSocket handling limitations

**Custom Implementation Benefits**:
- Direct integration with core engine (no CLI bridge)
- Optimized memory usage and performance
- Custom protocol support (binary, streaming)
- Fine-grained control over resource management

### Migration Triggers

**Migrate when**:
- Response time > 200ms for 95th percentile
- Memory usage > 1GB per instance
- Concurrent requests > 1000/second required
- Custom features need deep engine integration

---

## 🏗️ CUSTOM ARCHITECTURE DESIGN

### Target Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Layer    │    │   Core Engine    │    │   Data Layer    │
│                 │    │                  │    │                 │
│ • Request       │───▶│ • Scanner        │───▶│ • JSON Store    │
│ • Response      │    │ • Context Mgr    │    │ • Cache         │
│ • WebSocket     │    │ • Task Mgr       │    │ • File System   │
│ • Auth          │    │ • AI Bridge      │    │ • Git           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Engine Design
```python
# src/llmstruct/engine/core.py
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator
import asyncio

class CoreEngine:
    """High-performance core engine replacing CLI calls"""
    
    def __init__(self):
        self.scanner = ProjectScanner()
        self.context_manager = ContextManager()
        self.task_manager = TaskManager()
        self.cache = HighPerformanceCache()
        
    async def scan_project_stream(
        self, 
        options: ScanOptions
    ) -> AsyncIterator[ScanProgress]:
        """Stream scan progress in real-time"""
        async for progress in self.scanner.scan_async(options):
            yield progress
    
    async def get_optimized_context(
        self, 
        mode: ContextMode, 
        query_hint: str = None
    ) -> ContextResult:
        """Get context with AI-driven optimization"""
        cache_key = self.cache.generate_key(mode, query_hint)
        
        if cached := await self.cache.get(cache_key):
            return cached
            
        result = await self.context_manager.build_context(mode, query_hint)
        await self.cache.set(cache_key, result, ttl=3600)
        
        return result
```

---

## 🔄 MIGRATION PHASES

### Phase 1: Preparation (2 weeks)

#### Week 1: Core Engine Development
```python
# src/llmstruct/engine/scanner.py
class ProjectScanner:
    """High-performance project scanner replacing CLI scan"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.language_parsers = LanguageParserRegistry()
        
    async def scan_async(self, options: ScanOptions) -> AsyncIterator[ScanProgress]:
        """Asynchronous scanning with progress reporting"""
        files = await self._discover_files(options)
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            try:
                result = await self._process_file(file_path)
                yield ScanProgress(
                    current=i + 1,
                    total=total_files,
                    file=file_path,
                    result=result
                )
            except Exception as e:
                yield ScanProgress(
                    current=i + 1,
                    total=total_files,
                    file=file_path,
                    error=str(e)
                )
    
    async def _process_file(self, file_path: Path) -> FileAnalysis:
        """Process single file with appropriate parser"""
        parser = self.language_parsers.get_parser(file_path.suffix)
        return await parser.analyze_async(file_path)
```

#### Week 2: Context Engine Optimization
```python
# src/llmstruct/engine/context.py
class ContextManager:
    """AI-optimized context generation"""
    
    def __init__(self):
        self.ai_optimizer = ContextOptimizer()
        self.token_counter = TokenCounter()
        
    async def build_context(
        self, 
        mode: ContextMode, 
        query_hint: str = None
    ) -> ContextResult:
        """Build optimized context based on mode and query"""
        
        # AI-driven context selection
        if query_hint:
            relevance_scores = await self.ai_optimizer.score_files(query_hint)
            files = self._select_by_relevance(relevance_scores, mode)
        else:
            files = self._select_by_mode(mode)
        
        context_data = {}
        token_count = 0
        
        for file_path in files:
            content = await self._get_file_context(file_path, mode)
            tokens = self.token_counter.count(content)
            
            if token_count + tokens > self._get_token_limit(mode):
                break
                
            context_data[str(file_path)] = content
            token_count += tokens
        
        return ContextResult(
            data=context_data,
            token_count=token_count,
            mode=mode,
            optimization_applied=query_hint is not None
        )
```

### Phase 2: HTTP Layer Development (2 weeks)

#### Week 3: Custom HTTP Server
```python
# src/llmstruct/server/http.py
import asyncio
from typing import Dict, Callable, Any
import json

class HighPerformanceHTTPServer:
    """Custom HTTP server optimized for llmstruct workloads"""
    
    def __init__(self, engine: CoreEngine):
        self.engine = engine
        self.routes: Dict[str, Callable] = {}
        self.middleware_stack = []
        
    def route(self, path: str, method: str = "GET"):
        def decorator(handler):
            self.routes[f"{method}:{path}"] = handler
            return handler
        return decorator
    
    async def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        """High-performance request handling"""
        route_key = f"{request.method}:{request.path}"
        
        if handler := self.routes.get(route_key):
            # Apply middleware
            for middleware in self.middleware_stack:
                request = await middleware.process_request(request)
            
            # Execute handler
            response = await handler(request, self.engine)
            
            # Apply response middleware
            for middleware in reversed(self.middleware_stack):
                response = await middleware.process_response(response)
                
            return response
        
        return HTTPResponse(status=404, body={"error": "Not found"})

# Usage
server = HighPerformanceHTTPServer(engine)

@server.route("/api/v1/project/scan", "POST")
async def scan_project(request: HTTPRequest, engine: CoreEngine):
    options = ScanOptions(**request.json)
    
    # Stream response
    async def stream_generator():
        yield '{"status": "started", "data": ['
        first = True
        
        async for progress in engine.scan_project_stream(options):
            if not first:
                yield ","
            yield json.dumps(progress.dict())
            first = False
            
        yield "]}"
    
    return StreamingResponse(stream_generator(), media_type="application/json")
```

#### Week 4: WebSocket & Real-time Features
```python
# src/llmstruct/server/websocket.py
class HighPerformanceWebSocket:
    """Custom WebSocket implementation for real-time updates"""
    
    def __init__(self, engine: CoreEngine):
        self.engine = engine
        self.connections: Dict[str, WebSocketConnection] = {}
        
    async def handle_connection(self, connection: WebSocketConnection):
        """Handle new WebSocket connection"""
        connection_id = self._generate_connection_id()
        self.connections[connection_id] = connection
        
        try:
            async for message in connection:
                await self._handle_message(connection_id, message)
        finally:
            del self.connections[connection_id]
    
    async def _handle_message(self, connection_id: str, message: dict):
        """Handle incoming WebSocket message"""
        if message["type"] == "scan_request":
            await self._handle_scan_request(connection_id, message)
        elif message["type"] == "context_request":
            await self._handle_context_request(connection_id, message)
    
    async def _handle_scan_request(self, connection_id: str, message: dict):
        """Handle real-time scan request"""
        connection = self.connections[connection_id]
        options = ScanOptions(**message["data"])
        
        async for progress in self.engine.scan_project_stream(options):
            await connection.send({
                "type": "scan_progress",
                "data": progress.dict()
            })
```

### Phase 3: Migration Execution (1 week)

#### Migration Strategy
```python
# src/llmstruct/migration/migrator.py
class APIServerMigrator:
    """Handles migration from FastAPI to custom implementation"""
    
    def __init__(self):
        self.fastapi_server = None
        self.custom_server = None
        self.traffic_splitter = TrafficSplitter()
        
    async def gradual_migration(self, migration_percentage: float = 0.1):
        """Gradually migrate traffic from FastAPI to custom server"""
        
        # Start custom server
        await self.custom_server.start()
        
        # Configure traffic splitting
        self.traffic_splitter.configure(
            fastapi_weight=1.0 - migration_percentage,
            custom_weight=migration_percentage
        )
        
        # Monitor performance
        metrics = await self._collect_metrics(duration=3600)  # 1 hour
        
        if metrics.custom_performance > metrics.fastapi_performance:
            return True  # Safe to increase traffic
        else:
            # Rollback if performance degrades
            await self._rollback(migration_percentage / 2)
            return False

class TrafficSplitter:
    """Split traffic between FastAPI and custom implementation"""
    
    async def route_request(self, request: HTTPRequest) -> HTTPResponse:
        """Route request based on configured weights"""
        if self._should_route_to_custom():
            return await self.custom_server.handle(request)
        else:
            return await self.fastapi_server.handle(request)
```

---

## 🚀 PERFORMANCE OPTIMIZATIONS

### Memory Management
```python
# src/llmstruct/engine/memory.py
class MemoryOptimizedCache:
    """Custom cache optimized for llmstruct data patterns"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}
        
    async def get(self, key: str) -> Any:
        """Get with LRU eviction"""
        if entry := self.cache.get(key):
            self.access_times[key] = time.time()
            return entry.data
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set with memory management"""
        serialized = self._serialize(value)
        size = len(serialized)
        
        # Evict if necessary
        while self._get_memory_usage() + size > self.max_memory:
            await self._evict_lru()
        
        self.cache[key] = CacheEntry(
            data=value,
            size=size,
            expires_at=time.time() + ttl
        )
```

### Connection Pooling
```python
# src/llmstruct/server/connection_pool.py
class ConnectionPool:
    """Optimized connection management"""
    
    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_queue = asyncio.Queue()
        
    async def acquire_connection(self) -> Connection:
        """Acquire connection with backpressure"""
        if self.active_connections < self.max_connections:
            self.active_connections += 1
            return Connection()
        else:
            # Wait for available connection
            return await self.connection_queue.get()
    
    async def release_connection(self, connection: Connection):
        """Release connection back to pool"""
        self.active_connections -= 1
        await self.connection_queue.put(connection)
```

---

## 📊 MIGRATION MONITORING

### Performance Metrics
```python
# src/llmstruct/migration/metrics.py
class MigrationMetrics:
    """Track migration performance and health"""
    
    def __init__(self):
        self.fastapi_metrics = ServerMetrics("fastapi")
        self.custom_metrics = ServerMetrics("custom")
        
    async def collect_comparison_data(self) -> MigrationReport:
        """Collect performance comparison data"""
        fastapi_stats = await self.fastapi_metrics.get_stats()
        custom_stats = await self.custom_metrics.get_stats()
        
        return MigrationReport(
            fastapi={
                "response_time_p95": fastapi_stats.response_time_p95,
                "memory_usage": fastapi_stats.memory_usage,
                "throughput": fastapi_stats.requests_per_second,
                "error_rate": fastapi_stats.error_rate
            },
            custom={
                "response_time_p95": custom_stats.response_time_p95,
                "memory_usage": custom_stats.memory_usage,
                "throughput": custom_stats.requests_per_second,
                "error_rate": custom_stats.error_rate
            },
            improvement_factors={
                "response_time": fastapi_stats.response_time_p95 / custom_stats.response_time_p95,
                "memory": fastapi_stats.memory_usage / custom_stats.memory_usage,
                "throughput": custom_stats.requests_per_second / fastapi_stats.requests_per_second
            }
        )
```

---

## 🔒 COMPATIBILITY MAINTENANCE

### API Contract Preservation
```python
# src/llmstruct/migration/compatibility.py
class APICompatibilityLayer:
    """Ensure API contract compatibility during migration"""
    
    def __init__(self):
        self.schema_validator = SchemaValidator()
        self.response_transformer = ResponseTransformer()
        
    async def validate_compatibility(self, endpoint: str, request: dict, response: dict):
        """Validate that custom implementation maintains API contract"""
        
        # Validate request schema
        await self.schema_validator.validate_request(endpoint, request)
        
        # Validate response schema
        await self.schema_validator.validate_response(endpoint, response)
        
        # Check response time compatibility
        if response.get("processing_time", 0) > self._get_sla_limit(endpoint):
            raise CompatibilityError(f"Response time SLA violated for {endpoint}")

class ResponseTransformer:
    """Transform responses to maintain compatibility"""
    
    async def transform_response(self, custom_response: dict, fastapi_format: dict) -> dict:
        """Transform custom server response to FastAPI format"""
        # Ensure field naming compatibility
        # Handle datetime format consistency
        # Maintain error message structure
        pass
```

---

## ✅ MIGRATION CHECKLIST

### Pre-Migration
- [ ] Core engine performance benchmarked
- [ ] Custom HTTP server tested under load
- [ ] API contract compatibility verified
- [ ] Monitoring and alerting configured
- [ ] Rollback plan prepared

### Migration Execution
- [ ] Traffic splitting at 10% to custom server
- [ ] Performance metrics collected and analyzed
- [ ] Error rates monitored and acceptable
- [ ] Gradual increase to 50% traffic
- [ ] Full migration to custom server
- [ ] FastAPI server gracefully shut down

### Post-Migration
- [ ] Performance targets met or exceeded
- [ ] Memory usage within acceptable limits
- [ ] All API endpoints functional
- [ ] WebSocket connections stable
- [ ] Documentation updated
- [ ] Team trained on new architecture

---

## 🎯 SUCCESS CRITERIA

### Performance Improvements
- **Response Time**: 50-80% improvement in 95th percentile
- **Memory Usage**: 30-50% reduction in baseline memory
- **Throughput**: 300-500% increase in requests/second
- **Resource Efficiency**: 40-60% better CPU utilization

### Functionality Preservation
- **API Compatibility**: 100% backward compatibility maintained
- **Feature Parity**: All FastAPI features available in custom implementation
- **Error Handling**: Consistent error responses and status codes
- **Security**: Maintained or improved security posture

---

*Migration strategy complete. Ready for phased implementation when performance requirements justify the transition.* 