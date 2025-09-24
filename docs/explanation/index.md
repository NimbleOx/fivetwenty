# Explanations - Understanding-Oriented Content

## What are Explanations?

Explanations are **understanding-oriented** content that provide context, background knowledge, and deep understanding of concepts, design decisions, and the broader context of FiveTwenty. They help you understand the "why" behind the technology.

## When to Use Explanations

**Use explanations when you:**

- **Want to understand** the reasoning behind design decisions
- **Need context** for why something works the way it does
- **Seek background knowledge** about trading concepts
- **Want to make informed** architectural choices
- **Need to understand** trade-offs and alternatives
- **Are designing** your own trading systems

**Don't use explanations when you:**

- Want to learn step-by-step (use [Tutorials](../tutorials/index.md))
- Need to solve a specific problem (use [How-to Guides](../how-to-guides/index.md))
- Want to look up API details (use [API Reference](../api-reference/index.md))

## Understanding Areas

Our explanations cover both technical architecture and domain knowledge:

### **Architecture & Design**
Understand the technical decisions behind FiveTwenty.

- **[SDK Architecture](sdk-architecture.md)** - Overall design philosophy and component relationships
- **[Async vs Sync Design](./async-vs-sync.md)** - Why async-first and when to use each approach
- **[Error Handling Philosophy](./error-handling.md)** - Approach to error management and recovery
- **[Configuration Patterns](./configuration.md)** - How configuration works and why

### **Domain Knowledge**
Understand the financial trading concepts that inform SDK design.

- **[Forex Trading Concepts](forex-trading-concepts.md)** - Currency trading fundamentals and OANDA specifics
- **[Market Data & Streaming](./streaming.md)** - How market data works and why streaming matters
- **[Best Practices & Patterns](./best-practices.md)** - Established patterns for successful trading systems

## Explanation Characteristics

### **Context-Providing**
Explanations help you understand the broader picture:

- **Why decisions were made** rather than what decisions were made
- **Historical context** that led to current approaches
- **Industry standards** and how OANDA fits
- **Alternative approaches** and their trade-offs

### **Conceptual Understanding**
Build deep knowledge of underlying concepts:

- **Mental models** for how systems work
- **Relationships** between different components
- **Implications** of design choices
- **Consequences** of different approaches

### **Insight-Oriented**
Provide insights that inform better decisions:

- **When to use** different approaches
- **Performance characteristics** of various patterns
- **Security implications** of architectural choices
- **Scalability considerations** for production systems

## Key Topics Explored

### **Architectural Principles**

**Async-First Design:**

- Why modern Python trading systems benefit from async patterns
- How async improves throughput and resource utilization
- When sync wrappers are appropriate
- Performance implications of different concurrency models

**Error Handling Strategy:**

- Philosophy of "explicit is better than implicit"
- How OANDA API errors map to Python exceptions
- Recovery strategies for different error types
- Building resilient trading systems

**Data Model Design:**

- Why Pydantic models provide safety and performance
- How decimal precision prevents financial calculation errors
- Field validation and its importance in trading
- Serialization patterns for API communication

### **Financial Technology Context**

**Market Data Architecture:**

- Real-time vs historical data access patterns
- Why streaming is crucial for modern trading
- Latency considerations and their business impact
- Data quality and validation strategies

**Trading System Patterns:**

- Event-driven architecture for trading systems
- Risk management integration points
- Order management system design
- Portfolio and position tracking approaches

**Regulatory and Risk Considerations:**

- Why practice environments are essential
- Risk management as a first-class concern
- Audit trails and compliance requirements
- Disaster recovery and business continuity

## How Explanations Help

### **Informed Decision Making**
Understanding the "why" helps you make better choices:

- Choose appropriate patterns for your use case
- Understand performance and scalability implications
- Make informed trade-offs between alternatives
- Design systems that align with best practices

### **Better Implementation**
Deep understanding leads to better code:

- Write more maintainable and robust applications
- Anticipate and handle edge cases appropriately
- Optimize for the right metrics
- Design for long-term success

### **Strategic Planning**
Conceptual knowledge enables strategic thinking:

- Plan architecture for future requirements
- Understand when to adopt new patterns
- Evaluate third-party tools and services
- Make technology decisions with confidence

## Learning Path Through Explanations

### **Start Here** (Foundation)
1. **[SDK Architecture](sdk-architecture.md)** - Understand the overall design
2. **[Async vs Sync Design](./async-vs-sync.md)** - Choose the right approach

### **Domain Knowledge** (Context)
3. **[Forex Trading Concepts](forex-trading-concepts.md)** - Understand the trading domain
4. **[Market Data & Streaming](./streaming.md)** - Grasp real-time data concepts

### **Advanced Architecture** (Mastery)
5. **[Error Handling Philosophy](./error-handling.md)** - Build robust systems
6. **[Configuration Patterns](./configuration.md)** - Manage complexity
7. **[Best Practices & Patterns](./best-practices.md)** - Apply proven approaches

## Complementary Resources

Explanations work best when combined with other content types:

- **After reading explanations**, try [Tutorials](../tutorials/index.md) to practice concepts
- **When implementing**, consult [How-to Guides](../how-to-guides/index.md) for specific solutions
- **During development**, reference [API Documentation](../api-reference/index.md) for specifications

## Discussion and Community

Understanding deepens through discussion:

- **[GitHub Discussions](#)** - Share insights and ask questions
- **[Issue Tracker](#)** - Report unclear explanations
- **[Wiki](https://github.com/NimbleOx/fivetwenty/wiki)** - Community-contributed explanations

---

**Ready to deepen your understanding?** Start with [SDK Architecture](sdk-architecture.md) for a comprehensive overview, or dive into any topic that interests you.