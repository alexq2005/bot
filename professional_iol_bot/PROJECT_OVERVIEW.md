# IOL Professional Trading Bot (SOTA v2.0)

**Version:** 2.0.0 (Next-Gen AI)

A state-of-the-art algorithmic trading system designed for the Argentine market (BCBA/IOL), featuring Deep Reinforcement Learning, Institutional Risk Management, and Financial NLP.

## 🚀 Key Features

### 1. Evolutionary AI Brain
*   **Deep Reinforcement Learning (DRL):** Utilizes a **PPO (Proximal Policy Optimization)** agent trained via `stable-baselines3`. The agent observes market state (RSI, MACD, Sentiment, Position) and decides the optimal action (Buy/Sell/Hold).
*   **Self-Training:** The bot includes a `train_model` loop that retrains the agent using deterministic pattern simulation (Sine Wave + Trend) to reinforce "Buy Low, Sell High" logic.

### 2. Advanced Sentiment Analysis (NLP)
*   **FinBERT Integration:** Uses `ProsusAI/finbert` (HuggingFace Transformers), a BERT model pre-trained on financial text, to analyze news headlines with professional accuracy.
*   **Multi-Source Intelligence:** Aggregates news from **NewsData.io**, **Finnhub**, **Alpha Vantage**, and **NewsAPI**.

### 3. Institutional Risk Management
*   **ATR Position Sizing:** Automatically adjusts trade quantity based on market volatility (Average True Range). High volatility = Smaller positions.
*   **Portfolio Constraints:** Enforces max allocation caps (20% per asset) to ensure diversity.

### 4. Robust Architecture
*   **Mock & Live Modes:** Fully safe testing environment (`MOCK_MODE=True`) and production-ready execution.
*   **Persistence:** SQLite database stores every trade, log, and sentiment score for auditability.
*   **Dockerized:** Ready for deployment with `docker-compose`.

## 🏗 System Architecture

*   **`src/bot.py`**: The central orchestrator that manages the lifecycle (Data -> AI -> Strategy -> Execution).
*   **`src/strategy.py` (`EvolutionaryStrategy`)**: The decision engine. It uses a **Hybrid Consensus** model:
    *   Consults the **RL Agent** for a decision.
    *   Validates with **Technical Indicators** (RSI/MACD) and **Sentiment**.
    *   Only trades when there is high conviction or a safety trigger.
*   **`src/ml_engine.py`**: Manages the PPO Agent (training, loading, predicting).
*   **`src/ai_engine.py`**: Runs the FinBERT pipeline for news analysis.
*   **`src/risk_manager.py`**: Calculates position sizes and risk limits.
*   **`src/iol_client.py`**: Handles API communication with Invertir Online (or Mocking).

## 🛠 Installation & Usage

### Prerequisites
*   Python 3.10+
*   Docker (Optional)

### Quick Start (Local)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration:**
    Create a `.env` file with your keys (or use defaults for Mock Mode):
    ```env
    IOL_USERNAME=your_user
    IOL_PASSWORD=your_pass
    MOCK_MODE=True
    TRADING_SYMBOLS=["GGAL", "YPFD"]
    ```

3.  **Run the Bot:**
    ```bash
    python -m src.bot
    ```

4.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

### Docker Deployment

```bash
docker-compose up --build
```

## ⚠️ Risk Warning

Trading involves significant financial risk. This software is provided for educational and research purposes. The "Live Mode" executes real orders with your money. Use responsibly.
