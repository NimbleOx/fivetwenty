# Tutorials - Learning-Oriented Content

## What are Tutorials?

Tutorials are lessons: each one walks you through a series of steps against a practice account, and each builds on the last. They are the right place to start if you are new to FiveTwenty or to trading APIs in general.

## When to Use Tutorials

Use tutorials when you want guided, hands-on practice rather than answers to a specific question.

**Don't use tutorials when you:**

- Need to solve a specific problem or understand concepts (use [Guides](../guides/index.md))
- Want to look up API details (use [API Reference](../api-reference/index.md))

## Learning Path

The tutorials build on each other in this order:

### **Getting Started** (New to FiveTwenty)
Start here if you're new to the FiveTwenty or trading APIs.

1. **[Installation & Setup](getting-started/installation.md)** - Set up your development environment
2. **[Authentication Basics](getting-started/authentication.md)** - Connect to OANDA safely
3. **[Your First Trade](getting-started/first-trade.md)** - Execute your first trade
4. **[Understanding Environments](../guides/understanding/environments.md)** - Practice vs Live trading

### **Guided Learning** (Building Core Skills)
Continue here once you've completed the getting started section.

1. **[Basic Trading Concepts](basic-trading/index.md)** - Learn fundamental trading operations
2. **[Advanced Order Types](advanced-orders/index.md)** - Work with OANDA's full range of order types
3. **[Risk Management Fundamentals](risk-management.md)** - Protect your capital
4. **[Account Management Basics](account-management.md)** - Monitor and analyze your trading
5. **[Working with Streaming Data](streaming-data.md)** - Handle real-time market data

### **Specialized Learning** (Advanced Topics)
Deep-dive tutorials for specific areas of trading and SDK usage.

1. **[Risk Management](risk-management.md)** - Protect your trading capital using FiveTwenty controls
2. **[Account Management](account-management.md)** - Manage multiple positions effectively
3. **[Streaming Data](streaming-data.md)** - Handle real-time market feeds
4. **[Advanced Orders](advanced-orders/index.md)** - Learn complex order types

### **Interactive Notebooks** (Hands-On Practice)
Apply your knowledge with Jupyter notebooks that combine code, explanation, and exercises.

1. **[Quick Start Guide](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/quick-start.ipynb)** - Interactive SDK introduction
2. **[Trading Strategy Development](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/trading-strategies.ipynb)** - Build your first strategy
3. **[Risk Management in Practice](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/risk-management.ipynb)** - Apply risk controls
4. **[Data Analysis Techniques](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/data-analysis.ipynb)** - Analyze market data
5. **[Real-time Data Processing](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/streaming-data.ipynb)** - Work with live feeds
6. **[Strategy Backtesting](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/backtesting.ipynb)** - Test strategies on historical data

## Tutorial Principles

A few conventions hold across all tutorials. Every example uses a practice account by default, with explicit warnings anywhere live trading comes up. Each tutorial states its prerequisites, has a clear outcome, and points out common pitfalls along the way. Where something can go wrong with real consequences, we explain how to recover.

## Getting Help

While working through tutorials:

- **Found a bug?** Check our [GitHub Issues](#)
- **Need clarification?** Visit our [Discussions](#)
- **Want more details?** See our [API Reference](../api-reference/index.md)
- **Need background knowledge?** Check our [Guides](../guides/index.md)

---

## Learning Outcomes

After completing our tutorials, you will be able to:

### Getting Started Skills
- Install and configure the FiveTwenty SDK in any Python environment
- Authenticate securely with OANDA using practice and live environments
- Execute your first trade with safety checks in place
- Understand the differences between practice and live trading

### Core Trading Skills
- Learn all major order types: market, limit, stop, and MIT orders
- Implement risk management with stop losses and take profits
- Calculate position sizes based on account risk and market conditions
- Monitor and manage positions in real-time

### Advanced Trading Skills
- Use Decimal precision for all financial calculations to avoid rounding errors
- Build complete automated trading strategies with signal generation
- Handle real-time streaming data for live market analysis
- Build portfolio analysis and performance tracking

### Production-Ready Skills
- Implement error handling and recovery
- Design live trading systems with proper safeguards
- Apply risk management across all trading operations
- Monitor and alert on trading system performance

---

Start with [Installation & Setup](getting-started/installation.md), or jump to whichever section matches your current skill level.