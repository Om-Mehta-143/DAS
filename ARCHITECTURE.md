# Technical Architecture

## Technology Stack Recommendations

### Backend (Orchestrator & API)

**Recommended: Python (FastAPI) or Go**

**Python (FastAPI) - RECOMMENDED FOR MVP**
```
Pros:
✅ Rich security/networking libraries (requests, aiohttp, scapy)
✅ Fast development with FastAPI
✅ Excellent async support
✅ Strong data analysis ecosystem (pandas, matplotlib)
✅ Easy integration with ML for anomaly detection (future)
✅ Large security community

Cons:
⚠️ Slightly slower than Go
⚠️ GIL limitations (mitigated by asyncio)

Best For: Rapid MVP development, complex attack logic
```

**Alternative: Go**
```
Pros:
✅ Excellent concurrency (goroutines)
✅ High performance
✅ Built-in HTTP/2 support
✅ Easy deployment (single binary)
✅ Low resource usage

Cons:
⚠️ Steeper learning curve
⚠️ Fewer attack simulation libraries
⚠️ Longer development time

Best For: Production-scale, high-performance systems
```

**Recommendation:** Start with Python/FastAPI, migrate critical paths to Go if needed

---

### Traffic Nodes (Attack Agents)

**Recommended: Python with aiohttp**

```python
# Lightweight, async HTTP client
# Perfect for distributed attack simulation
# Can handle 1000+ concurrent connections per node

Technologies:
- aiohttp: Async HTTP client/server
- httpx: Modern HTTP client with HTTP/2
- playwright: Browser automation (for JS-heavy targets)
- asyncio: Concurrency framework
```

**Container:** Docker with Alpine Linux base
- Small footprint (~50MB per node)
- Fast startup
- Easy orchestration

---

### Monitoring & Analysis Engine

**Recommended: Python + ClickHouse/TimescaleDB**

**Data Storage:**
- **ClickHouse** (RECOMMENDED): Columnar database for analytics
  - Excellent for time-series data
  - Blazing fast aggregations
  - Built-in visualization support
  
- **Alternative: TimescaleDB**: PostgreSQL extension for time-series
  - Easier setup
  - SQL familiar syntax
  - Good for smaller scale

**Processing:**
- **Pandas**: Data analysis
- **NumPy**: Numerical computations
- **Matplotlib/Plotly**: Visualization

---

### Control Dashboard (Frontend)

**Recommended: React + Next.js**

```
Modern Stack:
- React 18: Component-based UI
- Next.js: SSR, routing, API routes
- TypeScript: Type safety
- TailwindCSS: Rapid styling
- Recharts: Data visualization
- Zustand: State management
- Socket.io: Real-time updates
```

**Alternative: Svelte/SvelteKit**
- Faster, smaller bundle size
- Simpler state management
- Steeper learning curve

---

### Infrastructure & Orchestration

**Container Orchestration:**
- **Docker Compose**: Development & small deployments
- **Kubernetes**: Production scale (future)

**Message Queue (for node coordination):**
- **Redis + Bull Queue**: Simple, fast (RECOMMENDED)
- **RabbitMQ**: More features, more complex
- **NATS**: Lightweight, cloud-native

**Monitoring Stack:**
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Loki**: Log aggregation

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CONTROL DASHBOARD                          │
│                     (React + Next.js + Socket.io)                   │
└────────────┬────────────────────────────────────────────────────────┘
             │ REST API + WebSocket
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│  │   Scenario   │  │   Traffic    │  │   Results              │   │
│  │   Manager    │  │ Coordinator  │  │   Aggregator           │   │
│  └──────────────┘  └──────────────┘  └────────────────────────┘   │
└─────────┬──────────────────┬────────────────────┬───────────────────┘
          │                  │                    │
          │                  │                    │
          ▼                  ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────────────────────┐
│  Redis Queue     │ │  Attack Nodes    │ │  Analysis Engine    │
│  (Job Queue)     │ │  (Docker Fleet)  │ │  (Python + DB)      │
└──────────────────┘ └──────────────────┘ └─────────────────────┘
          │                  │                    │
          └──────────────────┼────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  ClickHouse  │
                    │  (Metrics)   │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Grafana      │
                    │ (Optional)   │
                    └──────────────┘
```

---

## Detailed Component Architecture

### 1. Orchestration Layer (Backend)

**Technology:** FastAPI (Python 3.11+)

**Modules:**

```
orchestrator/
├── api/
│   ├── scenarios.py       # CRUD for attack scenarios
│   ├── tests.py          # Test execution endpoints
│   ├── results.py        # Results retrieval
│   └── nodes.py          # Node management
├── core/
│   ├── scenario_engine.py    # Attack scenario logic
│   ├── traffic_coordinator.py # Node coordination
│   ├── config.py             # Configuration management
│   └── models.py             # Data models (Pydantic)
├── attack_modules/
│   ├── base.py              # Base attack class
│   ├── credential_stuffing.py
│   ├── brute_force.py
│   ├── slow_scraping.py
│   ├── api_enumeration.py
│   ├── burst_attack.py
│   └── distributed_low_rate.py
├── queue/
│   ├── producer.py          # Job submission
│   └── consumer.py          # Job processing
└── utils/
    ├── logging.py
    ├── metrics.py
    └── validators.py
```

**Key Design Patterns:**

1. **Strategy Pattern** for attack modules
```python
class AttackModule(ABC):
    @abstractmethod
    async def generate_request(self) -> Request:
        pass
    
    @abstractmethod
    async def analyze_response(self, response: Response) -> Metrics:
        pass
```

2. **Factory Pattern** for scenario creation
```python
class ScenarioFactory:
    @staticmethod
    def create(scenario_type: str, config: dict) -> AttackModule:
        return attack_modules[scenario_type](config)
```

3. **Observer Pattern** for real-time updates
```python
class TestExecutor:
    def __init__(self):
        self.observers: List[Observer] = []
    
    def notify(self, event: Event):
        for observer in self.observers:
            await observer.update(event)
```

---

### 2. Distributed Traffic Nodes

**Technology:** Python with aiohttp, packaged as Docker containers

**Node Architecture:**

```
attack_node/
├── main.py                  # Entry point
├── client.py               # HTTP client logic
├── executor.py             # Attack execution
├── reporting.py            # Metrics reporting
└── config.py               # Node configuration
```

**Node Behavior:**

```python
# Pseudo-code
class AttackNode:
    async def start(self):
        # 1. Connect to orchestrator
        await self.register()
        
        # 2. Listen for instructions
        while True:
            instruction = await self.receive_instruction()
            
            # 3. Execute attack pattern
            results = await self.execute(instruction)
            
            # 4. Report metrics
            await self.report(results)
    
    async def execute(self, instruction):
        # Generate requests according to pattern
        # Handle timing, sessions, payloads
        # Collect response metrics
        pass
```

**Communication Protocol:**

```json
// Instruction from Orchestrator
{
  "attack_id": "uuid",
  "module": "credential_stuffing",
  "target": "https://example.com/login",
  "parameters": {
    "rate": 10,  // requests per second
    "duration": 300,  // seconds
    "credentials": "s3://bucket/creds.txt"
  },
  "timing": {
    "jitter": 0.2,  // 20% random variation
    "ramp_up": 30   // seconds
  }
}

// Report to Orchestrator
{
  "attack_id": "uuid",
  "node_id": "node-01",
  "timestamp": "2026-02-11T10:30:45Z",
  "metrics": {
    "requests_sent": 150,
    "responses": {
      "200": 10,
      "401": 135,
      "429": 5  // Rate limited!
    },
    "avg_response_time": 245,  // ms
    "blocked": true,
    "block_timestamp": "2026-02-11T10:30:40Z"
  }
}
```

---

### 3. Monitoring & Analysis Engine

**Technology:** Python + ClickHouse + Pandas

**Data Pipeline:**

```
1. Ingest
   ↓
   [Raw Metrics] → ClickHouse (time-series storage)
   ↓
2. Process
   ↓
   [Analysis Engine] → Pandas DataFrame operations
   ↓
3. Analyze
   ↓
   [Scoring Algorithm] → Effectiveness calculations
   ↓
4. Output
   ↓
   [Results API] → Dashboard / Reports
```

**ClickHouse Schema:**

```sql
CREATE TABLE attack_metrics (
    timestamp DateTime,
    attack_id String,
    node_id String,
    request_id String,
    target_url String,
    status_code UInt16,
    response_time_ms UInt32,
    response_size_bytes UInt32,
    blocked Boolean,
    captcha_presented Boolean,
    session_terminated Boolean,
    error_message String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (attack_id, timestamp);

CREATE TABLE defense_events (
    timestamp DateTime,
    attack_id String,
    event_type String,  -- 'rate_limit', 'captcha', 'block', 'lockout'
    severity String,    -- 'low', 'medium', 'high'
    details String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (attack_id, timestamp);
```

**Analysis Algorithms:**

```python
class DefenseAnalyzer:
    def calculate_effectiveness_score(self, attack_id: str) -> float:
        """
        Score = weighted_sum(
            detection_speed_score,
            blocking_accuracy_score,
            false_positive_score,
            resistance_score
        )
        """
        metrics = self.get_metrics(attack_id)
        
        # Detection speed: How fast was the attack detected?
        detection_speed = self._score_detection_speed(
            metrics.time_to_first_block
        )
        
        # Blocking accuracy: % of malicious requests blocked
        blocking_accuracy = (
            metrics.blocked_requests / metrics.total_requests
        )
        
        # False positive rate: Legitimate traffic affected
        false_positive_rate = self._calculate_false_positives(metrics)
        false_positive_score = 1 - false_positive_rate
        
        # Resistance: Can attack bypass with simple modifications?
        resistance = self._test_bypass_resistance(metrics)
        
        # Weighted scoring
        return (
            0.3 * detection_speed +
            0.4 * blocking_accuracy +
            0.2 * false_positive_score +
            0.1 * resistance
        )
```

---

### 4. Control Dashboard (Frontend)

**Technology:** React + Next.js + TypeScript

**Page Structure:**

```
dashboard/
├── pages/
│   ├── index.tsx              # Home / test overview
│   ├── scenarios/
│   │   ├── index.tsx          # List scenarios
│   │   ├── [id].tsx           # Scenario details
│   │   └── new.tsx            # Create scenario
│   ├── tests/
│   │   ├── index.tsx          # Test history
│   │   ├── [id].tsx           # Test results
│   │   └── compare.tsx        # Compare tests
│   └── nodes/
│       └── index.tsx          # Node management
├── components/
│   ├── ScenarioBuilder/
│   ├── TestExecutionPanel/
│   ├── MetricsVisualization/
│   ├── TimelineChart/
│   └── ComparisonView/
├── hooks/
│   ├── useWebSocket.ts        # Real-time updates
│   ├── useTestExecution.ts
│   └── useMetrics.ts
└── lib/
    ├── api.ts                 # API client
    └── types.ts               # TypeScript types
```

**Real-Time Updates:**

```typescript
// WebSocket connection for live test updates
const useTestUpdates = (testId: string) => {
  const [metrics, setMetrics] = useState<Metrics>({});
  
  useEffect(() => {
    const socket = io(BACKEND_URL);
    
    socket.on(`test:${testId}:update`, (data) => {
      setMetrics(prev => ({
        ...prev,
        ...data
      }));
    });
    
    return () => socket.disconnect();
  }, [testId]);
  
  return metrics;
};
```

---

## Data Flow Example: Running a Test

```
1. USER: Click "Run Test" in Dashboard
   ↓
2. FRONTEND: POST /api/tests/run
   {
     "scenario_id": "cred-stuff-001",
     "nodes": 5,
     "target": "https://example.com"
   }
   ↓
3. ORCHESTRATOR: 
   - Create test record
   - Generate attack instructions
   - Push jobs to Redis queue
   ↓
4. REDIS QUEUE:
   - Job distributed to available nodes
   ↓
5. ATTACK NODES:
   - Pull job from queue
   - Execute attack pattern
   - Send requests to target
   - Report metrics every 1s
   ↓
6. TARGET SYSTEM:
   - Receives requests
   - Applies defenses
   - Returns responses
   ↓
7. MONITORING ENGINE:
   - Receives metrics from nodes
   - Stores in ClickHouse
   - Performs real-time analysis
   - Detects defense triggers
   ↓
8. ORCHESTRATOR:
   - Aggregates results
   - Sends updates via WebSocket
   ↓
9. FRONTEND:
   - Updates live metrics
   - Renders timeline
   - Shows real-time status
   ↓
10. TEST COMPLETE:
    - Final analysis run
    - Generate report
    - Store results
    - Notify user
```

---

## Security & Safety Considerations

### Preventing Misuse

1. **Target Verification**
   - Require DNS TXT record verification
   - Support allowlist of domains
   - Reject targets without proof of ownership

2. **Rate Limiting**
   - Hard limits on attack intensity
   - Cooldown periods between tests
   - Monitoring of platform usage

3. **Audit Logging**
   - All tests logged with user identity
   - IP addresses of nodes recorded
   - Detailed activity logs

4. **Deployment Control**
   - Nodes only deployable in controlled environments
   - API keys required for node registration
   - Revocable node credentials

### Legal Safeguards

```markdown
Required Before Test Execution:
1. ✅ Domain ownership verification
2. ✅ Terms of service acceptance
3. ✅ No third-party testing without explicit permission
4. ✅ Compliance with local laws
5. ✅ Rate limit thresholds configured
```

---

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
services:
  orchestrator:
    build: ./orchestrator
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - CLICKHOUSE_URL=clickhouse://clickhouse:9000
  
  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
  
  redis:
    image: redis:7-alpine
  
  clickhouse:
    image: clickhouse/clickhouse-server:latest
  
  attack-node:
    build: ./attack-node
    deploy:
      replicas: 3
```

### Production Considerations

1. **Orchestrator**: Deploy on Kubernetes with auto-scaling
2. **Nodes**: Serverless containers (AWS Fargate, Cloud Run)
3. **Database**: Managed ClickHouse (Altinity, ClickHouse Cloud)
4. **Frontend**: Vercel, Netlify, or CloudFront + S3
5. **Queue**: Managed Redis (AWS ElastiCache, Redis Labs)

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Nodes supported | 100+ concurrent |
| Requests/second per node | 1,000+ |
| Orchestrator latency | <50ms |
| Dashboard update frequency | Real-time (1s) |
| Data retention | 90 days |
| Test result query time | <2s |

---

## Future Enhancements

### Phase 2 Features
- ML-based anomaly detection
- Auto-tuning recommendations
- Compliance report templates
- Integration with CI/CD (GitHub Actions, GitLab CI)

### Phase 3 Features
- Browser automation attacks (Playwright-based)
- API fuzzing capabilities
- Custom attack module SDK
- Multi-tenant support
- Marketplace for attack scenarios

